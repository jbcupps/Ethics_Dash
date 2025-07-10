# Setup Azure MongoDB Persistence
# This script creates the necessary Azure resources for MongoDB persistence
# Run this script with administrator privileges in PowerShell

# Configuration Variables - Update these as needed
$ResourceGroupName = "ethicsdash-rg"
$Location = "eastus"  # Azure region
$StorageAccountName = "ethicsdashstorage"  # Must be globally unique
$FileShareName = "ethicsdash-mongo-data"
$OutputEnvFile = ".env.azure"

# Login to Azure
Write-Host "Logging in to Azure..." -ForegroundColor Green
az login

# Check if resource group exists, create if not
$rgExists = az group exists --name $ResourceGroupName
if ($rgExists -eq "false") {
    Write-Host "Creating resource group $ResourceGroupName..." -ForegroundColor Yellow
    az group create --name $ResourceGroupName --location $Location
} else {
    Write-Host "Resource group $ResourceGroupName already exists." -ForegroundColor Cyan
}

# Create storage account if it doesn't exist
$storageExists = az storage account check-name --name $StorageAccountName --query "nameAvailable" -o tsv
if ($storageExists -eq "true") {
    Write-Host "Creating storage account $StorageAccountName..." -ForegroundColor Yellow
    az storage account create `
        --name $StorageAccountName `
        --resource-group $ResourceGroupName `
        --location $Location `
        --sku Standard_LRS `
        --kind StorageV2 `
        --enable-large-file-share
} else {
    Write-Host "Storage account with name $StorageAccountName already exists or name is invalid." -ForegroundColor Cyan
}

# Get storage account key
Write-Host "Retrieving storage account key..." -ForegroundColor Green
$StorageKey = az storage account keys list `
    --resource-group $ResourceGroupName `
    --account-name $StorageAccountName `
    --query "[0].value" -o tsv

# Create file share if it doesn't exist
Write-Host "Creating file share $FileShareName..." -ForegroundColor Yellow
$shareExists = az storage share exists `
    --name $FileShareName `
    --account-name $StorageAccountName `
    --account-key $StorageKey `
    --query "exists" -o tsv
    
if ($shareExists -eq "false") {
    az storage share create `
        --name $FileShareName `
        --account-name $StorageAccountName `
        --account-key $StorageKey `
        --quota 1024
} else {
    Write-Host "File share $FileShareName already exists." -ForegroundColor Cyan
}

# Generate environment variables file
Write-Host "Generating environment file with MongoDB persistence settings..." -ForegroundColor Green

$MongoUsername = "admin"
$MongoPassword = [System.Guid]::NewGuid().ToString("N").Substring(0, 16)  # Generate a secure random password

$envContent = @"
# MongoDB Persistence Settings for Azure
MONGO_USERNAME=$MongoUsername
MONGO_PASSWORD=$MongoPassword
STORAGE_ACCOUNT_NAME=$StorageAccountName
STORAGE_ACCOUNT_KEY=$StorageKey

# Make sure to add these to your Azure deployment environment variables
"@

# Write to file
$envContent | Out-File -FilePath $OutputEnvFile -Encoding utf8

Write-Host "Setup completed successfully!" -ForegroundColor Green
Write-Host "MongoDB persistence settings have been saved to $OutputEnvFile" -ForegroundColor Green
Write-Host "Important: Store these credentials securely and add them to your Azure deployment environment variables." -ForegroundColor Yellow
Write-Host "For production use, consider storing secrets as GitHub repository secrets." -ForegroundColor Yellow
