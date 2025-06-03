# Setting Up Persistent Storage for MongoDB in Azure

This document outlines the steps to configure persistent storage for MongoDB in Azure using Azure Storage Account and Azure Files.

## Prerequisites

- Azure CLI installed and configured
- Access to the Ethics Dashboard Azure subscription
- Proper permissions to create resources in the resource group

## Configuration Steps

### 1. Login to Azure (if not already logged in)

```bash
az login
```

### 2. Set Variables

```bash
# Resource Group (using the same one from GitHub workflow)
RESOURCE_GROUP="ethicsdash-rg"

# Region - modify based on your preference
LOCATION="eastus"

# Storage Account name must be globally unique
STORAGE_ACCOUNT_NAME="ethicsdashdbstorage"

# File Share name for MongoDB data
FILE_SHARE_NAME="mongodbdata"

# Size of the file share (100GB)
FILE_SHARE_QUOTA=100
```

### 3. Create or use the existing Resource Group

```bash
# Check if resource group exists
if ! az group show --name $RESOURCE_GROUP &> /dev/null; then
    echo "Creating resource group $RESOURCE_GROUP..."
    az group create --name $RESOURCE_GROUP --location $LOCATION
else
    echo "Using existing resource group $RESOURCE_GROUP"
fi
```

### 4. Create Storage Account

```bash
# Check if storage account exists
if ! az storage account show --name $STORAGE_ACCOUNT_NAME --resource-group $RESOURCE_GROUP &> /dev/null; then
    echo "Creating storage account $STORAGE_ACCOUNT_NAME..."
    az storage account create \
        --name $STORAGE_ACCOUNT_NAME \
        --resource-group $RESOURCE_GROUP \
        --location $LOCATION \
        --sku Standard_LRS \
        --kind StorageV2 \
        --https-only true \
        --min-tls-version TLS1_2
else
    echo "Using existing storage account $STORAGE_ACCOUNT_NAME"
fi
```

### 5. Create Azure File Share

```bash
# Get the storage account key
STORAGE_KEY=$(az storage account keys list \
    --resource-group $RESOURCE_GROUP \
    --account-name $STORAGE_ACCOUNT_NAME \
    --query "[0].value" -o tsv)

# Create file share if it doesn't exist
if ! az storage share exists \
    --name $FILE_SHARE_NAME \
    --account-name $STORAGE_ACCOUNT_NAME \
    --account-key $STORAGE_KEY \
    --query "exists" -o tsv | grep -q "true"; then
    
    echo "Creating file share $FILE_SHARE_NAME..."
    az storage share create \
        --name $FILE_SHARE_NAME \
        --account-name $STORAGE_ACCOUNT_NAME \
        --account-key $STORAGE_KEY \
        --quota $FILE_SHARE_QUOTA
else
    echo "Using existing file share $FILE_SHARE_NAME"
fi
```

### 6. Update Web App Configuration to Mount the File Share

```bash
# Web App name (from GitHub workflow)
WEBAPP_NAME="ethicsdash-cicd-app"

# Configure storage for the Web App
az webapp config storage-account add \
    --resource-group $RESOURCE_GROUP \
    --name $WEBAPP_NAME \
    --custom-id mongodb-data \
    --storage-type AzureFiles \
    --share-name $FILE_SHARE_NAME \
    --account-name $STORAGE_ACCOUNT_NAME \
    --access-key $STORAGE_KEY \
    --mount-path /data/db
```

### 7. Update the Sidecar Configuration

Now, modify the `sidecar.azure.yml` file to use the mounted storage path instead of a Docker volume:

```yaml
version: '3.4'

services:
  # Start MongoDB first since it's needed by all services
  ai-mongo:
    image: mongo:latest
    ports:
      - "27017:27017"
    volumes:
      - ${WEBAPP_STORAGE_HOME}/data/db:/data/db
    restart: always

  # Other services remain the same...
  
  # Remove the volumes section since we're using Azure Files now
```

### 8. Redeploy the Web App

After updating the Docker Compose file, redeploy the application using the GitHub Actions workflow.

## Verifying the Storage

To verify that MongoDB is correctly using the Azure File Share:

1. Connect to the MongoDB container in the Web App
2. Check that data is being written to the mounted path
3. Restart the Web App and verify that data persists

## Troubleshooting

If you encounter issues:

1. Check that the storage account and file share exist
2. Verify that the Web App has the correct permissions to access the storage
3. Check the Web App logs for any mounting errors
4. Ensure that the MongoDB container has write permissions to the mounted directory 