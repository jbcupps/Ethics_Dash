#!/bin/bash

# Check if GitHub CLI is installed
if ! command -v gh &> /dev/null; then
    echo "GitHub CLI is not installed. Please install it first: https://cli.github.com/"
    exit 1
fi

# Check if user is logged in to GitHub
if ! gh auth status &> /dev/null; then
    echo "Please login to GitHub first using: gh auth login"
    exit 1
fi

# Get repository name
REPO_NAME=$(basename $(git rev-parse --show-toplevel))

# Function to securely set a secret
set_secret() {
    local secret_name=$1
    local prompt_message=$2
    local default_value=$3
    
    if [ -n "$default_value" ]; then
        read -p "$prompt_message [Press Enter to use default: $default_value]: " secret_value
        secret_value=${secret_value:-$default_value}
    else
        read -s -p "$prompt_message: " secret_value
        echo
    fi
    
    gh secret set "$secret_name" -R "$REPO_NAME" -b "$secret_value"
}

echo "Setting up GitHub secrets for $REPO_NAME..."

# Set ACR secrets
set_secret "ACR_REGISTRY" "Enter your Azure Container Registry URL (e.g., yourregistry.azurecr.io)"
set_secret "ACR_USERNAME" "Enter your ACR username"
set_secret "ACR_PASSWORD" "Enter your ACR password"

# Set API secrets
echo -e "\nSetting up API secrets (you can leave these empty for now and update them later):"
set_secret "API_KEY" "Enter your API key" "placeholder"
set_secret "API_SECRET" "Enter your API secret" "placeholder"
set_secret "API_ENDPOINT" "Enter your API endpoint URL" "https://api.example.com"
set_secret "API_VERSION" "Enter your API version" "v1"

# Set environment-specific secrets
echo -e "\nSetting up environment-specific secrets:"
set_secret "NODE_ENV" "Enter the environment (development/production)" "development"
set_secret "LOG_LEVEL" "Enter the log level (debug/info/warn/error)" "info"

echo -e "\nGitHub secrets have been set up successfully!"
echo "You can verify the secrets in your repository settings under 'Secrets and variables' -> 'Actions'"
echo "Note: You can update these secrets later using the GitHub CLI or web interface" 