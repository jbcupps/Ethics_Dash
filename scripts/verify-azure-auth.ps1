# PowerShell script to verify and update Azure authentication for GitHub Actions
# Run this script from the repository root directory

param(
    [Parameter(Mandatory=$false)]
    [string]$ResourceGroupName = "",
    
    [Parameter(Mandatory=$false)]
    [string]$Location = "eastus",
    
    [Parameter(Mandatory=$false)]
    [string]$AcrName = "",
    
    [Parameter(Mandatory=$false)]
    [string]$KeyVaultName = "",
    
    [Parameter(Mandatory=$true)]
    [string]$GitHubRepoName,
    
    [Parameter(Mandatory=$true)]
    [string]$GitHubOrgName,
    
    [Parameter(Mandatory=$false)]
    [string]$ProjectPrefix = "",
    
    [Parameter(Mandatory=$false)]
    [switch]$ForceRecreate = $false
)

function Handle-Error {
    param([string]$Message, [string]$ErrorDetails, [bool]$Fatal = $false)
    
    Write-Host "ERROR: $Message" -ForegroundColor Red
    if ($ErrorDetails) {
        Write-Host "  Details: $ErrorDetails" -ForegroundColor Red
    }
    
    if ($Fatal) {
        Write-Host "Fatal error. Exiting script." -ForegroundColor Red
        exit 1
    }
}

# Derive project prefix if not provided
if (-not $ProjectPrefix) {
    $ProjectPrefix = ($GitHubRepoName -replace '[^a-zA-Z0-9]', '').ToLower()
    Write-Host "Using derived project prefix: $ProjectPrefix" -ForegroundColor Yellow
}

# Auto-generate resource names if not provided
if (-not $ResourceGroupName) {
    $ResourceGroupName = "$ProjectPrefix-rg"
    Write-Host "Using generated Resource Group name: $ResourceGroupName" -ForegroundColor Yellow
}

if (-not $AcrName) {
    # ACR names must be alphanumeric only, 5-50 chars
    $AcrName = "$($ProjectPrefix -replace '[^a-zA-Z0-9]', '')acr"
    Write-Host "Using generated ACR name: $AcrName" -ForegroundColor Yellow
}

if (-not $KeyVaultName) {
    # Key Vault names must be 3-24 alphanumeric chars including hyphens
    $KeyVaultName = "$($ProjectPrefix -replace '[^a-zA-Z0-9\-]', '')kv"
    Write-Host "Using generated Key Vault name: $KeyVaultName" -ForegroundColor Yellow
}

Write-Host "Starting Azure Authentication setup for GitHub Actions..." -ForegroundColor Green
Write-Host "Resource Group: $ResourceGroupName" -ForegroundColor Cyan
Write-Host "ACR: $AcrName" -ForegroundColor Cyan
Write-Host "Key Vault: $KeyVaultName" -ForegroundColor Cyan
Write-Host "GitHub Org/Repo: $GitHubOrgName/$GitHubRepoName" -ForegroundColor Cyan

# Login to Azure and handle errors
try {
    Write-Host "Checking Azure CLI login status..." -ForegroundColor Yellow
    # Use 'az account show' which is less likely to trigger extension issues than complex commands immediately after login
    az account show --output none 2>$null
    if ($LASTEXITCODE -ne 0) {
        Write-Host "Logging in to Azure..." -ForegroundColor Yellow
        # Use --only-show-errors to minimize output noise on success
        az login --only-show-errors
        if ($LASTEXITCODE -ne 0) {
            Handle-Error "Failed to log in to Azure" "Check Azure CLI installation and credentials" $true
        }
        Write-Host "Azure login successful." -ForegroundColor Green
    } else {
        Write-Host "Already logged into Azure" -ForegroundColor Green
    }
} catch {
    Handle-Error "Error during Azure login check/process" $_.Exception.Message $true
}

