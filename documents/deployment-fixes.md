# Deployment Configuration Fixes

## Azure Web App Multi-Container Deployment Fix

### Issue
Azure CLI deployment was failing with error:
```
ERROR: az webapp config container set: 'sidecar' is not a valid value for '--multicontainer-config-type'. Allowed values: COMPOSE, KUBE.
```

### Root Cause
The GitHub Actions workflow was attempting to use `--multicontainer-config-type sidecar` which is not a supported configuration type in Azure Web App. Azure Web App only supports:
- `COMPOSE` - For Docker Compose configurations
- `KUBE` - For Kubernetes configurations

### Solution
Updated the `.github/workflows/deploy-to-azure.yml` file:

**Before:**
```yaml
--multicontainer-config-type sidecar \
--multicontainer-config-file sidecar.azure.yml
```

**After:**
```yaml
--multicontainer-config-type COMPOSE \
--multicontainer-config-file docker-compose.azure.yml
```

### Files Modified
- `.github/workflows/deploy-to-azure.yml` - Changed deployment configuration to use COMPOSE type

### Files Available for Deployment
- `docker-compose.azure.yml` - Azure-specific Docker Compose configuration (used for deployment)
- `sidecar.azure.yml` - Legacy sidecar configuration (kept for reference)
- `docker-compose.yml` - Local development Docker Compose configuration

### Deployment Command
The corrected Azure CLI command now properly uses Docker Compose format:
```bash
az webapp config container set \
  --resource-group ethicsdash-rg \
  --name ethicsdash-cicd-app \
  --multicontainer-config-type COMPOSE \
  --multicontainer-config-file docker-compose.azure.yml
```

### Next Steps
1. Test the deployment with the corrected configuration
2. Verify all containers start properly in Azure Web App
3. Monitor application logs for any runtime issues
4. Consider removing the `sidecar.azure.yml` file if no longer needed

### Date
Updated: December 2024 