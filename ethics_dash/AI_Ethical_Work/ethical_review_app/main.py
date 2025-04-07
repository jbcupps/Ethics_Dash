# Main application file for the Ethical Review App (Flask Web Interface)

import os
from typing import Tuple, Dict, Optional, List
from flask import Flask, render_template, request, flash, url_for, redirect
# Change absolute import to relative import
from ethical_review_app.modules.llm_interface import generate_response, perform_ethical_analysis

# --- Configuration Constants ---
ONTOLOGY_FILEPATH = "ethical_review_app/ontology.md"
PROMPT_LOG_FILEPATH = "context/prompts.txt" # Use relative path from workspace root

# Environment variable names
GEMINI_API_KEY_ENV = "GEMINI_API_KEY"
ANTHROPIC_API_KEY_ENV = "ANTHROPIC_API_KEY"
GEMINI_API_ENDPOINT_ENV = "GEMINI_API_ENDPOINT"
ANTHROPIC_API_ENDPOINT_ENV = "ANTHROPIC_API_ENDPOINT"

# --- Model Definitions ---
GEMINI_MODELS: List[str] = [
    "gemini-1.5-pro-latest",
    "gemini-1.5-flash-latest",
    "gemini-1.0-pro",
    # Add other relevant Gemini models as needed
]

ANTHROPIC_MODELS: List[str] = [
    "claude-3-opus-20240229",
    "claude-3-sonnet-20240229",
    "claude-3-haiku-20240307",
    # Add other relevant Anthropic models as needed
]

ALL_MODELS: List[str] = GEMINI_MODELS + ANTHROPIC_MODELS

# --- Flask App Initialization ---
app = Flask(__name__)
app.secret_key = os.urandom(24) # Needed for flashing messages

# --- Helper Functions ---

def load_ontology(filepath: str = ONTOLOGY_FILEPATH) -> Optional[str]:
    """Loads the ethical ontology text from the specified file.

    Args:
        filepath: Path to the ontology file.

    Returns:
        The ontology text as a string, or None if an error occurs.
    """
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            return f.read()
    except FileNotFoundError:
        app.logger.error(f"Ontology file not found at {filepath}")
        return None
    except IOError as e: # More specific exception for file I/O
        app.logger.error(f"Failed to read ontology file {filepath}: {e}")
        return None
    except Exception as e: # Catch unexpected errors
        app.logger.error(f"An unexpected error occurred reading ontology {filepath}: {e}")
        return None

def log_prompt(prompt: str, model_name: str, filepath: str = PROMPT_LOG_FILEPATH):
    """Appends the given prompt and selected model to the log file.

    Args:
        prompt: The user's input prompt.
        model_name: The selected LLM model.
        filepath: Path to the log file.
    """
    try:
        # Ensure the directory exists
        log_dir = os.path.dirname(filepath)
        if log_dir and not os.path.exists(log_dir):
             os.makedirs(log_dir, exist_ok=True)
             app.logger.info(f"Created log directory: {log_dir}")

        with open(filepath, 'a', encoding='utf-8') as f:
            f.write(f"--- User Prompt (Model: {model_name}) ---\n{prompt}\n\n")
        app.logger.debug(f"Logged prompt for model {model_name} to {filepath}")
    except IOError as e: # More specific exception for file I/O
        app.logger.error(f"Failed to log prompt to {filepath}: {e}")
    except Exception as e: # Catch unexpected errors
        app.logger.error(f"An unexpected error occurred logging prompt to {filepath}: {e}")

