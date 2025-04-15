# PowerShell script to set up Azure resources and GitHub secrets for CICD pipeline
# Run this script from the repository root directory

# Parameters (customize these values)
param(
    [Parameter(Mandatory=$true)]
    [string]$ResourceGroupName,
    
    [Parameter(Mandatory=$true)]
    [string]$Location,
    
    [Parameter(Mandatory=$true)]
    [string]$AcrName,
    
    [Parameter(Mandatory=$true)]
    [string]$KeyVaultName,
    
    [Parameter(Mandatory=$true)]
    [string]$GitHubRepoName,
    
    [Parameter(Mandatory=$true)]
    [string]$GitHubOrgName,
    
    [string]$GitHubAppName = "EthicsDash-CICD-App",
    
    [Parameter(Mandatory=$false)]
    [string]$FederatedCredentialName = "ethics-dash-credential"
)

Write-Host "Starting Azure resources and GitHub secrets setup..." -ForegroundColor Green

# Login to Azure (if not already logged in)
$azLoginStatus = az account show 2>&1
if ($LASTEXITCODE -ne 0) {
    Write-Host "Logging in to Azure..." -ForegroundColor Yellow
    az login
} else {
    Write-Host "Already logged into Azure" -ForegroundColor Green
}

# Login to GitHub CLI (if not already logged in)
$ghStatus = gh auth status 2>&1
if ($LASTEXITCODE -ne 0) {
    Write-Host "Logging in to GitHub CLI..." -ForegroundColor Yellow
    gh auth login
} else {
    Write-Host "Already logged into GitHub CLI" -ForegroundColor Green
}

# Create or use existing resource group
Write-Host "Creating/confirming resource group: $ResourceGroupName" -ForegroundColor Yellow
$resourceGroupExists = az group exists --name $ResourceGroupName
if ($resourceGroupExists -eq "false") {
    az group create --name $ResourceGroupName --location $Location
    Write-Host "Resource group created: $ResourceGroupName" -ForegroundColor Green
} else {
    Write-Host "Using existing resource group: $ResourceGroupName" -ForegroundColor Green
}

# Create Azure Container Registry (ACR)
Write-Host "Creating Azure Container Registry: $AcrName" -ForegroundColor Yellow
$acrExists = az acr show --name $AcrName --resource-group $ResourceGroupName 2>&1
if ($LASTEXITCODE -ne 0) {
    az acr create --resource-group $ResourceGroupName --name $AcrName --sku Basic
    Write-Host "Azure Container Registry created: $AcrName" -ForegroundColor Green
} else {
    Write-Host "Using existing Azure Container Registry: $AcrName" -ForegroundColor Green
}

# Create or get ACR credentials
$acrUsername = az acr credential show --name $AcrName --resource-group $ResourceGroupName --query username -o tsv
$acrPassword = az acr credential show --name $AcrName --resource-group $ResourceGroupName --query "passwords[0].value" -o tsv
$acrLoginServer = "$AcrName.azurecr.io"

# Create Azure Key Vault
Write-Host "Creating Azure Key Vault: $KeyVaultName" -ForegroundColor Yellow
$keyVaultExists = az keyvault show --name $KeyVaultName --resource-group $ResourceGroupName 2>&1
if ($LASTEXITCODE -ne 0) {
    az keyvault create --resource-group $ResourceGroupName --name $KeyVaultName --location $Location --enable-rbac-authorization false
    Write-Host "Azure Key Vault created: $KeyVaultName" -ForegroundColor Green
} else {
    Write-Host "Using existing Azure Key Vault: $KeyVaultName" -ForegroundColor Green
}

# Create Azure AD application for GitHub Actions
Write-Host "Creating Azure AD application for GitHub Actions" -ForegroundColor Yellow
$appOutput = az ad app create --display-name $GitHubAppName | ConvertFrom-Json
$appId = $appOutput.appId
$objectId = $appOutput.id

Write-Host "Creating Service Principal for the application" -ForegroundColor Yellow
az ad sp create --id $appId

# Get Azure subscription ID
$subscriptionId = az account show --query id -o tsv

# Set up Federated Credentials for GitHub OIDC
Write-Host "Setting up Federated Credentials for GitHub OIDC" -ForegroundColor Yellow
$fedCredentialPath = "federated-credential.json"

@"
{
    "name": "$FederatedCredentialName",
    "issuer": "https://token.actions.githubusercontent.com",
    "subject": "repo:$GitHubOrgName/$GitHubRepoName:ref:refs/heads/main",
    "description": "Federated identity credential for GitHub Actions",
    "audiences": ["api://AzureADTokenExchange"]
}
"@ | Out-File -FilePath $fedCredentialPath -Encoding utf8

az ad app federated-credential create --id $objectId --parameters $fedCredentialPath
Write-Host "Federated Credentials created successfully" -ForegroundColor Green

# Assign roles to the service principal
Write-Host "Assigning roles to the service principal" -ForegroundColor Yellow
$spId = az ad sp show --id $appId --query id -o tsv

# Assign AcrPush role for pushing to ACR
az role assignment create --assignee $spId --scope "/subscriptions/$subscriptionId/resourceGroups/$ResourceGroupName/providers/Microsoft.ContainerRegistry/registries/$AcrName" --role "AcrPush"

# Assign Key Vault Secrets User role for accessing secrets
az role assignment create --assignee $spId --scope "/subscriptions/$subscriptionId/resourceGroups/$ResourceGroupName/providers/Microsoft.KeyVault/vaults/$KeyVaultName" --role "Key Vault Secrets User"

# Store sample secrets in Key Vault (placeholder values)
Write-Host "Storing sample secrets in Key Vault" -ForegroundColor Yellow
az keyvault secret set --vault-name $KeyVaultName --name "API-KEY" --value "sample-api-key-replace-with-real-value"
az keyvault secret set --vault-name $KeyVaultName --name "API-SECRET" --value "sample-api-secret-replace-with-real-value"
az keyvault secret set --vault-name $KeyVaultName --name "API-ENDPOINT" --value "https://api.example.com/v1"
az keyvault secret set --vault-name $KeyVaultName --name "API-VERSION" --value "v1"
az keyvault secret set --vault-name $KeyVaultName --name "NODE-ENV" --value "production"
az keyvault secret set --vault-name $KeyVaultName --name "LOG-LEVEL" --value "info"

# Set up GitHub secrets
Write-Host "Setting up GitHub secrets" -ForegroundColor Yellow

# Set Azure-related secrets
gh secret set AZURE_CLIENT_ID --body $appId
gh secret set AZURE_TENANT_ID --body $(az account show --query tenantId -o tsv)
gh secret set AZURE_SUBSCRIPTION_ID --body $subscriptionId

# Set ACR-related secrets
gh secret set ACR_REGISTRY_NAME --body $AcrName

# Set Key Vault-related secrets
gh secret set KEY_VAULT_NAME --body $KeyVaultName

Write-Host "Setup complete!" -ForegroundColor Green
Write-Host "Next steps:" -ForegroundColor Yellow
Write-Host "1. Commit and push the GitHub workflow file (.github/workflows/azure-cicd-pipeline.yml)" -ForegroundColor Yellow
Write-Host "2. Update the secrets in Key Vault with actual values" -ForegroundColor Yellow
Write-Host "3. Test the workflow by manually triggering it from GitHub Actions tab" -ForegroundColor Yellow 