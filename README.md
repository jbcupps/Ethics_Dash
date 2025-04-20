# Ethics Dashboard

<!-- Project Description: A brief overview of what the Ethics Dashboard does. -->
A web application focused on ethical analysis using AI models, leveraging backend processes for validation, model selection, and result generation.

## Table of Contents

- [Prerequisites](#prerequisites)
- [Setup](#setup)
  - [Azure Container Registry (ACR)](#azure-container-registry-acr)
  - [GitHub Secrets](#github-secrets)
- [Local Development](#local-development)
- [Configuration](#configuration)
  - [Environment Variables (`.env`)](#environment-variables-env)
  - [Available GitHub Secrets](#available-github-secrets)
- [API Usage](#api-usage)
- [CI/CD Pipeline](#cicd-pipeline)
- [Security Notes](#security-notes)

## Prerequisites

<!-- List all necessary software and accounts needed before starting the setup. -->
- Azure CLI installed
- Docker installed
- GitHub account with repository access
- GitHub CLI installed (`gh`)
- PowerShell 5.1 or later (for Windows users)

## Setup

<!-- Steps required to set up the project environment, including cloud resources and repository secrets. -->

### Azure Container Registry (ACR)

1.  **Create an Azure Container Registry:**
    ```bash
    # Replace <your-resource-group> and <your-registry-name> with your actual Azure resource group and desired ACR name
    az acr create --resource-group <your-resource-group> --name <your-registry-name> --sku Basic
    ```

### GitHub Secrets

Configure GitHub Actions secrets to allow the CI/CD pipeline to authenticate with Azure and potentially other services.

1.  **Install GitHub CLI:** If not already installed, follow the instructions at [https://cli.github.com/](https://cli.github.com/).
2.  **Login to GitHub CLI:** Authenticate the CLI with your GitHub account:
    ```bash
    gh auth login
    ```
3.  **Run the Setup Script:**
    -   The provided script (`scripts/setup-github-secrets.sh` or similar) helps automate the process of setting necessary secrets in your GitHub repository.
    -   It will likely prompt for ACR credentials (`ACR_REGISTRY`, `ACR_USERNAME`, `ACR_PASSWORD`) and any required API keys/secrets (`API_KEY`, `API_SECRET`, etc.).
    -   Using placeholder values initially is acceptable if the actual credentials are not yet available; they can be updated later via the GitHub UI or CLI.

    *Using Bash (Linux/macOS):*
    ```bash
    # Ensure the script is executable
    chmod +x scripts/setup-github-secrets.sh
    # Run the script
    ./scripts/setup-github-secrets.sh
    ```

    <!-- TODO: Add specific instructions for the PowerShell script if one exists and differs significantly -->
    <!-- *Using PowerShell (Windows):* -->
    <!-- ```powershell -->
    <!-- # Example: .\scripts\setup-github-secrets.ps1 -->
    <!-- ``` -->


## Local Development

<!-- Simplify and clarify instructions for setting up environment files and running services. -->
This project uses Docker Compose to run both frontend and backend services locally. Follow these steps:

1.  **Copy and configure environment files**:
    ```bash
    # Copy root configuration
    cp .env.example .env
    # The file 'backend/backend.env' already contains placeholders for LLM API keys and models.
    # Edit it in-place to fill in your OpenAI, Anthropic, and Gemini keys, and set DEFAULT_LLM_MODEL and ANALYSIS_LLM_MODEL.
    ```

2.  **Build Docker images**:
    ```bash
    # Use Docker Compose v2 syntax
    docker compose build
    ```

3.  **Start all services**:
    ```bash
    docker compose up -d
    ```

4.  **View service logs** (for troubleshooting):
    ```bash
    docker compose logs -f ai-backend
    docker compose logs -f ai-frontend
    docker compose logs -f app
    ```

5.  **Stop and remove containers**:
    ```bash
    docker compose down
    ```

6.  **Optional: Rebuild a single service**:
    ```bash
    docker compose build ai-backend
    docker compose up -d ai-backend
    ```

## Configuration

<!-- Details about configuration files, environment variables, and secrets management. -->

### Environment Variables (`.env`)

-   The `.env` file stores configuration variables for the **local development environment only**.
-   It is based on the `.env.example` template.
-   **Crucially, this file should be listed in your `.gitignore` file and NEVER committed to version control.**

### Available GitHub Secrets

The CI/CD pipeline defined in `.github/workflows/` relies on the following secrets configured at the GitHub repository or organization level:

<!-- List secrets used in the CI/CD pipeline -->
#### ACR Configuration
-   `ACR_REGISTRY`: The login server name/URL of your Azure Container Registry (e.g., `<your-registry-name>.azurecr.io`).
-   `ACR_USERNAME`: The username for authenticating with ACR (often a service principal ID).
-   `ACR_PASSWORD`: The password or secret corresponding to the `ACR_USERNAME`.

#### API Configuration
-   `API_KEY`: Primary key or identifier for accessing a required API.
-   `API_SECRET`: Secret or secondary key for API authentication.
-   `API_ENDPOINT`: Base URL for the API endpoint.
-   `API_VERSION`: Specific version of the API being targeted (if applicable).

#### Environment Configuration
-   `NODE_ENV`: Specifies the runtime environment (e.g., `development`, `staging`, `production`). This often controls framework behavior, logging levels, etc.
-   `LOG_LEVEL`: Determines the verbosity of application logs (e.g., `debug`, `info`, `warn`, `error`).

## API Usage

<!-- Instructions on how to interact with the project's API(s). -->

### Base URL
The base URL for the API is configured via the `API_ENDPOINT` environment variable or GitHub secret.
- **Local Development:** Check your `.env` file.
- **Deployed Environments:** Refer to the environment configuration or the `API_ENDPOINT` secret value used in the CI/CD pipeline.

### Authentication
Authentication is typically handled using the `API_KEY` and `API_SECRET`.
- **Mechanism:** Authentication details (e.g., header names like `X-API-KEY` or `Authorization`) should be verified in the API implementation.
- **Credentials:** Obtain the necessary key and secret from the configured GitHub Secrets or your local `.env` file.

### Endpoints
Detailed API endpoint documentation is not currently linked here. Please refer to the API source code or create dedicated documentation (e.g., using Swagger/OpenAPI). The `docs/R2_Ethical_Analysis_Flow.md` file describes the `/analyze` endpoint flow.

Example: "Detailed API endpoint documentation can be found in the [API Specification](link-to-spec-or-docs)."

### Versioning
The API version may be specified by the `API_VERSION` configuration variable. If used, include this information in your requests as needed (e.g., in the URL path or an `Accept` header). The specific implementation of API versioning (if any) should be verified in the API source code.

## CI/CD Pipeline

<!-- Overview of the continuous integration and deployment process facilitated by GitHub Actions. -->
This repository utilizes GitHub Actions for its Continuous Integration and Continuous Deployment (CI/CD) pipeline. The workflow configuration can be found in `.github/workflows/`.

Key features of the pipeline include:
-   **Automated Builds:** Automatically builds Docker images upon pushes to the `main` branch (or other configured branches/events).
-   **ACR Integration:** Pushes the successfully built Docker images to the specified Azure Container Registry (ACR).
-   **Docker Layer Caching:** Leverages caching to speed up subsequent image builds.
-   **Multi-Platform Support:** Configured to build images compatible with multiple architectures (if needed).
-   **Notifications:** Provides feedback on the success or failure of workflow runs.
-   **Manual Trigger:** Allows the workflow to be triggered manually from the GitHub Actions UI.
-   **Configuration Verification:** May include steps to validate necessary API configurations or environment settings.
-   **Environment-Specific Settings:** Can adapt behavior based on the target environment (e.g., using different secrets for staging vs. production if workflows are structured accordingly).

## Security Notes

<!-- Critical security practices and considerations relevant to this project. -->
-   **Secret Management:** Never commit sensitive information like passwords, API keys, or `.env` files directly into the Git repository. Use `.gitignore` to prevent accidental commits.
-   **Production Secrets:** For production deployments, prioritize secure secret management solutions like Azure Key Vault over environment variables stored directly on the host or less secure methods. Integrate Key Vault access into your deployment process.
-   **Credential Rotation:** Regularly rotate credentials used for accessing ACR, APIs, and other sensitive resources. Update the corresponding GitHub Secrets promptly.
-   **GitHub Secret Security:** GitHub encrypts secrets, making them inaccessible directly after creation (only usable within Actions). Ensure repository access controls are appropriate.
-   **PowerShell Execution Policy (Windows):** If using PowerShell scripts for setup or tasks, be mindful of the system's execution policy. Changes should be understood and potentially reverted if temporary. Apply the principle of least privilege.