# Explicitly list and select Azure subscription
try {
    Write-Host "Fetching available Azure subscriptions..." -ForegroundColor Yellow
    $subscriptions = az account list --output json | ConvertFrom-Json
    
    if (-not $subscriptions) {
        Handle-Error "Could not retrieve subscription list." "Check Azure connection and permissions." $true
    }
    
    if ($subscriptions.Count -eq 0) {
        Handle-Error "No Azure subscriptions found for this account." "Please check your Azure account." $true
    } elseif ($subscriptions.Count -eq 1) {
        $selectedSub = $subscriptions[0]
        Write-Host "Only one subscription found:" -ForegroundColor Green
        Write-Host "- $($selectedSub.name) ($($selectedSub.id))" -ForegroundColor Green
        $subscriptionId = $selectedSub.id
    } else {
        Write-Host "Multiple Azure subscriptions found. Please select one:" -ForegroundColor Yellow
        for ($i = 0; $i -lt $subscriptions.Count; $i++) {
            Write-Host "[$($i+1)] $($subscriptions[$i].name) ($($subscriptions[$i].id))"
        }
        
        $choice = Read-Host "Enter the number of the subscription to use"
        $index = $choice -as [int]
        
        if ($null -eq $index -or $index -lt 1 -or $index -gt $subscriptions.Count) {
            Handle-Error "Invalid selection." "Please run the script again and enter a valid number." $true
        }
        
        $selectedSub = $subscriptions[$index-1]
        $subscriptionId = $selectedSub.id
        Write-Host "Using subscription: $($selectedSub.name) ($($selectedSub.id))" -ForegroundColor Green
    }
    
    # Set the selected subscription as active for subsequent commands
    Write-Host "Setting active subscription to $subscriptionId..." -ForegroundColor Yellow
    az account set --subscription $subscriptionId --only-show-errors
    if ($LASTEXITCODE -ne 0) {
        Handle-Error "Failed to set active subscription." "Check permissions for the selected subscription." $true
    }
    Write-Host "Active subscription set successfully." -ForegroundColor Green

} catch {
    Handle-Error "Error during subscription selection" $_.Exception.Message $true
}

# Get subscription details (NOW using the explicitly set subscription)
try {
    # Re-fetch account details for the explicitly set subscription
    $accountDetails = az account show --output json | ConvertFrom-Json
    $subscriptionId = $accountDetails.id
    $tenantId = $accountDetails.tenantId
    
    if (-not $subscriptionId -or -not $tenantId) {
        # This should be less likely now, but keep as a safeguard
        Handle-Error "Failed to retrieve subscription or tenant ID after setting subscription." "Check Azure connection and permissions for subscription $subscriptionId." $true
    }
    
    Write-Host "Using Azure Subscription ID: $subscriptionId" -ForegroundColor Yellow
    Write-Host "Using Azure Tenant ID: $tenantId" -ForegroundColor Yellow
} catch {
    Handle-Error "Error getting details for the selected subscription" $_.Exception.Message $true
}

# Create or verify resource group exists
try {
    Write-Host "Checking if resource group '$ResourceGroupName' exists..." -ForegroundColor Yellow
    $rgExists = az group exists --name $ResourceGroupName
    
    if ($rgExists -eq "false") {
        Write-Host "Creating resource group '$ResourceGroupName' in location '$Location'..." -ForegroundColor Yellow
        az group create --name $ResourceGroupName --location $Location --output none
        if ($LASTEXITCODE -ne 0) {
            Handle-Error "Failed to create resource group" "Check permissions and resource name validity" $true
        }
        Write-Host "Resource group created successfully" -ForegroundColor Green
    } else {
        Write-Host "Resource group '$ResourceGroupName' already exists" -ForegroundColor Green
    }
} catch {
    Handle-Error "Error creating/verifying resource group" $_.Exception.Message $true
}

# Create or verify ACR exists
try {
    Write-Host "Checking if Azure Container Registry '$AcrName' exists..." -ForegroundColor Yellow
    # Attempt to show the ACR. If it exists, $LASTEXITCODE will be 0.
    az acr show --name $AcrName --resource-group $ResourceGroupName --output none 2>$null
    
    if ($LASTEXITCODE -ne 0) {
        Write-Host "Azure Container Registry '$AcrName' not found. Creating..." -ForegroundColor Yellow
        az acr create --resource-group $ResourceGroupName --name $AcrName --sku Basic --admin-enabled false --output none
        if ($LASTEXITCODE -ne 0) {
            # If creation fails after checking, it's likely a real issue (permissions, name conflict, etc.)
            Handle-Error "Failed to create ACR '$AcrName'" "Check permissions and ACR name availability/uniqueness" $true
        }
        Write-Host "Azure Container Registry created successfully" -ForegroundColor Green
    } else {
        Write-Host "Azure Container Registry '$AcrName' already exists. Using existing." -ForegroundColor Green
    }
} catch {
    # Catch errors during the 'az acr show' or 'az acr create' calls
    Handle-Error "Error creating/verifying ACR" $_.Exception.Message $true
}

