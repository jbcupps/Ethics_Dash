# Azure App Service Networking Configuration

## Problem

The Ethics Dashboard deployment to Azure App Service was experiencing networking issues between containers, resulting in connection errors:

```
connect() failed (111: Connection refused) while connecting to upstream
```

The frontend Nginx container was unable to connect to the backend API container, despite both being defined in the same Docker Compose file.

## Root Cause

Azure App Service multi-container deployments have some specific networking behaviors different from standard Docker Compose deployments:

1. **Simplified Networking**: Azure App Service's implementation of Docker Compose supports a more limited subset of features compared to standard Docker Compose.

2. **Service Discovery**: The DNS-based service discovery may not work exactly as expected with dynamic configuration using environment variables.

3. **Health Checks**: Custom health checks might not be properly respected or might interfere with Azure's own container health monitoring.

4. **Container Startup Timing**: The services may start up in a different order or at different speeds compared to local Docker, leading to connection issues during initialization.

## Solution

The following changes were made to address the networking issues:

### 1. Simplified Docker Compose Configuration

- Removed explicit network definitions
- Removed custom health checks
- Removed environment variables for service discovery
- Retained only essential configuration
- Reordered services to ensure MongoDB is started first

### 2. Direct Service References in Nginx

- Modified the Nginx configuration to use direct service names (`http://ai-backend:5000`) instead of environment variable substitution
- Removed resolver configuration that relies on Docker's DNS system
- Added longer timeouts for proxy connections
- Implemented Nginx retry mechanisms for upstream failures

### 3. Simplified Frontend Container

- Removed environment variable substitution in the Nginx configuration
- Removed the custom entrypoint script
- Used a direct Nginx configuration with hardcoded service names

### 4. Improved Backend Startup Sequence

- Enabled MongoDB connection checking in the backend entrypoint script
- Added explicit waiting periods to ensure proper service initialization
- Increased Gunicorn timeout to allow for longer startup operations
- Added fault tolerance for initialization errors

## Results

After implementing these changes, the containers can properly communicate with each other within the Azure App Service environment. The simplified configuration is more compatible with Azure's implementation of multi-container apps, and the improved startup sequence ensures that services wait for their dependencies to be ready.

## Best Practices for Azure App Service Multi-Container Apps

1. **Use Simple Configuration**: Keep Docker Compose files as simple as possible for Azure App Service.

2. **Direct Service References**: Use direct service names rather than dynamic environment variables for service discovery.

3. **Avoid Custom Health Checks**: Let Azure handle container health monitoring.

4. **Increase Timeouts**: Use longer timeouts in Nginx proxy configuration to account for potential delays during container startup.

5. **Monitor Container Logs**: Use Azure's logging features to monitor container startup and communication issues.

6. **Implement Retries**: Add retry mechanisms in both the application and proxy configurations.

7. **Explicit Service Ordering**: Order services in the Docker Compose file to ensure proper startup sequence.

8. **Startup Waits**: Add explicit wait periods in entrypoint scripts for critical dependencies.

## Additional Resources

- [Azure App Service Docker Compose Support](https://docs.microsoft.com/en-us/azure/app-service/configure-custom-container?pivots=container-linux#docker-compose-options)
- [Troubleshooting Multi-Container Apps](https://docs.microsoft.com/en-us/azure/app-service/configure-custom-container?pivots=container-linux#troubleshoot-multi-container-configuration) 