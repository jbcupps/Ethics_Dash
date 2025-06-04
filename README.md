# Ethics Dashboard

<!-- Project Description: A brief overview of what the Ethics Dashboard does. -->
A web application focused on ethical analysis using AI models, leveraging backend processes for validation, model selection, and result generation.

## Table of Contents

- [Prerequisites](#prerequisites)
- [Setup](#setup)
- [Local Development](#local-development)
- [Configuration](#configuration)
  - [Environment Variables (`.env`)](#environment-variables-env)
- [API Usage](#api-usage)
- [Physical Verification Blockchain (PVB)](#physical-verification-blockchain-pvb)
- [Security Notes](#security-notes)

## Prerequisites

<!-- List all necessary software and accounts needed before starting the setup. -->
- Docker installed
- Docker Compose installed
- PowerShell 5.1 or later (for Windows users)

## Setup

1. Clone the repository
2. Copy the example environment file:
   ```bash
   cp .env.example .env
   ```
3. Edit `.env` to configure your environment variables (API keys, etc.)

## Local Development

<!-- Simplify and clarify instructions for setting up environment files and running services. -->
This project uses Docker Compose to run both frontend and backend services locally. Follow these steps:

1.  **Copy and configure environment files**:
    ```bash
    # Copy root configuration
    cp .env.example .env
    # The file 'backend.env' already contains placeholders for LLM API keys and models.
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

Required environment variables:
- `API_KEY`: Primary key for accessing required APIs
- `API_SECRET`: Secret or secondary key for API authentication
- `API_ENDPOINT`: Base URL for the API endpoint
- `API_VERSION`: Specific version of the API being targeted
- `NODE_ENV`: Specifies the runtime environment (e.g., `development`, `production`)
- `LOG_LEVEL`: Determines verbosity of application logs

## API Usage

<!-- Instructions on how to interact with the project's API(s). -->

### Base URL
The base URL for the API is configured via the `API_ENDPOINT` environment variable.
- **Local Development:** Check your `.env` file.

### Authentication
Authentication is handled using the `API_KEY` and `API_SECRET`.
- **Mechanism:** Authentication details (e.g., header names like `X-API-KEY` or `Authorization`) should be verified in the API implementation.
- **Credentials:** Obtain the necessary key and secret from your local `.env` file.

### Endpoints
Detailed API endpoint documentation is not currently linked here. Please refer to the API source code or create dedicated documentation (e.g., using Swagger/OpenAPI). The `docs/R2_Ethical_Analysis_Flow.md` file describes the `/analyze` endpoint flow.

### Versioning
The API version may be specified by the `API_VERSION` configuration variable. If used, include this information in your requests as needed (e.g., in the URL path or an `Accept` header). The specific implementation of API versioning (if any) should be verified in the API source code.

## Physical Verification Blockchain (PVB)

The Ethics Dashboard includes a Physical Verification Blockchain (PVB) system that provides cryptographically secure chain of custody for media and data. This system enables:

- **Device Security Modules (DSMs)**: Software/hardware on capturing devices that sign data at the source
- **Trusted Verifiers (TVs)**: Entities that vet and register DSMs
- **Immutable Records**: Blockchain-based storage of data hashes, signatures, and metadata

### PVB Features

- Cryptographic verification of data authenticity
- Immutable audit trails
- Decentralized trust through blockchain technology
- Support for off-chain data storage (IPFS, Arweave)
- RESTful API for integration with external systems

### PVB API Endpoints

- **Health Check**: `GET /api/pvb/health`
- **Verifier Registration**: `POST /api/pvb/verifiers`
- **Device Management**: `POST /api/pvb/verifiers/{address}/devices`
- **Data Submission**: `POST /api/pvb/data`
- **Data Verification**: `GET /api/pvb/data/{hash}/verify`

### Quick Start with PVB

1. **Start the blockchain service**:
   ```bash
   docker compose up -d ganache
   ```

2. **Deploy smart contracts**:
   ```bash
   python scripts/deploy_pvb_contracts.py
   ```

3. **Test the PVB API**:
   ```bash
   curl http://localhost:5000/api/pvb/health
   ```

For detailed PVB documentation, see [docs/PVB_Implementation_Guide.md](docs/PVB_Implementation_Guide.md).

## Security Notes

<!-- Critical security practices and considerations relevant to this project. -->
-   **Secret Management:** Never commit sensitive information like passwords, API keys, or `.env` files directly into the Git repository. Use `.gitignore` to prevent accidental commits.
-   **Production Secrets:** For production deployments, ensure secure secret management and proper environment variable configuration.
-   **PowerShell Execution Policy (Windows):** If using PowerShell scripts for setup or tasks, be mindful of the system's execution policy. Changes should be understood and potentially reverted if temporary. Apply the principle of least privilege.
