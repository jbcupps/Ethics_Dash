#!/bin/bash
# Script to set up GitHub secrets for Ethics Dashboard

echo "Ethics Dashboard GitHub Secrets Setup"
echo "===================================="
echo ""
echo "This script will guide you through setting up the required API keys for deployment."
echo "You'll need to have the GitHub CLI (gh) installed and authenticated."
echo ""

# Check if gh CLI is installed
if ! command -v gh &> /dev/null; then
    echo "GitHub CLI (gh) is not installed or not in PATH."
    echo "Please install it from: https://cli.github.com/"
    exit 1
fi

# Check if logged in
if ! gh auth status &> /dev/null; then
    echo "You're not logged in to GitHub CLI."
    echo "Please run 'gh auth login' first."
    exit 1
fi

# Function to set secret with confirmation
set_secret() {
    local name=$1
    local description=$2
    
    echo ""
    echo "Setting up secret: $name"
    echo "$description"
    echo ""
    echo "Please enter the value (input will be hidden):"
    
    # Read secret value
    read -s value
    
    # Set the secret
    if [ -n "$value" ]; then
        echo "$value" | gh secret set "$name"
        echo "✓ Secret '$name' set successfully!"
    else
        echo "⚠️ No value provided for '$name'. Skipping."
    fi
}

# Set up the API keys
set_secret "OPENAI_API_KEY" "Your OpenAI API key (e.g., sk-...)"
set_secret "GEMINI_API_KEY" "Your Google Gemini API key"
set_secret "XAI_API_KEY" "Your xAI (Grok) API key (if available, otherwise you can skip)"

# Confirm results
echo ""
echo "GitHub secrets setup complete!"
echo "You can verify your secrets with: gh secret list"
echo ""
echo "If you need to update the workflow, edit .github/workflows/deploy-and-troubleshoot.yml"
echo "Then run the workflow from the GitHub Actions tab on your repository." 