# Azure Deployment Documentation

## Resources Created

- **Resource Group**: `ethicsdash`
- **Container Registry**: `ethicsdashacr`
- **Key Vault**: `ethicsdashkv`
- **Container App Environment**: `ethicsdash`
- **Container App**: `ethicsdash-app`
- **Cosmos DB (MongoDB API)**: `ethicsdash-mongo`
  - **Database**: `ethicsdash-db`
  - **Collection**: `ethical-memes`

## GitHub Secrets

The following secrets are configured in the GitHub repository:

- `ACR_REGISTRY` - The Azure Container Registry URL
- `ACR_USERNAME` - The ACR admin username
- `ACR_PASSWORD` - The ACR admin password
- `AZURE_CLIENT_ID` - The Service Principal app ID for Azure authentication
- `AZURE_TENANT_ID` - The Azure tenant ID
- `AZURE_SUBSCRIPTION_ID` - The Azure subscription ID
- `MONGO_URI` - The MongoDB connection string
- `ANTHROPIC_API_KEY` - The Anthropic API key for Claude LLM

## CI/CD Pipeline

The CI/CD pipeline is defined in `.github/workflows/azure-deploy.yml`. It performs the following steps:

1. Builds the Docker image from the repository's Dockerfile
2. Pushes the image to Azure Container Registry
3. Creates/updates the Container App with the latest image
4. Sets environment variables in the Container App using secrets

## Manual Deployment Steps

If you need to manually deploy the application, follow these steps:

1. Build the Docker image:
   ```bash
   docker build -t ethicsdashacr.azurecr.io/ethicsdash-app:latest .
   ```

2. Login to ACR:
   ```bash
   az acr login --name ethicsdashacr
   ```

3. Push the image to ACR:
   ```bash
   docker push ethicsdashacr.azurecr.io/ethicsdash-app:latest
   ```

4. Deploy to Container App:
   ```bash
   az containerapp update \
     --name ethicsdash-app \
     --resource-group ethicsdash \
     --image ethicsdashacr.azurecr.io/ethicsdash-app:latest
   ```

## Maintenance

### Updating Environment Variables

To update environment variables in the Container App:

```bash
az containerapp update \
  --name ethicsdash-app \
  --resource-group ethicsdash \
  --set-env-vars "KEY=VALUE"
```

### Scaling

The Container App is configured to scale automatically between 1-3 replicas. To adjust scaling parameters:

```bash
az containerapp update \
  --name ethicsdash-app \
  --resource-group ethicsdash \
  --min-replicas 2 \
  --max-replicas 5
``` 