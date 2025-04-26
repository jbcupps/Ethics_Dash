# Azure Web App Deployment Guide

## Overview

This document provides information about deploying the Ethics Dashboard application to Azure Web App for Containers. The deployment uses multi-container configuration with Docker Compose to set up the complete application stack including frontend, backend, MongoDB, and database initialization service.

## Architecture

The Ethics Dashboard application is deployed as a multi-container application with the following components:

1. **Frontend** - Nginx serving the React application
2. **Backend** - Python backend API service
3. **MongoDB** - Database for the application
4. **DB-Init** - One-time service to initialize the database with required data

## Docker Compose Configuration

The deployment uses a special `docker-compose.azure.yml` file that is optimized for Azure Web App for Containers. This file:

- Uses a simpler format compatible with Azure Web App
- Removes advanced Docker Compose features like custom healthchecks which may not be supported
- Sets restart policies for the containers
- Uses direct image references to Azure Container Registry

## Environment Variables

The following environment variables are configured in the Azure Web App:

- `MONGO_URI` - MongoDB connection string
- `NODE_ENV` - Set to "production" for production deployment
- `LOG_LEVEL` - Log level for the application
- `API_VERSION` - API version for the backend
- `WEBSITES_ENABLE_APP_SERVICE_STORAGE` - Disabled to prevent using Azure storage for container data

## Troubleshooting

### "Bad Request" Error When Deploying

If you encounter a "Bad Request" error when deploying via GitHub Actions, check the following:

1. **Docker Compose Format**: Ensure the docker-compose.azure.yml file uses a compatible version (3.4) and only includes features supported by Azure Web App
2. **Image References**: Make sure all image references are valid and accessible
3. **Volume Configuration**: Check that volume definitions are simple and don't use custom options
4. **Container Names**: Remove explicit container_name definitions
5. **Healthchecks**: Remove healthcheck configurations as they might not be supported
6. **Depends On**: Use simple depends_on format without condition options

### Container Startup Issues

If containers fail to start after deployment:

1. **Check Logs**: Use the Azure Portal or Azure CLI to view container logs
   ```bash
   az webapp log download --resource-group YOUR_RESOURCE_GROUP --name YOUR_WEBAPP_NAME --log-file logs.zip
   ```

2. **Environment Variables**: Verify that all required environment variables are set
3. **Image Accessibility**: Ensure Azure Web App has access to pull images from ACR
4. **Memory/CPU Limits**: Check if containers are hitting resource limits
5. **Network Configuration**: Verify that containers can communicate with each other

### MongoDB Persistence Issues

If MongoDB data is not persisting:

1. **Volume Configuration**: Check that the MongoDB volume is properly configured
2. **Storage Configuration**: Verify Azure Web App storage settings
3. **App Service Plan**: Ensure your App Service Plan supports persistent storage

## Deployment Verification

After deployment, verify the application by:

1. Accessing the frontend at `https://YOUR_WEBAPP_NAME.azurewebsites.net`
2. Checking that the backend API is responding at `https://YOUR_WEBAPP_NAME.azurewebsites.net/api/health`
3. Verifying that the database has been initialized with required data

## Continuous Deployment

The GitHub Actions workflow handles CI/CD for the application. It:

1. Builds container images for frontend, backend, and db-init services
2. Pushes these images to Azure Container Registry
3. Configures the Azure Web App with appropriate settings
4. Deploys the application using the docker-compose.azure.yml file
5. Verifies the deployment and displays logs for troubleshooting 