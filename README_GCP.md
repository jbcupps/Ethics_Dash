# Google Cloud Platform (GCP) Deployment Guide (Artifact Registry & Cloud Run)

This guide explains how to set up and use the GitHub Actions workflow (`.github/workflows/gcp_deploy.yml`) to build Docker images, push them to GCP Artifact Registry, and deploy the services to GCP Cloud Run.

## Prerequisites

-   Google Cloud Platform (GCP) Project
-   GCP Billing Enabled
-   `gcloud` CLI installed locally (optional, for setup verification)
-   GitHub repository with the `gcp_deploy.yml` workflow file
-   A MongoDB instance accessible from GCP (e.g., MongoDB Atlas, self-hosted on GCE/GKE)

## Setup Steps

1.  **Enable GCP APIs:** In your GCP project, enable the following APIs:
    * Artifact Registry API
    * Cloud Run Admin API
    * Cloud Build API (used implicitly by some actions)
    * IAM Service Account Credentials API (for Workload Identity Federation)

2.  **Create Artifact Registry Repository:**
    ```bash
    gcloud artifacts repositories create <YOUR_REPO_NAME> \
        --repository-format=docker \
        --location=<YOUR_REGION> \
        --description="Docker repository for Ethics Dash" \
        --project=<YOUR_PROJECT_ID>
    ```
    *(Replace placeholders)*

3.  **Set up Workload Identity Federation:** This is the recommended secure way for GitHub Actions to authenticate to GCP without service account keys.
    * Follow the official GCP guide: [Configuring Workload Identity Federation](https://cloud.google.com/iam/docs/configuring-workload-identity-federation#github)
    * Create a Workload Identity Pool and Provider linked to your GitHub repository.
    * Create a GCP Service Account (e.g., `github-actions-deployer@...`).
    * Grant the Service Account the necessary IAM roles:
        * `roles/artifactregistry.writer` (to push images)
        * `roles/run.admin` (to deploy to Cloud Run)
        * `roles/iam.serviceAccountUser` (to impersonate the service account)
        * (Optional) Roles for accessing secrets if using Secret Manager (e.g., `roles/secretmanager.secretAccessor`).
    * Allow the GitHub Actions identity (linked to your repository/branch) to impersonate the GCP Service Account via an IAM policy binding on the Service Account.

4.  **Configure GitHub Secrets:**
    Navigate to your GitHub repository's `Settings` > `Secrets and variables` > `Actions` and add the following repository secrets:
    * `GCP_PROJECT_ID`: Your Google Cloud Project ID.
    * `GCP_WORKLOAD_IDENTITY_PROVIDER`: The full resource name of the Workload Identity Provider you created (e.g., `projects/123456789/locations/global/workloadIdentityPools/github-pool/providers/github-provider`).
    * `GCP_SERVICE_ACCOUNT_EMAIL`: The email address of the GCP Service Account you created (e.g., `github-actions-deployer@your-project-id.iam.gserviceaccount.com`).
    * `GCP_ARTIFACT_REGISTRY_REGION`: The region of your Artifact Registry (e.g., `us-central1`).
    * `GCP_ARTIFACT_REGISTRY_REPO`: The name of your Artifact Registry repository (e.g., `ethics-dash-repo`).
    * `GCP_CLOUD_RUN_REGION`: The region where you want to deploy Cloud Run services (e.g., `us-central1`).
    * `GCP_MONGO_URI`: The **connection string** for your cloud MongoDB instance (e.g., MongoDB Atlas connection string). **Store this securely!**
    * **(Optional but Recommended)** Store LLM API keys in GCP Secret Manager and grant the Service Account access, then reference them in Cloud Run environment variables. Alternatively, store them as GitHub secrets and pass them during deployment (less secure).

5.  **Understand the Workflow:**
    * The `.github/workflows/gcp_deploy.yml` workflow triggers on pushes to the `main` branch or manually.
    * It checks out the code.
    * It authenticates to GCP using Workload Identity Federation.
    * It configures Docker to push to Artifact Registry.
    * It builds the `ai-backend` and `ai-frontend` Docker images.
    * It pushes the images to Artifact Registry, tagged with the Git SHA.
    * It deploys the `ai-backend` image to Cloud Run, setting necessary environment variables (like `MONGO_URI`).
    * It deploys the `ai-frontend` image to Cloud Run, potentially passing the backend URL as an environment variable.
    * It outputs the URLs of the deployed services.

## Running the Deployment Workflow

1.  **Automatic Trigger:** Push changes to the `main` branch of your repository.
2.  **Manual Trigger:**
    * Go to the "Actions" tab in your GitHub repository.
    * Select the "Build and Deploy to GCP Artifact Registry and Cloud Run" workflow.
    * Click "Run workflow" and choose the branch (usually `main`).

## Accessing the Deployed Application

Once the workflow completes successfully, the frontend application will be available at the URL outputted by the final step (Frontend Service URL).

## Important Notes

-   **DB Initialization:** This workflow does *not* automatically run the `db-init` container. You will need to run the database population script (`scripts/populate_memes.py`) manually against your cloud MongoDB instance the first time, or create a GCP Cloud Build job or a GKE Job to handle this initialization step using the `db-init` image (which you'd need to add build/push steps for in the workflow).
-   **Secret Management:** Passing secrets like `GCP_MONGO_URI` directly as GitHub secrets is less secure than using GCP Secret Manager and granting the Cloud Run service account access. Adapt the workflow accordingly for better security.
-   **Nginx Configuration:** The `ai-frontend` (Nginx) container needs to be correctly configured (in its `nginx.conf` or similar) to proxy API calls (`/api/*`) to the backend Cloud Run service URL. The workflow attempts to pass this dynamically, but verify the Nginx configuration handles it.
-   **Cloud Run Settings:** Adjust Cloud Run flags (`--min-instances`, `--max-instances`) 