def _get_api_config(selected_model: str, form_api_key: Optional[str]) -> Tuple[Optional[str], Optional[str], str]:
    """Determines the API key, endpoint, and source based on model and form input.

    Args:
        selected_model: The name of the selected LLM.
        form_api_key: API key optionally provided via the web form.

    Returns:
        A tuple containing: (api_key, api_endpoint, key_source_message).
        Returns (None, None, error_message) if the key cannot be determined.
    """
    api_key: Optional[str] = None
    api_endpoint: Optional[str] = None
    key_source: str = ""
    api_key_name: str = "" # For user messages
    env_var_key: str = "" # Actual env var name
    env_var_endpoint: str = ""

    # Determine required env var names based on model
    if selected_model in GEMINI_MODELS:
        api_key_name = "Gemini"
        env_var_key = GEMINI_API_KEY_ENV
        env_var_endpoint = GEMINI_API_ENDPOINT_ENV
    elif selected_model in ANTHROPIC_MODELS:
        api_key_name = "Anthropic"
        env_var_key = ANTHROPIC_API_KEY_ENV
        env_var_endpoint = ANTHROPIC_API_ENDPOINT_ENV
    else:
        # Should be caught by earlier validation, but good practice
        return None, None, "Invalid model specified for API config."

    # Prioritize form input for the key
    if form_api_key:
        api_key = form_api_key
        key_source = "form input"
    else:
        # Fallback to environment variable for the key
        api_key = os.getenv(env_var_key)
        key_source = f"environment variable ({env_var_key})"

    # Get endpoint from environment variable regardless of key source
    api_endpoint = os.getenv(env_var_endpoint)
    endpoint_source = f"environment variable ({env_var_endpoint})"

    # Validate API Key
    if not api_key:
        error_msg = f"API Key for {api_key_name} not provided via form or {env_var_key} env var."
        return None, None, error_msg
    else:
        app.logger.info(f"Using API key from: {key_source}")

    # Log endpoint status (optional but helpful)
    if not api_endpoint:
        app.logger.warning(f"API Endpoint for {api_key_name} not found via {env_var_endpoint}. Using library default if applicable.")
    else:
        app.logger.info(f"Using API endpoint from: {endpoint_source}")

    return api_key, api_endpoint, f"Using API key from {key_source}" # Return success message for potential future use

def _handle_llm_calls(prompt: str, api_key: str, selected_model: str, api_endpoint: Optional[str], ontology_text: str) -> Tuple[Optional[str], Optional[str]]:
    """Handles the calls to generate response (R1) and perform analysis (R2).

    Args:
        prompt: The user's input prompt.
        api_key: The API key to use.
        selected_model: The LLM model name.
        api_endpoint: The API endpoint to use (optional).
        ontology_text: The ethical ontology text.

    Returns:
        A tuple containing: (initial_response, ethical_analysis_response).
        Values can be None if generation/analysis fails or is blocked.
    """
    initial_response: Optional[str] = None
    ethical_analysis_response: Optional[str] = None

    try:
        # --- Generate Initial Response (R1) ---
        app.logger.info(f"Generating initial response (R1) using {selected_model}...")
        initial_response = generate_response(prompt, api_key, selected_model, api_endpoint=api_endpoint)

        if not initial_response:
            r1_error = f"Failed to generate initial response (R1) using {selected_model}. Model block or API error likely."
            initial_response = "[No response generated or content blocked]" # Provide placeholder
            flash(r1_error, 'warning')
            app.logger.warning(f"{r1_error} Prompt: {prompt[:100]}...") # Log truncated prompt
        else:
            app.logger.info("R1 generated successfully.")

        # --- Perform Ethical Analysis (R2) ---
        app.logger.info(f"Performing ethical analysis (R2) using {selected_model}...")
        # Ensure r1 passed to analysis is always a string
        r1_for_analysis = initial_response if initial_response else "[No initial response was generated or it was blocked]"

        ethical_analysis_response = perform_ethical_analysis(
            prompt, r1_for_analysis, ontology_text, api_key, selected_model, api_endpoint=api_endpoint
        )

        if not ethical_analysis_response:
            r2_error = f"Failed to perform ethical analysis (R2) using {selected_model}. Model block or API error likely."
            ethical_analysis_response = "[No analysis generated or content blocked]" # Provide placeholder
            flash(r2_error, 'warning')
            app.logger.warning(f"{r2_error} Prompt: {prompt[:100]}...")
        else:
            app.logger.info("R2 generated successfully.")

    except Exception as e:
        # Catch unexpected errors during LLM calls
        llm_error = f"An unexpected error occurred during LLM interaction: {e}"
        flash(llm_error, 'error')
        app.logger.error(llm_error, exc_info=True) # Log with traceback
        # Ensure return values reflect failure
        initial_response = initial_response if initial_response else "[Error during R1 generation]"
        ethical_analysis_response = "[Error during R2 generation]"

    return initial_response, ethical_analysis_response

