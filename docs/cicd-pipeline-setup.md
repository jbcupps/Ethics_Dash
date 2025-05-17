# Ethics Dashboard CICD Pipeline Setup Guide

This guide will walk you through setting up the CI/CD pipeline for the Ethics Dashboard project.

## Overview

The CI/CD pipeline follows this flow:
1. Local Docker development
2. GitHub commit
3. GitHub Actions workflow
4. Azure Container Registry (ACR)
5. Application build with secrets from Azure Key Vault

## Prerequisites

- Azure subscription
- GitHub repository with write access
- Azure CLI installed
- GitHub CLI installed
- PowerShell 5.1 or later

## Step-by-Step Setup

### 1. Clone the Repository

```powershell
git clone https://github.com/your-org/Ethics_Dash.git
cd Ethics_Dash
```

### 2. Ensure Required CLIs are Installed

```powershell
# Check Azure CLI installation
az --version

# Check GitHub CLI installation
gh --version

# Login to Azure CLI
az login

# Login to GitHub CLI
gh auth login
```

### 3. Create Required Azure Resources

You can use the provided PowerShell script to create all required Azure resources:

```powershell
# Make sure scripts directory exists
mkdir -p scripts

# Run the setup script
.\scripts\setup-azure-pipeline.ps1 `
  -ResourceGroupName "ethics-dash-rg" `
  -Location "eastus" `
  -AcrName "ethicsdashacr" `
  -KeyVaultName "ethics-dash-kv" `
  -GitHubRepoName "Ethics_Dash" `
  -GitHubOrgName "YourGitHubOrg"
```

### 4. Verify GitHub Secrets

Verify that the script has created the necessary GitHub secrets:

```powershell
gh secret list
```

The following secrets should be set:
- AZURE_CLIENT_ID
- AZURE_TENANT_ID
- AZURE_SUBSCRIPTION_ID
- ACR_REGISTRY_NAME
- KEY_VAULT_NAME

### 5. Update Key Vault Secrets

Replace the placeholder secrets in Key Vault with your actual values:

```powershell
# Example: Update API key
az keyvault secret set --vault-name "ethics-dash-kv" --name "API-KEY" --value "your-actual-api-key"

# Example: Update API secret
az keyvault secret set --vault-name "ethics-dash-kv" --name "API-SECRET" --value "your-actual-api-secret"

# Update other secrets as needed
az keyvault secret set --vault-name "ethics-dash-kv" --name "API-ENDPOINT" --value "https://your-actual-api-endpoint.com"
az keyvault secret set --vault-name "ethics-dash-kv" --name "API-VERSION" --value "v2"
az keyvault secret set --vault-name "ethics-dash-kv" --name "NODE-ENV" --value "production"
az keyvault secret set --vault-name "ethics-dash-kv" --name "LOG-LEVEL" --value "info"
```

### 6. Commit and Push the Workflow File

```powershell
git add .github/workflows/deploy-to-azure.yml
git commit -m "Add GitHub Actions workflow for CICD pipeline"
git push origin main
```

### 7. Trigger the Workflow

You can trigger the workflow manually from the GitHub Actions tab in your repository.

1. Go to your GitHub repository
2. Click on the "Actions" tab
3. Select the "Azure CICD Pipeline" workflow
4. Click "Run workflow"
5. Select the main branch and click "Run workflow"

## Troubleshooting

### Common Issues

1. **Authentication failures:**
   - Check that the federated credential is properly set up
   - Verify GitHub secrets are correctly configured

   ```powershell
   # Check service principal
   az ad sp show --id $AZURE_CLIENT_ID
   
   # Check role assignments
   az role assignment list --assignee $AZURE_CLIENT_ID
   ```

2. **ACR push failures:**
   - Verify the service principal has AcrPush role

   ```powershell
   # Reassign AcrPush role if needed
   az role assignment create --assignee $AZURE_CLIENT_ID --scope "/subscriptions/$AZURE_SUBSCRIPTION_ID/resourceGroups/ethics-dash-rg/providers/Microsoft.ContainerRegistry/registries/ethicsdashacr" --role "AcrPush"
   ```

3. **Key Vault access issues:**
   - Check Key Vault access policies or RBAC permissions

   ```powershell
   # Reassign Key Vault Secrets User role if needed
   az role assignment create --assignee $AZURE_CLIENT_ID --scope "/subscriptions/$AZURE_SUBSCRIPTION_ID/resourceGroups/ethics-dash-rg/providers/Microsoft.KeyVault/vaults/ethics-dash-kv" --role "Key Vault Secrets User"
   ```

## Testing the Pipeline

To test the pipeline, make a small change to a file in the repository, commit, and push:

```powershell
# Edit a file
echo "# Test change" >> README.md

# Commit and push
git add README.md
git commit -m "Test CI/CD pipeline"
git push origin main
```

Then check the GitHub Actions tab to see if the workflow runs successfully.

## Local Development

For local development, you can use docker-compose:

```powershell
# Build and run locally
docker-compose build
docker-compose up -d
```

Test your changes locally before pushing to GitHub to trigger the CI/CD pipeline.

## Additional Resources

- [GitHub Actions Documentation](https://docs.github.com/en/actions)
- [Azure Container Registry Documentation](https://docs.microsoft.com/en-us/azure/container-registry/)
- [Azure Key Vault Documentation](https://docs.microsoft.com/en-us/azure/key-vault/)
- [GitHub OIDC with Azure](https://docs.github.com/en/actions/deployment/security-hardening-your-deployments/configuring-openid-connect-in-azure) 