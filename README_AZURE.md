# Azure Deployment Guide (ACR)

This guide explains how to set up and use the GitHub Actions workflow (`.github/workflows/deploy-to-azure.yml`) to build Docker images and push them to Azure Container Registry (ACR). This workflow *only* handles the image push; deploying to a service like Azure App Service or Azure Container Instances requires additional steps or workflow modifications.

## Prerequisites

-   Azure Subscription
-   Azure CLI installed and configured
-   GitHub repository with the `deploy-to-azure.yml` workflow file
-   An Azure Container Registry (ACR) instance
-   An Azure Service Principal or configuration for GitHub OIDC authentication with Azure
-   Azure Storage Account for MongoDB persistence (see below)

## Setup Steps

1.  **Create Azure Resources (if not existing):**
    * Azure Resource Group
    * Azure Container Registry (ACR)
    * Azure Service Principal (SPN) with `AcrPush` role assigned to your ACR **OR** configure GitHub OIDC authentication (Recommended).
    * Azure Storage Account for persistent MongoDB storage (see MongoDB Persistence section)

2.  **Configure GitHub Secrets:**
    Navigate to your GitHub repository's `Settings` > `Secrets and variables` > `Actions` and add the following repository secrets:
    * `AZURE_CLIENT_ID`: The Client ID (or App ID) of your Azure Service Principal or the OIDC-linked App Registration.
    * `AZURE_TENANT_ID`: Your Azure Active Directory Tenant ID.
    * `AZURE_SUBSCRIPTION_ID`: Your Azure Subscription ID.
    * `ACR_REGISTRY_NAME`: The full login server name of your ACR (e.g., `myethicsdashacr.azurecr.io`).
    * `ACR_SP_PASSWORD`: The password or secret for your Azure Service Principal. **(Skip if using OIDC and role assignments for Docker login)**. *Alternatively, configure OIDC to allow Docker login without a password secret.*
    * `MONGO_USERNAME`: Username for MongoDB authentication.
    * `MONGO_PASSWORD`: Password for MongoDB authentication.
    * `STORAGE_ACCOUNT_NAME`: Name of your Azure Storage Account.
    * `STORAGE_ACCOUNT_KEY`: Access key for your Azure Storage Account.

3.  **Understand the Workflow:**
    * The `.github/workflows/deploy-to-azure.yml` workflow triggers on pushes to the `main` branch or can be run manually.
    * It checks out the code.
    * It logs into Azure using the provided secrets (OIDC recommended).
    * It logs into ACR.
    * It builds the Docker images for `ai-backend`, `ai-frontend`, and `db-init` using their respective Dockerfiles.
    * It tags the images with the ACR name and the Git SHA (`<acr_name>/<image_name>:<git_sha>`).
    * It pushes the tagged images to your ACR.

## MongoDB Persistence Setup

The Ethics Dashboard application uses MongoDB to store data including ethical memes. To ensure data persistence between container rebuilds, we've configured the `docker-compose.azure.yml` file to use Azure File Storage.

### Setting up Persistent Storage

1. **Run the automated setup script:**
   ```powershell
   ./scripts/setup_azure_mongodb_persistence.ps1
   ```
   This script will:
   - Create a resource group (if it doesn't exist)
   - Create a storage account (if it doesn't exist)
   - Create a file share for MongoDB data
   - Generate secure MongoDB credentials
   - Create a `.env.azure` file with the necessary environment variables

2. **Add the generated environment variables to your deployment:**
   Add the following environment variables to your Azure deployment service:
   - `MONGO_USERNAME`
   - `MONGO_PASSWORD`
   - `STORAGE_ACCOUNT_NAME`
   - `STORAGE_ACCOUNT_KEY`

3. **Security Considerations:**
   - If you deploy using the provided Docker Compose setup, MongoDB runs inside
     the container without authentication. The `MONGO_USERNAME` and
     `MONGO_PASSWORD` variables can be left empty.
   - Use Azure Private Endpoints for your storage account in production.
   - Regularly rotate any credentials and storage account keys if you enable
     authentication.

For more detailed information, see `documents/azure_persistence_setup.md`.

## Running the Deployment Workflow

1.  **Automatic Trigger:** Push changes to the `main` branch of your repository.
2.  **Manual Trigger:**
    * Go to the "Actions" tab in your GitHub repository.
    * Select the "Build and Push to Azure Container Registry" workflow.
    * Click "Run workflow" and choose the branch (usually `main`).

## Next Steps (Deployment to Azure Services)

This workflow only pushes images to ACR. To deploy the application, you need to:

1.  **Choose an Azure Hosting Service:**
    * **Azure App Service (Web App for Containers):** Suitable for web apps, supports multi-container using Docker Compose (ensure volume mounts are compatible or removed/adapted). You would configure App Service to pull images from your ACR. **Note:** The volume errors seen in logs suggest direct Docker Compose deployment with host binds might be problematic here; adapt the compose file or use alternative volume strategies.
    * **Azure Container Instances (ACI):** Simple way to run containers without orchestration. You can deploy containers individually or using a YAML definition, pulling from ACR.
    * **Azure Kubernetes Service (AKS):** Full Kubernetes orchestration for complex deployments. (Recommended for production use with persistent storage)

2.  **Configure Deployment:** Update your chosen service to use the images tagged with the latest Git SHA from your ACR. This often involves updating service definitions, ARM templates, Bicep files, or Terraform configurations. You might extend the GitHub Actions workflow to include deployment steps using Azure CLI commands (`az webapp config container set`, `az container create`, `kubectl apply`, etc.).

3.  **Manage Secrets:** Ensure your deployed application has secure access to necessary secrets (API keys, Database URI). Store them as GitHub repository secrets and reference them in your workflow or App Service configuration.