# Create or verify Key Vault exists
try {
    Write-Host "Checking if Key Vault '$KeyVaultName' exists..." -ForegroundColor Yellow
    # Attempt to show the Key Vault. If it exists, $LASTEXITCODE will be 0.
    az keyvault show --name $KeyVaultName --resource-group $ResourceGroupName --output none 2>$null
    
    if ($LASTEXITCODE -ne 0) {
        Write-Host "Key Vault '$KeyVaultName' not found. Creating..." -ForegroundColor Yellow
        az keyvault create --resource-group $ResourceGroupName --name $KeyVaultName --location $Location --output none
        if ($LASTEXITCODE -ne 0) {
             # If creation fails after checking, it's likely a real issue
            Handle-Error "Failed to create Key Vault '$KeyVaultName'" "Check permissions and Key Vault name availability/uniqueness" $true
        }
        Write-Host "Key Vault created successfully" -ForegroundColor Green
    } else {
        Write-Host "Key Vault '$KeyVaultName' already exists. Using existing." -ForegroundColor Green
    }
} catch {
    # Catch errors during the 'az keyvault show' or 'az keyvault create' calls
    Handle-Error "Error creating/verifying Key Vault" $_.Exception.Message $true
}

# Check GitHub CLI availability and login
try {
    Write-Host "Checking GitHub CLI login status..." -ForegroundColor Yellow
    $ghCliVersion = gh --version 2>&1
    
    if ($LASTEXITCODE -ne 0) {
        Handle-Error "GitHub CLI (gh) not installed or not in PATH" "Please install GitHub CLI: https://cli.github.com/" $true
    }
    
    $ghStatus = gh auth status 2>&1
    if ($LASTEXITCODE -ne 0) {
        Write-Host "Logging in to GitHub CLI..." -ForegroundColor Yellow
        gh auth login
        if ($LASTEXITCODE -ne 0) {
            Handle-Error "Failed to log in to GitHub CLI" "Check GitHub credentials" $true
        }
    } else {
        Write-Host "Already logged into GitHub CLI" -ForegroundColor Green
    }
} catch {
    Handle-Error "Error with GitHub CLI" $_.Exception.Message $true
}

# Create or find Azure AD application for OIDC
try {
    $appName = "$ProjectPrefix-cicd-app"
    Write-Host "Looking for existing Azure AD application '$appName'..." -ForegroundColor Yellow
    
    $existingApps = az ad app list --display-name $appName --query "[].{appId:appId, objectId:id}" | ConvertFrom-Json
    
    if (-not $existingApps -or $existingApps.Count -eq 0 -or $ForceRecreate) {
        if ($ForceRecreate -and $existingApps.Count -gt 0) {
            Write-Host "Deleting existing Azure AD application..." -ForegroundColor Yellow
            az ad app delete --id $existingApps[0].appId --output none
        }
        
        Write-Host "Creating new Azure AD application '$appName'..." -ForegroundColor Yellow
        $app = az ad app create --display-name $appName | ConvertFrom-Json
        $appId = $app.appId
        $objectId = $app.id
        
        Write-Host "Creating Service Principal for the application..." -ForegroundColor Yellow
        az ad sp create --id $appId --output none
        if ($LASTEXITCODE -ne 0) {
            Handle-Error "Failed to create Service Principal" "Check AD permissions" $true
        }
    } else {
        Write-Host "Found existing Azure AD application '$appName'" -ForegroundColor Green
        $appId = $existingApps[0].appId
        $objectId = $existingApps[0].objectId
    }
    
    Write-Host "App ID: $appId" -ForegroundColor Yellow
    Write-Host "Object ID: $objectId" -ForegroundColor Yellow
} catch {
    Handle-Error "Error creating/finding Azure AD application" $_.Exception.Message $true
}

# Verify and update Service Principal
try {
    Write-Host "Verifying Service Principal..." -ForegroundColor Yellow
    $spId = az ad sp show --id $appId --query id -o tsv
    
    if (-not $spId) {
        Write-Host "Service Principal not found. Creating..." -ForegroundColor Yellow
        az ad sp create --id $appId --output none
        $spId = az ad sp show --id $appId --query id -o tsv
        
        if (-not $spId) {
            Handle-Error "Failed to create or retrieve Service Principal" "Check AD permissions" $true
        }
    }
    
    Write-Host "Service Principal ID: $spId" -ForegroundColor Yellow
} catch {
    Handle-Error "Error verifying Service Principal" $_.Exception.Message $true
}

