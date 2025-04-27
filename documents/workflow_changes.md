# Workflow Changes Documentation

## Frontend Docker Build Fix (2025-04-26)

### Issue
The frontend Docker build was failing with the following error:
```
ERROR: failed to solve: failed to compute cache key: failed to calculate checksum of ref tr1a7lgrwfzf79b9a0dprub4u::x1yuv84tno6odoc0wjpycw155: "/scripts/frontend-check.sh": not found
```

This occurred because the frontend Dockerfile was attempting to copy a file `scripts/frontend-check.sh` from within the frontend build context, but the file existed in the root scripts directory and not within the frontend directory.

### Solution
Modified the frontend `Dockerfile` to embed the health check script directly in the Dockerfile using a Heredoc (`RUN <<EOF > ... EOF`). This approach:

1. Eliminates the dependency on the external script file
2. Makes the Dockerfile more self-contained and handles multi-line script content reliably
3. Removes the need for context preparation steps in the GitHub workflow

### Files Changed
1. `frontend/Dockerfile`: Modified to embed the health check script instead of copying it
2. `.github/workflows/deploy-to-azure.yml`: Removed the "Prepare frontend context" step

### Tests Performed
- Verified the script content matches the original `scripts/frontend-check.sh`
- Confirmed the Docker build process succeeds
- Verified that the frontend container can properly check backend availability

### Notes
- This approach ensures that the frontend container can be built independently without relying on files outside its context
- The embedded script maintains all the functionality of the original script
- Future updates to the health check logic should be made directly in the Dockerfile 

## Backend MongoDB Availability Check Fix (2025-04-27)

### Issue
The backend container was failing to start properly due to the `nc` (netcat) command not being found in the container environment. This command was used in `start-backend.sh` to check if MongoDB was available before starting the application.

### Solution
Updated the `start-backend.sh` script to use a Python-based check for MongoDB availability using the `pymongo` library, which is already a dependency of the backend application. This approach is more reliable in container environments where additional utilities like `nc` might not be available.

### Files Changed
1. `scripts/start-backend.sh`: Changed the MongoDB availability check from `nc` to a Python script using `pymongo`.

### Notes
- This change ensures that the backend can reliably check for MongoDB availability without requiring additional system utilities.
- The `docker-compose.azure.yml` already has proper health checks and dependency conditions to ensure MongoDB is started before the backend. 

## Docker Compose and Startup Fixes (2025-04-27)

### Issue
Multiple issues were causing deployment failures and container startup problems:
1.  Azure deployment failed with a 'Bad Request' error due to incompatible custom `entrypoint` commands in `docker-compose.azure.yml`.
2.  MongoDB authentication was failing because credentials were not being passed correctly to the `MONGO_INITDB_ROOT_*` variables within the `ai-mongo` service.
3.  The backend application was missing the `dash-cytoscape` Python dependency.
4.  Local `docker-compose.yml` was missing a healthcheck for MongoDB.

### Solution
1.  Removed custom `entrypoint` overrides (with `sleep`) from `ai-backend` and `ai-frontend` in `docker-compose.azure.yml`, relying instead on `depends_on`, healthchecks, and application-level wait logic.
2.  Removed the `environment` section from the `ai-mongo` service in `docker-compose.azure.yml`. Authentication is now handled solely by the connecting applications (`ai-backend`, `db-init`) using credentials provided by Azure App Service settings.
3.  Added `dash-cytoscape` to `backend/requirements.txt` (though it seems it was already present).
4.  Added a MongoDB healthcheck to the local `docker-compose.yml`.
5.  Ensured `db-init` runs after `ai-mongo` is healthy and before `ai-backend` starts in `docker-compose.azure.yml` using `depends_on` conditions.

### Files Changed
1.  `docker-compose.azure.yml`: Removed `ai-mongo` environment variables, removed custom `entrypoint` from `ai-backend` and `ai-frontend`, adjusted `depends_on` for `ai-backend`.
2.  `docker-compose.yml`: Added `healthcheck` to `ai-mongo` service.
3.  `backend/requirements.txt`: Ensured `dash-cytoscape` is present.

### Notes
- These changes ensure a more robust startup sequence, correct authentication handling, and fix the Azure deployment error.
- The application relies on environment variables (`MONGO_USERNAME`, `MONGO_PASSWORD`, etc.) being correctly set in the Azure App Service configuration (via the `deploy-to-azure.yml` workflow) for services that need to connect to MongoDB. 