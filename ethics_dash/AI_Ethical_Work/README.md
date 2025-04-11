# Ethical Review Tool

A web application designed to generate responses from various Large Language Models (LLMs) and subsequently analyze those responses based on a defined ethical ontology. Users can provide a prompt, select an LLM for the initial response (R1), and optionally choose a different LLM for the ethical analysis (R2). The application supports models from OpenAI, Google Gemini, and Anthropic.

## Features

*   **Prompt Input**: Text area for users to input their initial prompt (P1).
*   **LLM Selection (R1 & R2)**: Dropdowns allow users to select specific models from OpenAI, Gemini, and Anthropic for both the initial response generation (R1) and the ethical analysis (R2).
*   **API Configuration Override**: Optional input fields for users to provide specific API keys and API endpoint URLs for both R1 and R2 models, overriding the defaults set in environment variables.
*   **Ethical Analysis**: The generated response (R1) is analyzed by the selected R2 model using the principles defined in `backend/app/ontology.md`.
*   **Results Display**: Shows the original prompt, the models used, the initial response, the textual ethical analysis summary, and structured ethical scores (Deontology, Teleology, Areteology).
*   **Dockerized**: Fully containerized using Docker and Docker Compose for easy setup and deployment.

## Architecture

This application utilizes a two-tier architecture:

1.  **Backend API** (`backend/`): A Flask-based RESTful API responsible for:
    *   Receiving prompt analysis requests.
    *   Determining API configurations (keys, endpoints, models) based on user input or environment variables.
    *   Interacting with selected AI models (OpenAI, Gemini, Anthropic) via the `llm_interface.py` module.
    *   Performing ethical analysis using the `ontology.md` framework.
    *   Returning structured results (response, analysis, scores) to the frontend.
2.  **Frontend Web UI** (`frontend/`): A React-based single-page application providing:
    *   User interface for prompt entry and optional model/API configuration.
    *   Interaction with the backend API (`/api/analyze`).
    *   Dynamic display of generated responses and ethical analysis results.

## Directory Structure

```
TriangleEthic/                      # Project Root
├── backend/                    # Backend API service (Flask)
│   ├── app/
│   │   ├── modules/
│   │   │   └── llm_interface.py  # Handles actual API calls to LLMs
│   │   ├── __init__.py         # Flask app factory
│   │   ├── api.py              # API routes (e.g., /analyze)
│   │   └── ontology.md         # Ethical framework definitions
│   ├── wsgi.py                 # WSGI entry point for Gunicorn
│   ├── Dockerfile              # Backend container build definition
│   └── requirements.txt        # Python dependencies
├── frontend/                   # Frontend Web App (React)
│   ├── src/
│   │   ├── components/         # React UI components (PromptForm, Results, etc.)
│   │   ├── services/           # API communication layer (api.js)
│   │   ├── App.css             # Main application styles
│   │   ├── App.js              # Main App component
│   │   └── index.js            # React entry point
│   ├── public/                 # Static assets (index.html, etc.)
│   ├── Dockerfile              # Frontend container build definition (Nginx)
│   ├── nginx.conf              # Nginx configuration for serving React app
│   └── package.json            # Node.js dependencies
├── context/
│   └── prompts.txt             # Log of user prompts submitted via the UI
├── .env                        # Environment variables (API keys, defaults) - !! DO NOT COMMIT !!
├── .gitignore                  # Specifies intentionally untracked files
├── docker-compose.yml          # Defines and configures the Docker services (backend, frontend)
├── deploy_to_acr.ps1           # PowerShell script for deploying images to ACR - !! DO NOT COMMIT SENSITIVE DATA IF MODIFIED !!
├── LICENSE                     # Project License (MIT)
└── README.md                   # This file
```

## Getting Started

### Prerequisites

*   Docker and Docker Compose installed.
*   Azure CLI installed (optional, required for `deploy_to_acr.ps1` script).
*   API Keys for the LLM providers you intend to use (OpenAI, Google Gemini, Anthropic).

### Environment Setup

1.  **Clone the repository:**
    ```bash
    git clone <your-repository-url>
    cd TriangleEthic
    ```