# Configure federated credentials for GitHub OIDC
try {
    Write-Host "Configuring federated credentials for GitHub OIDC..." -ForegroundColor Yellow
    
    $fedCredentials = az ad app federated-credential list --id $objectId | ConvertFrom-Json
    $repoIdentifier = "repo:$GitHubOrgName/$GitHubRepoName"
    
    $mainBranchCredential = $fedCredentials | Where-Object { $_.subject -like "*$repoIdentifier:ref:refs/heads/main*" }
    if (-not $mainBranchCredential) {
        Write-Host "Creating federated credential for main branch..." -ForegroundColor Yellow
        $mainCredName = "$ProjectPrefix-main-credential"
        $mainCredPath = "main-credential.json"
        
        @"
{
    "name": "$mainCredName",
    "issuer": "https://token.actions.githubusercontent.com",
    "subject": "repo:$GitHubOrgName/$GitHubRepoName:ref:refs/heads/main",
    "description": "Federated identity credential for GitHub Actions - main branch",
    "audiences": ["api://AzureADTokenExchange"]
}
"@ | Out-File -FilePath $mainCredPath -Encoding utf8
        
        az ad app federated-credential create --id $objectId --parameters $mainCredPath --output none
        Remove-Item $mainCredPath
    } else {
        Write-Host "Main branch federated credential already exists" -ForegroundColor Green
    }
    
    $prCredential = $fedCredentials | Where-Object { $_.subject -like "*$repoIdentifier:pull_request*" }
    if (-not $prCredential) {
        Write-Host "Creating federated credential for pull requests..." -ForegroundColor Yellow
        $prCredName = "$ProjectPrefix-pr-credential"
        $prCredPath = "pr-credential.json"
        
        @"
{
    "name": "$prCredName",
    "issuer": "https://token.actions.githubusercontent.com",
    "subject": "repo:$GitHubOrgName/$GitHubRepoName:pull_request",
    "description": "Federated identity credential for GitHub Actions - pull requests",
    "audiences": ["api://AzureADTokenExchange"]
}
"@ | Out-File -FilePath $prCredPath -Encoding utf8
        
        az ad app federated-credential create --id $objectId --parameters $prCredPath --output none
        Remove-Item $prCredPath
    } else {
        Write-Host "Pull request federated credential already exists" -ForegroundColor Green
    }
} catch {
    Handle-Error "Error configuring federated credentials" $_.Exception.Message
}

# Assign roles to the service principal
try {
    Write-Host "Assigning roles to the service principal..." -ForegroundColor Yellow
    
    # Get ACR resource ID
    $acrResourceId = az acr show --name $AcrName --resource-group $ResourceGroupName --query id -o tsv
    if (-not $acrResourceId) {
        Handle-Error "Failed to get ACR resource ID" "Check if ACR exists and you have permissions to access it" $true
    }
    
    # Check ACR role assignment
    $acrRoleAssignment = az role assignment list --assignee $spId --scope $acrResourceId --role "AcrPush" --query "[0].id" -o tsv
    
    if (-not $acrRoleAssignment) {
        Write-Host "Assigning AcrPush role for ACR..." -ForegroundColor Yellow
        az role assignment create --assignee $spId --scope $acrResourceId --role "AcrPush" --output none
        if ($LASTEXITCODE -ne 0) {
            Handle-Error "Failed to assign AcrPush role" "Check permissions and role name" $false
        } else {
            Write-Host "AcrPush role assigned successfully" -ForegroundColor Green
        }
    } else {
        Write-Host "AcrPush role already assigned" -ForegroundColor Green
    }
    
    # Get Key Vault resource ID
    $kvResourceId = az keyvault show --name $KeyVaultName --resource-group $ResourceGroupName --query id -o tsv
    if (-not $kvResourceId) {
        Handle-Error "Failed to get Key Vault resource ID" "Check if Key Vault exists and you have permissions to access it" $true
    }
    
    # Check Key Vault role assignment
    $kvRoleAssignment = az role assignment list --assignee $spId --scope $kvResourceId --role "Key Vault Secrets User" --query "[0].id" -o tsv
    
    if (-not $kvRoleAssignment) {
        Write-Host "Assigning Key Vault Secrets User role..." -ForegroundColor Yellow
        az role assignment create --assignee $spId --scope $kvResourceId --role "Key Vault Secrets User" --output none
        if ($LASTEXITCODE -ne 0) {
            Handle-Error "Failed to assign Key Vault Secrets User role" "Check permissions and role name" $false
        } else {
            Write-Host "Key Vault Secrets User role assigned successfully" -ForegroundColor Green
        }
    } else {
        Write-Host "Key Vault Secrets User role already assigned" -ForegroundColor Green
    }
} catch {
    Handle-Error "Error assigning roles" $_.Exception.Message
}