# --- Flask Routes ---

@app.route('/', methods=['GET', 'POST'])
def index():
    """Handles the main page request (GET) and form submission (POST).

    On POST, validates input, retrieves API config, calls LLM functions,
    and renders the results.
    On GET, displays the initial form.
    """
    # Initialize variables for template context
    context: Dict[str, Optional[str]] = {
        "prompt_text": None,
        "initial_response": None,
        "ethical_analysis_response": None,
        "error": None,
        "selected_model": ALL_MODELS[0], # Default model
        "form_api_key": None # Keep API key field blank on render
    }
    context["models"] = ALL_MODELS # Always pass models

    if request.method == 'POST':
        # --- Get Form Data ---
        prompt_text = request.form.get('prompt')
        selected_model = request.form.get('model_select', ALL_MODELS[0])
        form_api_key = request.form.get('api_key_input') # User override

        # Persist entered prompt and model selection on error/reload
        context["prompt_text"] = prompt_text
        context["selected_model"] = selected_model
        # Don't persist API key in the input field for security

        # --- Validate Input ---
        if not prompt_text:
            flash("Please enter a prompt.", "error")
            return render_template('index.html', **context)

        if selected_model not in ALL_MODELS:
            flash("Invalid model selected.", "error")
            return render_template('index.html', **context)

        # --- Log the User Prompt ---
        log_prompt(prompt_text, selected_model)

        # --- Get API Configuration ---
        api_key, api_endpoint, config_message = _get_api_config(selected_model, form_api_key)

        if not api_key:
            # _get_api_config returns error message if key is missing
            flash(config_message, 'error')
            app.logger.error(config_message)
            return render_template('index.html', **context)

        # --- Load Ethical Ontology ---
        ontology_text = load_ontology()
        if not ontology_text:
            error_msg = "Server error: Could not load the ethical ontology."
            flash(error_msg, 'error')
            app.logger.error(error_msg)
            # Ontology is critical, don't proceed without it
            return render_template('index.html', **context)

        # --- Perform LLM Calls ---
        initial_response, ethical_analysis_response = _handle_llm_calls(
            prompt_text, api_key, selected_model, api_endpoint, ontology_text
        )

        # Update context with results
        context["initial_response"] = initial_response
        context["ethical_analysis_response"] = ethical_analysis_response

        # Note: Errors during LLM calls are flashed within _handle_llm_calls

    # --- Render Template ---
    # Handles both GET requests and the final rendering after POST processing
    return render_template('index.html', **context)


# --- Main Execution Guard ---

def _check_ontology_at_startup():
    """Checks for the ontology file existence at application start."""
    if not os.path.exists(ONTOLOGY_FILEPATH):
        # Use app logger if available, otherwise print
        log_func = app.logger.warning if app else print
        log_func(f"WARNING: Ontology file not found at {ONTOLOGY_FILEPATH}")
        log_func("Ethical analysis features may be limited or unavailable.")

if __name__ == "__main__":
    _check_ontology_at_startup()
    # Use debug=False in a production environment for security and performance
    # Consider using a production-ready WSGI server like Gunicorn or uWSGI
    # behind a reverse proxy (e.g., Nginx) instead of app.run() for production.
    app.run(debug=True, host='0.0.0.0', port=5000) # Make accessible within Docker