2.  **Create Environment File:** Create a `.env` file in the project root directory. Copy the contents of `.env.example` (if provided) or add the following variables, replacing placeholders with your actual keys and desired defaults:

    ```dotenv
    # --- General API Keys (Used if specific ANALYSIS keys aren't set) ---
    OPENAI_API_KEY="YOUR_OPENAI_API_KEY_HERE"
    GEMINI_API_KEY="YOUR_GEMINI_API_KEY_HERE"
    ANTHROPIC_API_KEY="YOUR_ANTHROPIC_API_KEY_HERE"

    # --- Specific Keys for ANALYSIS LLM (Optional - overrides general keys) ---
    # ANALYSIS_OPENAI_API_KEY=
    # ANALYSIS_GEMINI_API_KEY=
    # ANALYSIS_ANTHROPIC_API_KEY=

    # --- Optional API Endpoints (Uncomment and set if using non-standard endpoints) ---
    # OPENAI_API_ENDPOINT=
    # GEMINI_API_ENDPOINT=https://generativelanguage.googleapis.com/v1beta
    # ANTHROPIC_API_ENDPOINT=https://api.anthropic.com/v1
    # ANALYSIS_OPENAI_API_ENDPOINT=
    # ANALYSIS_GEMINI_API_ENDPOINT=
    # ANALYSIS_ANTHROPIC_API_ENDPOINT=

    # --- Default Model Selections --- 
    # Set a default model for the initial response (R1). 
    # If unset, the backend might default to the first available model found.
    DEFAULT_LLM_MODEL="claude-3-sonnet-20240229" # Example: "gpt-4o", "gemini-1.5-pro-latest"

    # Set a default model for the ethical analysis response (R2).
    # This is REQUIRED if not provided dynamically by the frontend.
    ANALYSIS_LLM_MODEL="claude-3-sonnet-20240229" # Example

    # --- Optional Anthropic SDK Config --- 
    # Set the Anthropic API version if needed (defaults to 2023-06-01)
    # ANTHROPIC_API_VERSION="2023-06-01"
    ```

    **Important:** Ensure the `.env` file is listed in your `.gitignore` to avoid committing sensitive API keys.

### Running with Docker Compose

1.  **Build and Start Containers:** From the project root directory:
    ```bash
    docker-compose build # Optional: only needed if Dockerfiles change
    docker-compose up -d
    ```
    The `-d` flag runs the containers in detached mode (in the background).

2.  **Access the Application:**
    *   **Frontend UI:** Open your web browser to [http://localhost:80](http://localhost:80)
    *   Backend API (for direct testing, e.g., with Postman): `http://localhost:5000/api`

3.  **Stopping the Application:**
    ```bash
    docker-compose down
    ```

## Usage

1.  Navigate to the application URL (default: `http://localhost:80`).
2.  Enter your prompt in the main text area.
3.  (Optional) Expand the "Optional: Specify Models, Keys & Endpoints" section.
4.  (Optional) Select specific models for "Origin Model (R1)" and/or "Ethical Review Model (R2)" from the dropdowns. If left blank, the defaults from the `.env` file are used.
5.  (Optional) Enter an API Key and/or API Endpoint URL for R1 and/or R2 if you want to override the keys/endpoints configured via the `.env` file.
6.  Click "Generate & Analyze".
7.  View the results, including the initial response and the ethical analysis breakdown.

## Deployment to Azure Container Registry (ACR)

A PowerShell script (`deploy_to_acr.ps1`) is provided to automate building and pushing the Docker images to ACR using `az acr build`.

1.  Ensure Azure CLI is installed and you are logged in (`az login`).
2.  Set the correct Azure subscription (`az account set --subscription <sub_id>`).
3.  Run the script from PowerShell in the project root:
    ```powershell
    .\deploy_to_acr.ps1
    ```
4.  Enter the requested information (Subscription ID/Name, ACR Name, ACR Resource Group).

The script will use the `docker-compose.yml` file to build the images defined within it directly in ACR.

**Note:** This script is included in `.gitignore`. If you modify it to include sensitive information (like hardcoded subscription IDs or ACR names), ensure it is not committed to your repository.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

*   Utilizes APIs from OpenAI, Google Gemini, and Anthropic.
*   Built with Flask, React, Docker.

### Local Setup

1.  **Prerequisites:**
    *   Docker and Docker Compose
    *   Git
    *   API Keys for desired LLM providers (OpenAI, Anthropic, Gemini)

2.  **Clone the Repository:**
    ```bash
    git clone <your-repository-url>
    cd <repository-directory>
    ```

3.  **Configure Environment Variables:**
    *   Create a `.env` file in the project root by copying the example file:
      ```powershell
      Copy-Item .env.example .env
      ```
    *   **Important:** Open the newly created `.env` file and replace the placeholder values with your actual API keys. You **must** set a valid model name for `ANALYSIS_LLM_MODEL` (e.g., `"claude-3-sonnet-20240229"`). You can optionally set `DEFAULT_LLM_MODEL` for the default R1 model.
    *   The `.env` file is listed in `.gitignore` and should **never** be committed to the repository.

4.  **Build and Run Containers:**
    *   From the project root directory, run:
      ```powershell
      docker compose up -d --build
      ```
    *   This command builds the Docker images (if they don't exist or if code has changed) and starts the `backend` and `frontend` services in detached mode (`-d`).

5.  **Access the Application:**
    *   Open your web browser and navigate to `http://localhost:80` (or just `http://localhost`). 