# Update GitHub secrets
try {
    Write-Host "Updating GitHub repository secrets..." -ForegroundColor Yellow
    
    # Set Azure-related secrets
    gh secret set AZURE_CLIENT_ID --body "$appId"
    if ($LASTEXITCODE -ne 0) {
        Handle-Error "Failed to set AZURE_CLIENT_ID secret" "Check GitHub CLI permissions" $false
    }
    
    gh secret set AZURE_TENANT_ID --body "$tenantId"
    if ($LASTEXITCODE -ne 0) {
        Handle-Error "Failed to set AZURE_TENANT_ID secret" "Check GitHub CLI permissions" $false
    }
    
    gh secret set AZURE_SUBSCRIPTION_ID --body "$subscriptionId"
    if ($LASTEXITCODE -ne 0) {
        Handle-Error "Failed to set AZURE_SUBSCRIPTION_ID secret" "Check GitHub CLI permissions" $false
    }
    
    # Set resource-related secrets
    gh secret set ACR_REGISTRY_NAME --body "$AcrName"
    if ($LASTEXITCODE -ne 0) {
        Handle-Error "Failed to set ACR_REGISTRY_NAME secret" "Check GitHub CLI permissions" $false
    }
    
    gh secret set KEY_VAULT_NAME --body "$KeyVaultName"
    if ($LASTEXITCODE -ne 0) {
        Handle-Error "Failed to set KEY_VAULT_NAME secret" "Check GitHub CLI permissions" $false
    }
    
    # Add resource group name for potential future use
    gh secret set RESOURCE_GROUP_NAME --body "$ResourceGroupName"
    if ($LASTEXITCODE -ne 0) {
        Handle-Error "Failed to set RESOURCE_GROUP_NAME secret" "Check GitHub CLI permissions" $false
    }
    
    Write-Host "GitHub secret verification complete!" -ForegroundColor Green
    Write-Host "Verified/updated the following GitHub secrets:" -ForegroundColor Green
    Write-Host "- AZURE_CLIENT_ID" -ForegroundColor Green
    Write-Host "- AZURE_TENANT_ID" -ForegroundColor Green
    Write-Host "- AZURE_SUBSCRIPTION_ID" -ForegroundColor Green
    Write-Host "- ACR_REGISTRY_NAME" -ForegroundColor Green
    Write-Host "- KEY_VAULT_NAME" -ForegroundColor Green
    Write-Host "- RESOURCE_GROUP_NAME" -ForegroundColor Green
} catch {
    Handle-Error "Error updating GitHub secrets" $_.Exception.Message
}

Write-Host "`n==== SETUP SUMMARY ====" -ForegroundColor Cyan
Write-Host "Resource Group: $ResourceGroupName" -ForegroundColor Cyan
Write-Host "ACR: $AcrName" -ForegroundColor Cyan
Write-Host "Key Vault: $KeyVaultName" -ForegroundColor Cyan
Write-Host "GitHub Org/Repo: $GitHubOrgName/$GitHubRepoName" -ForegroundColor Cyan
Write-Host "Azure AD App: $appName (ID: $appId)" -ForegroundColor Cyan
Write-Host "=========================" -ForegroundColor Cyan

Write-Host "`nTo test the authentication, trigger the GitHub Actions workflow manually:" -ForegroundColor Yellow
Write-Host "1. Go to your GitHub repository" -ForegroundColor Yellow
Write-Host "2. Click on the 'Actions' tab" -ForegroundColor Yellow
Write-Host "3. Select the 'Azure CICD Pipeline' workflow" -ForegroundColor Yellow
Write-Host "4. Click 'Run workflow'" -ForegroundColor Yellow 