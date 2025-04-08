# Check if GitHub CLI is installed
if (-not (Get-Command gh -ErrorAction SilentlyContinue)) {
    Write-Host "GitHub CLI is not installed. Please install it first: https://cli.github.com/" -ForegroundColor Red
    exit 1
}

# Check if user is logged in to GitHub
try {
    gh auth status 2>&1 > $null # Execute command, discard output, check $LASTEXITCODE below
    if ($LASTEXITCODE -ne 0) {
        Write-Host "Please login to GitHub first using: gh auth login" -ForegroundColor Yellow
        exit 1
    }
} catch {
    Write-Host "Please login to GitHub first using: gh auth login" -ForegroundColor Yellow
    exit 1
}

# Get repository name
try {
    $repoName = (git rev-parse --show-toplevel | Split-Path -Leaf)
} catch {
    Write-Host "Error: Not a git repository or git is not installed" -ForegroundColor Red
    exit 1
}

# Function to securely set a secret
function Set-GitHubSecret {
    param (
        [string]$SecretName,
        [string]$PromptMessage,
        [string]$DefaultValue = $null
    )

    if ($DefaultValue) {
        $secretValue = Read-Host "$PromptMessage [Press Enter to use default: $DefaultValue]"
        $secretValue = if ([string]::IsNullOrWhiteSpace($secretValue)) { $DefaultValue } else { $secretValue }
    } else {
        $secretValue = Read-Host "$PromptMessage"
    }

    # Check if secret value is empty
    if ([string]::IsNullOrWhiteSpace($secretValue)) {
        Write-Host "Warning: Empty value provided for ${SecretName}" -ForegroundColor Yellow
    }

    # Set the secret
    try {
        $result = gh secret set "$SecretName" -R "$repoName" -b "$secretValue" 2>&1
        if ($LASTEXITCODE -eq 0) {
            Write-Host "Successfully set ${SecretName}" -ForegroundColor Green
        } else {
            Write-Host "Failed to set ${SecretName}: ${result}" -ForegroundColor Red
        }
    } catch {
        Write-Host "Error setting ${SecretName}: ${_}" -ForegroundColor Red
    }
}

Write-Host "Setting up GitHub secrets for ${repoName}..." -ForegroundColor Cyan

# Set ACR secrets
Write-Host "`nSetting up ACR secrets:" -ForegroundColor Cyan
Set-GitHubSecret -SecretName "ACR_REGISTRY" -PromptMessage "Enter your Azure Container Registry URL (e.g., yourregistry.azurecr.io)"
Set-GitHubSecret -SecretName "ACR_USERNAME" -PromptMessage "Enter your ACR username"
Set-GitHubSecret -SecretName "ACR_PASSWORD" -PromptMessage "Enter your ACR password"

# Set API secrets
Write-Host "`nSetting up API secrets (you can leave these empty for now and update them later):" -ForegroundColor Cyan
Set-GitHubSecret -SecretName "API_KEY" -PromptMessage "Enter your API key" -DefaultValue "placeholder"
Set-GitHubSecret -SecretName "API_SECRET" -PromptMessage "Enter your API secret" -DefaultValue "placeholder"
Set-GitHubSecret -SecretName "API_ENDPOINT" -PromptMessage "Enter your API endpoint URL" -DefaultValue "https://api.example.com"
Set-GitHubSecret -SecretName "API_VERSION" -PromptMessage "Enter your API version" -DefaultValue "v1"

# Set environment-specific secrets
Write-Host "`nSetting up environment-specific secrets:" -ForegroundColor Cyan
Set-GitHubSecret -SecretName "NODE_ENV" -PromptMessage "Enter the environment (development/production)" -DefaultValue "development"
Set-GitHubSecret -SecretName "LOG_LEVEL" -PromptMessage "Enter the log level (debug/info/warn/error)" -DefaultValue "info"

Write-Host "`nGitHub secrets setup completed!" -ForegroundColor Green
Write-Host "You can verify the secrets in your repository settings under 'Secrets and variables' -> 'Actions'" -ForegroundColor Yellow
Write-Host "Note: You can update these secrets later using the GitHub CLI or web interface" -ForegroundColor Yellow 