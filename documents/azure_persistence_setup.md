# MongoDB Persistence Setup in Azure

This document explains how to configure persistent MongoDB storage for the Ethics Dashboard application when deployed in Azure.

## Overview

The Ethics Dashboard uses MongoDB to store various data, including ethical memes used during analysis. By default, the Docker container's MongoDB data is stored inside the container, which means data is lost when containers are rebuilt or redeployed.

To ensure data persistence between container rebuilds, we use Azure File Storage to host the MongoDB data directory.

## Configuration

### 1. Azure Storage Account Setup

First, create an Azure Storage Account and File Share:

```powershell
# Login to Azure
az login

# Create Resource Group (if not already created)
az group create --name ethicsdash-rg --location eastus

# Create Storage Account
az storage account create \
    --name ethicsdashstorage \
    --resource-group ethicsdash-rg \
    --location eastus \
    --sku Standard_LRS

# Get Storage Account Key
$STORAGE_KEY=$(az storage account keys list \
    --resource-group ethicsdash-rg \
    --account-name ethicsdashstorage \
    --query "[0].value" -o tsv)

# Create File Share
az storage share create \
    --name ethicsdash-mongo-data \
    --account-name ethicsdashstorage \
    --account-key $STORAGE_KEY
```

### 2. Environment Variables

Add the following environment variables to your deployment:

```
MONGO_USERNAME=admin
MONGO_PASSWORD=your_secure_password
STORAGE_ACCOUNT_NAME=ethicsdashstorage
STORAGE_ACCOUNT_KEY=your_storage_account_key
```

### 3. Sidecar Configuration

The `sidecar.azure.yml` file has been configured with:

- MongoDB authentication using environment variables
- Azure File Storage driver for the `mongo_data` volume
- Health check for MongoDB to ensure dependent services start only when the database is ready

### 4. How It Works

1. The MongoDB container mounts a volume that's backed by Azure File Storage
2. When data is written to MongoDB, it's stored in this persistent volume
3. If the container is rebuilt or restarted, it reconnects to the same storage
4. Data persists across deployments, scaling events, and host failures

### 5. Security Considerations

- Use strong, unique passwords for MongoDB authentication if you choose to enable it.
- When authentication is enabled, store credentials securely (for example, in GitHub Secrets) and reference them in your deployment.
- Consider encrypting data at rest by enabling encryption on your storage account
- Restrict network access to your storage account using firewall rules

### 6. Backup Recommendations

In addition to using persistent storage, implement a regular backup strategy:

- Schedule regular MongoDB dumps to a separate storage location
- Consider using Azure Backup services for the file share
- Test restoration procedures periodically

## Troubleshooting

If the MongoDB container fails to start:

1. Check storage account accessibility
2. Verify storage account keys are correct
3. Ensure the file share exists
4. Check MongoDB logs for authentication issues

If data appears to be lost:

1. Verify the volume is correctly mounted
2. Check if the environment variables are correctly set
3. Ensure the connection string in dependent services includes authentication

## Additional Resources

- [Azure Storage Documentation](https://docs.microsoft.com/en-us/azure/storage/)
- [Docker Volume Plugins](https://docs.docker.com/engine/extend/plugins_volume/)
- [MongoDB Security Checklist](https://docs.mongodb.com/manual/administration/security-checklist/) 