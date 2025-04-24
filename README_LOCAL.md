# Local Development Setup

This guide explains how to run the AIEthicsDash application locally using Docker Compose.

## Prerequisites

-   Docker installed
-   Docker Compose installed (usually included with Docker Desktop)
-   Git

## Setup Steps

1.  **Clone the Repository:**
    ```bash
    git clone <your-repository-url>
    cd AIEthicsDash
    ```

2.  **Configure Environment Variables:**
    * Copy the example environment file for the backend:
        ```bash
        cp backend/.env.example backend/.env
        ```
    * **Edit `backend/.env`:** Fill in your API keys for OpenAI, Anthropic, Gemini, and xAI (Grok). Set the desired default models for R1 (`DEFAULT_LLM_MODEL`) and R2 (`ANALYSIS_LLM_MODEL`). Set `MONGO_URI=mongodb://ai-mongo:27017/` and `MONGO_DB_NAME=ethics_db` (these match the `docker-compose.yml` service names).

3.  **Build Docker Images:**
    ```bash
    docker compose build
    ```
    This might take some time on the first run.

4.  **Run the Application:**
    ```bash
    docker compose up -d
    ```
    This starts all services (frontend, backend, mongo, db-init) in detached mode. The `db-init` service will run once to populate the database with initial memes.

5.  **Access the Application:**
    * **Frontend (React App):** Open your browser to `http://localhost:80` (or the port mapped for `ai-frontend`).
    * **Admin UI (Dash App):** Open your browser to `http://localhost:5000/dash/` (or the host port mapped to `ai-backend`'s port 5000, plus `/dash/`). *Note: This assumes the Dash admin UI is retained and served by the backend.*
    * **Backend API:** The API is available at `http://localhost:5000/api/`.

6.  **View Logs:**
    ```bash
    # View logs for all services
    docker compose logs -f

    # View logs for a specific service (e.g., backend)
    docker compose logs -f ai-backend
    ```

7.  **Stop the Application:**
    ```bash
    docker compose down
    ```
    Add `-v` if you want to remove the MongoDB data volume (`mongo_data`) as well: `docker compose down -v`.

## Troubleshooting

-   Ensure Docker Desktop is running.
-   Check logs (`docker compose logs -f <service_name>`) for errors.
-   Verify the `.env` file is correctly populated with API keys and the MongoDB URI.
-   Make sure ports 80 and 5000 (or your mapped ports) are not already in use on your host machine. 