"""API routes for the ethical review backend"""

import os
from typing import Dict, Any, Optional, Tuple
from flask import Blueprint, request, jsonify, current_app
import re # Import regex module for parsing
import json # Import JSON module for parsing
import logging # Import logging
from json import JSONDecodeError

from backend.app.modules.llm_interface import generate_response, perform_ethical_analysis

# --- Blueprint Definition ---
api_bp = Blueprint('api', __name__, url_prefix='/api')

# --- Setup Logger ---
logger = logging.getLogger(__name__)
# Assuming basicConfig is called in app __init__ or wsgi.py

# --- Constants ---
ONTOLOGY_FILEPATH = os.path.join(os.path.dirname(__file__), "ontology.md")
PROMPT_LOG_FILEPATH = "context/prompts.txt"

# Environment variable names (Added OpenAI)
OPENAI_API_KEY_ENV = "OPENAI_API_KEY"
GEMINI_API_KEY_ENV = "GEMINI_API_KEY"
ANTHROPIC_API_KEY_ENV = "ANTHROPIC_API_KEY"
OPENAI_API_ENDPOINT_ENV = "OPENAI_API_ENDPOINT"
GEMINI_API_ENDPOINT_ENV = "GEMINI_API_ENDPOINT"
ANTHROPIC_API_ENDPOINT_ENV = "ANTHROPIC_API_ENDPOINT"
DEFAULT_LLM_MODEL_ENV = "DEFAULT_LLM_MODEL"

# Environment variables for the Analysis LLM (Added OpenAI)
ANALYSIS_LLM_MODEL_ENV = "ANALYSIS_LLM_MODEL"
ANALYSIS_OPENAI_API_KEY_ENV = "ANALYSIS_OPENAI_API_KEY"
ANALYSIS_GEMINI_API_KEY_ENV = "ANALYSIS_GEMINI_API_KEY"
ANALYSIS_ANTHROPIC_API_KEY_ENV = "ANALYSIS_ANTHROPIC_API_KEY"
ANALYSIS_OPENAI_API_ENDPOINT_ENV = "ANALYSIS_OPENAI_API_ENDPOINT"
ANALYSIS_GEMINI_API_ENDPOINT_ENV = "ANALYSIS_GEMINI_API_ENDPOINT"
ANALYSIS_ANTHROPIC_API_ENDPOINT_ENV = "ANALYSIS_ANTHROPIC_API_ENDPOINT"

# --- Model Definitions ---
OPENAI_MODELS = [
    "gpt-4o",
    "gpt-4-turbo",
    "gpt-3.5-turbo"
]

GEMINI_MODELS = [
    "gemini-1.5-pro-latest",
    "gemini-1.5-flash-latest",
    "gemini-1.0-pro",
]

ANTHROPIC_MODELS = [
    "claude-3-opus-20240229",
    "claude-3-sonnet-20240229",
    "claude-3-haiku-20240307",
]

ALL_MODELS = OPENAI_MODELS + GEMINI_MODELS + ANTHROPIC_MODELS

# --- Helper Functions ---

def load_ontology(filepath: str = ONTOLOGY_FILEPATH) -> Optional[str]:
    """Loads the ethical ontology text from the specified file."""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            return f.read()
    except Exception as e:
        logger.error(f"Error loading ontology: {e}")
        return None

def log_prompt(prompt: str, model_name: str, filepath: str = PROMPT_LOG_FILEPATH):
    """Appends the given prompt and selected model to the log file."""
    try:
        # Ensure the directory exists
        log_dir = os.path.dirname(filepath)
        if log_dir and not os.path.exists(log_dir):
             os.makedirs(log_dir, exist_ok=True)
             logger.info(f"Created log directory: {log_dir}")

        with open(filepath, 'a', encoding='utf-8') as f:
            f.write(f"--- User Prompt (Model: {model_name}) ---\n{prompt}\n\n")
    except Exception as e:
        logger.error(f"Error logging prompt: {e}")

def _get_api_config(selected_model: str, 
                    form_api_key: Optional[str],
                    form_api_endpoint: Optional[str]) -> Dict[str, Any]:
    """
    Determines the API key and endpoint for the R1 model.
    Prioritizes form inputs (key, endpoint), otherwise falls back to environment variables.
    """
    api_key = None
    api_endpoint = None
    error = None
    key_source = "Environment Variable"
    endpoint_source = "Environment Variable"
    
    logger.info(f"_get_api_config: Fetching config for selected_model: {selected_model}")
    logger.info(f"_get_api_config: Received form_api_key: {'Provided' if form_api_key else 'Not Provided'}")
    logger.info(f"_get_api_config: Received form_api_endpoint: {'Provided' if form_api_endpoint else 'Not Provided'}")

    # Determine API provider and corresponding ENV VAR names
    env_var_key = None
    env_var_endpoint = None
    api_key_name = f"Origin ({selected_model})" # Default name

    if selected_model in OPENAI_MODELS:
        api_key_name = "Origin OpenAI"
        env_var_key = OPENAI_API_KEY_ENV
        env_var_endpoint = OPENAI_API_ENDPOINT_ENV
    elif selected_model in GEMINI_MODELS:
        api_key_name = "Origin Gemini"
        env_var_key = GEMINI_API_KEY_ENV
        env_var_endpoint = GEMINI_API_ENDPOINT_ENV
    elif selected_model in ANTHROPIC_MODELS:
        api_key_name = "Origin Anthropic"
        env_var_key = ANTHROPIC_API_KEY_ENV
        env_var_endpoint = ANTHROPIC_API_ENDPOINT_ENV
    else:
        # This case should ideally not be reached if model comes from dropdown
        # If we allow custom model names later, this logic might need adjustment
        logger.warning(f"_get_api_config: Unknown model type '{selected_model}' encountered. Relying on form inputs only for key/endpoint.")
        # No known env vars to check

    # 1. Prioritize API key provided in the form
    if form_api_key and isinstance(form_api_key, str) and form_api_key.strip():
        api_key = form_api_key.strip()
        key_source = "User Input"
        logger.info(f"_get_api_config: Using API key provided via form for {api_key_name}.")
    # 2. Fallback to environment variable if form key wasn't provided AND we know the variable name
    elif env_var_key:
        api_key = os.getenv(env_var_key)
        if api_key:
             key_source = f"Environment Variable ({env_var_key})"
             logger.info(f"_get_api_config: Using API key from env var {env_var_key} for {api_key_name}.")

    # 3. Prioritize API endpoint provided in the form
    if form_api_endpoint and isinstance(form_api_endpoint, str) and form_api_endpoint.strip():
        # Basic validation: Check if it looks somewhat like a URL
        if form_api_endpoint.startswith("http://") or form_api_endpoint.startswith("https://"):
            api_endpoint = form_api_endpoint.strip()
            endpoint_source = "User Input"
            logger.info(f"_get_api_config: Using API endpoint provided via form: {api_endpoint}")
        else:
            logger.warning(f"_get_api_config: Ignoring invalid form_api_endpoint (doesn't start with http/https): {form_api_endpoint}")
            # Keep api_endpoint as None to fallback to env var or default
    
    # 4. Fallback to environment variable endpoint if form endpoint wasn't provided/valid AND we know the variable name
    if not api_endpoint and env_var_endpoint: 
        env_endpoint_val = os.getenv(env_var_endpoint)
        if env_endpoint_val:
            api_endpoint = env_endpoint_val
            endpoint_source = f"Environment Variable ({env_var_endpoint})"
            logger.info(f"_get_api_config: Using API endpoint from env var {env_var_endpoint}: {api_endpoint}")

    # 5. Validate that *some* API Key was found
    if not api_key:
        if env_var_key: # If it was a known model type
            error = f"API Key for {api_key_name} not found. Provide one in the form or set the {env_var_key} environment variable."
        else: # Unknown model type
             error = f"API Key for model '{selected_model}' was not provided in the form or found in environment."
        logger.error(error)

    # Log final sources
    if not error:
        logger.info(f"_get_api_config: Final Key Source: {key_source}, Endpoint Source: {endpoint_source} for {selected_model}")
        
    return {
        "api_key": api_key,
        "api_endpoint": api_endpoint,
        "error": error
    }

def _get_analysis_api_config(selected_analysis_model: Optional[str] = None, 
                             form_analysis_api_key: Optional[str] = None, 
                             form_analysis_api_endpoint: Optional[str] = None) -> Dict[str, Any]:
    """
    Determines the API key, model, and endpoint for the Analysis LLM.
    Uses selected_analysis_model or falls back to ANALYSIS_LLM_MODEL_ENV.
    Prioritizes form inputs (key, endpoint), then specific env vars, then general env vars.
    """
    analysis_model = selected_analysis_model
    key_source = "Environment Variable"
    endpoint_source = "Environment Variable"

    # --- Determine Analysis Model --- 
    if not analysis_model or analysis_model not in ALL_MODELS:
        if selected_analysis_model and selected_analysis_model not in ALL_MODELS:
             logger.warning(f"_get_analysis_api_config: Invalid analysis model selected ('{selected_analysis_model}'). Falling back to environment default.")
        default_analysis_model_env = os.getenv(ANALYSIS_LLM_MODEL_ENV)
        if not default_analysis_model_env or default_analysis_model_env not in ALL_MODELS:
            error_msg = f"Analysis LLM model is not configured correctly. Neither selected ('{selected_analysis_model}') nor default env var {ANALYSIS_LLM_MODEL_ENV} ('{default_analysis_model_env}') are valid."
            logger.error(error_msg)
            return {"error": error_msg, "model": None, "api_key": None, "api_endpoint": None}
        analysis_model = default_analysis_model_env
        logger.info(f"_get_analysis_api_config: Using default analysis model from env var {ANALYSIS_LLM_MODEL_ENV}: {analysis_model}")
    else:
         logger.info(f"_get_analysis_api_config: Using user-selected analysis model: {analysis_model}")

    # --- Determine API Key & Endpoint --- 
    api_key = None
    api_endpoint = None
    error = None

    # Determine relevant env var names based on the *determined* analysis_model
    specific_key_env = None
    fallback_key_env = None
    specific_endpoint_env = None
    fallback_endpoint_env = None
    api_key_name = f"Analysis ({analysis_model})"
    
    if analysis_model in OPENAI_MODELS:
        api_key_name = "Analysis OpenAI"
        specific_key_env = ANALYSIS_OPENAI_API_KEY_ENV
        fallback_key_env = OPENAI_API_KEY_ENV
        specific_endpoint_env = ANALYSIS_OPENAI_API_ENDPOINT_ENV
        fallback_endpoint_env = OPENAI_API_ENDPOINT_ENV
    elif analysis_model in GEMINI_MODELS:
        api_key_name = "Analysis Gemini"
        specific_key_env = ANALYSIS_GEMINI_API_KEY_ENV
        fallback_key_env = GEMINI_API_KEY_ENV
        specific_endpoint_env = ANALYSIS_GEMINI_API_ENDPOINT_ENV
        fallback_endpoint_env = GEMINI_API_ENDPOINT_ENV
    elif analysis_model in ANTHROPIC_MODELS:
        api_key_name = "Analysis Anthropic"
        specific_key_env = ANALYSIS_ANTHROPIC_API_KEY_ENV
        fallback_key_env = ANTHROPIC_API_KEY_ENV
        specific_endpoint_env = ANALYSIS_ANTHROPIC_API_ENDPOINT_ENV
        fallback_endpoint_env = ANTHROPIC_API_ENDPOINT_ENV
    # No else needed as model validity is checked above

    # 1. Prioritize API key provided in the form
    if form_analysis_api_key and isinstance(form_analysis_api_key, str) and form_analysis_api_key.strip():
        api_key = form_analysis_api_key.strip()
        key_source = "User Input"
        logger.info(f"_get_analysis_api_config: Using API key provided via form for {api_key_name}.")
    # 2. Fallback to environment variables if form key wasn't provided
    else:
        # Check specific analysis key first, then standard key
        if specific_key_env:
            api_key = os.getenv(specific_key_env)
            if api_key:
                key_source = f"Environment Variable ({specific_key_env})"
        if not api_key and fallback_key_env: # If specific key not found or doesn't exist, try fallback
            api_key = os.getenv(fallback_key_env)
            if api_key:
                 key_source = f"Environment Variable ({fallback_key_env})"
        
        if api_key:
            logger.info(f"_get_analysis_api_config: Using API key from {key_source} for {api_key_name}.")

    # 3. Prioritize API endpoint provided in the form
    if form_analysis_api_endpoint and isinstance(form_analysis_api_endpoint, str) and form_analysis_api_endpoint.strip():
        if form_analysis_api_endpoint.startswith("http://") or form_analysis_api_endpoint.startswith("https://"):
            api_endpoint = form_analysis_api_endpoint.strip()
            endpoint_source = "User Input"
            logger.info(f"_get_analysis_api_config: Using API endpoint provided via form: {api_endpoint}")
        else:
            logger.warning(f"_get_analysis_api_config: Ignoring invalid form_analysis_api_endpoint: {form_analysis_api_endpoint}")
    
    # 4. Fallback to environment variable endpoint if form endpoint wasn't provided/valid
    if not api_endpoint:
        # Check specific analysis endpoint first, then standard endpoint
        if specific_endpoint_env:
            env_endpoint_val = os.getenv(specific_endpoint_env)
            if env_endpoint_val:
                api_endpoint = env_endpoint_val
                endpoint_source = f"Environment Variable ({specific_endpoint_env})"
        if not api_endpoint and fallback_endpoint_env: # If specific endpoint not found or doesn't exist, try fallback
            env_endpoint_val = os.getenv(fallback_endpoint_env)
            if env_endpoint_val:
                api_endpoint = env_endpoint_val
                endpoint_source = f"Environment Variable ({fallback_endpoint_env})"
        
        if api_endpoint:
             logger.info(f"_get_analysis_api_config: Using API endpoint from {endpoint_source}: {api_endpoint}")

    # 5. Validate that *some* API Key was found
    if not api_key:
        error_env_vars = f"{specific_key_env} or {fallback_key_env}" if specific_key_env and fallback_key_env else (specific_key_env or fallback_key_env or "relevant environment variables")
        error = f"API Key for {api_key_name} model '{analysis_model}' not found. Provide one in the form or set {error_env_vars}."
        logger.error(error)
        return {"error": error, "model": analysis_model, "api_key": None, "api_endpoint": api_endpoint}
    
    # Log final sources
    logger.info(f"_get_analysis_api_config: Final Key Source: {key_source}, Endpoint Source: {endpoint_source} for {analysis_model}")

    return {
        "model": analysis_model,
        "api_key": api_key,
        "api_endpoint": api_endpoint,
        "error": None
    }

def _parse_ethical_analysis(analysis_text: str) -> Tuple[str, Optional[Dict[str, Any]]]:
    """Parses the LLM's ethical analysis response, expecting a single JSON object.

    Args:
        analysis_text: The raw text response from the analysis LLM.

    Returns:
        A tuple containing:
        - The extracted textual summary (str).
        - The extracted scores JSON (dict), or None if parsing fails or keys are missing.
    """
    if not analysis_text or analysis_text == "[No analysis generated or content blocked]":
        current_app.logger.warning("Ethical analysis text was empty or indicated generation failure.")
        return analysis_text if analysis_text else "Analysis not generated.", None

    try:
        # Attempt to parse the entire response as a single JSON object
        parsed_data = json.loads(analysis_text)

        # Validate the structure and extract keys
        if not isinstance(parsed_data, dict):
             current_app.logger.error(f"Parsed analysis is not a dictionary: {type(parsed_data)}")
             return "Error: Analysis response was not a valid JSON object.", None

        summary = parsed_data.get("summary_text")
        scores = parsed_data.get("scores_json")

        # Check if required keys are present and summary is a string
        if summary is None or scores is None:
            missing_keys = []
            if summary is None: missing_keys.append("summary_text")
            if scores is None: missing_keys.append("scores_json")
            current_app.logger.error(f"Parsed analysis JSON is missing required keys: {missing_keys}. Got keys: {list(parsed_data.keys())}")
            return "Error: Analysis JSON missing required fields.", None

        if not isinstance(summary, str):
             current_app.logger.error(f"Parsed analysis 'summary_text' is not a string: {type(summary)}")
             # Still return the scores if they look ok, but provide an error summary
             summary = f"Error: Invalid summary format received (type: {type(summary)})."
             # Ensure scores is at least a dict, otherwise nullify it too
             if not isinstance(scores, dict):
                 current_app.logger.error(f"Parsed analysis 'scores_json' is not a dictionary: {type(scores)}")
                 scores = None

        # Basic check if scores look like a dictionary (further validation could be added)
        elif not isinstance(scores, dict):
             current_app.logger.error(f"Parsed analysis 'scores_json' is not a dictionary: {type(scores)}")
             return summary, None # Return valid summary, but no scores

        current_app.logger.info("Successfully parsed ethical analysis JSON.")
        return summary, scores

    except JSONDecodeError as e:
        current_app.logger.error(f"Failed to decode analysis response as JSON: {e}")
        current_app.logger.debug(f"Raw analysis text that failed parsing:\n{analysis_text}")
        # Try to extract something meaningful as a fallback, or return a generic error
        error_summary = "Error: Could not parse analysis response from the LLM. It was not valid JSON."
        # Optionally, you could try regex to find the *intended* summary if the LLM failed formatting
        # For simplicity, just return the error.
        return error_summary, None
    except Exception as e:
        # Catch any other unexpected errors during parsing/validation
        current_app.logger.error(f"Unexpected error parsing ethical analysis: {e}", exc_info=True)
        return "Error: An unexpected error occurred while processing the analysis response.", None

# --- Private Helpers for /analyze Route ---

def _validate_analyze_request(data: Optional[Dict[str, Any]]) -> Tuple[Optional[Dict], Optional[int]]:
    """Validates the incoming request data for the /analyze endpoint."""
    if not data:
        return {"error": "No JSON data received"}, 400
    
    prompt = data.get('prompt')
    if not prompt or not isinstance(prompt, str) or not prompt.strip():
        return {"error": "Invalid or missing 'prompt' provided"}, 400

    origin_model = data.get('origin_model')
    analysis_model = data.get('analysis_model')
    origin_api_key = data.get('origin_api_key')
    analysis_api_key = data.get('analysis_api_key')
    origin_api_endpoint = data.get('origin_api_endpoint') # Added
    analysis_api_endpoint = data.get('analysis_api_endpoint') # Added

    # Validate models (ensure they are in ALL_MODELS if provided, as they come from dropdown)
    if origin_model is not None:
        if not isinstance(origin_model, str) or not origin_model.strip():
             return {"error": "Optional 'origin_model' must be a non-empty string."}, 400
        if origin_model not in ALL_MODELS:
             return {"error": f"Optional 'origin_model' must be one of the supported models: {', '.join(ALL_MODELS)}"}, 400
             
    if analysis_model is not None:
        if not isinstance(analysis_model, str) or not analysis_model.strip():
            return {"error": "Optional 'analysis_model' must be a non-empty string."}, 400
        if analysis_model not in ALL_MODELS:
            return {"error": f"Optional 'analysis_model' must be one of the supported models: {', '.join(ALL_MODELS)}"}, 400
            
    # Validate API keys (must be non-empty string if provided)
    if origin_api_key is not None and (not isinstance(origin_api_key, str) or not origin_api_key.strip()):
         return {"error": "Optional 'origin_api_key' must be a non-empty string."}, 400
    if analysis_api_key is not None and (not isinstance(analysis_api_key, str) or not analysis_api_key.strip()):
         return {"error": "Optional 'analysis_api_key' must be a non-empty string."}, 400
         
    # Validate API endpoints (must look like URL if provided)
    if origin_api_endpoint is not None:
        if not isinstance(origin_api_endpoint, str) or not origin_api_endpoint.strip():
             return {"error": "Optional 'origin_api_endpoint' must be a non-empty string."}, 400
        if not origin_api_endpoint.startswith("http://") and not origin_api_endpoint.startswith("https://"):
             return {"error": "Optional 'origin_api_endpoint' must be a valid URL (starting with http:// or https://)."}, 400
             
    if analysis_api_endpoint is not None:
        if not isinstance(analysis_api_endpoint, str) or not analysis_api_endpoint.strip():
             return {"error": "Optional 'analysis_api_endpoint' must be a non-empty string."}, 400
        if not analysis_api_endpoint.startswith("http://") and not analysis_api_endpoint.startswith("https://"):
             return {"error": "Optional 'analysis_api_endpoint' must be a valid URL (starting with http:// or https://)."}, 400

    # Removed custom model check as origin_model is now from dropdown

    return None, None # No error

def _process_analysis_request(
    prompt: str,
    r1_model_to_use: str, # Pass the determined R1 model
    initial_config: Dict[str, Any],
    analysis_config: Dict[str, Any],
    ontology_text: str
) -> Tuple[Optional[Dict], Optional[int]]:
    """Handles generating R1, performing R2, and parsing results."""

    logger.info(f"_process_analysis_request: Using R1 model: {r1_model_to_use}")
    logger.info(f"_process_analysis_request: Using R2 model: {analysis_config.get('model')}")

    # Initialize results
    response_payload = {
        "prompt": prompt,
        "r1_model": r1_model_to_use,
        "r2_model": analysis_config.get('model'),
        "initial_response": None,
        "analysis_summary": None,
        "ethical_scores": None,
        "error": None
    }

    try:
        # --- Generate Initial Response (R1) ---
        logger.info(f"Generating initial response (R1) with model: {r1_model_to_use}")
        initial_response = generate_response(
            prompt=prompt,
            api_key=initial_config['api_key'],
            model_name=r1_model_to_use,
            api_endpoint=initial_config.get('api_endpoint')
        )
        response_payload["initial_response"] = initial_response

        if not initial_response:
            # Even if R1 fails/is blocked, we might still try R2 analysis
            logger.error(f"Failed to generate initial response (R1) from LLM {r1_model_to_use}. Check LLM interface logs.")
            initial_response = "[No response generated or content blocked]" # Provide placeholder
            # response_payload["error"] = f"Failed to generate response (R1) from {r1_model_to_use}."
            # return response_payload, 500 # Optionally stop here

        # --- Perform Ethical Analysis (R2) ---
        logger.info(f"Performing analysis (R2) with model: {analysis_config.get('model')}")
        # Ensure R1 passed to analysis is always a string
        r1_for_analysis = initial_response if initial_response else "[No initial response was generated or it was blocked]"

        # Combine ontology and db context if needed (adjust based on llm_interface)
        # For now, context isn't explicitly used by the updated perform_ethical_analysis
        analysis_context = {"ontology": ontology_text, "db": current_app.db} 

        raw_ethical_analysis_result = perform_ethical_analysis(
            prompt=prompt,                   # Corrected keyword
            initial_response=r1_for_analysis,# Corrected keyword
            analysis_model=analysis_config['model'], # Corrected keyword
            api_config=analysis_config,      # Pass the whole config dict
            context=analysis_context         # Pass context dictionary (optional for now)
        )

        # --- Process R2 Result ---
        # The function now returns the parsed dict or None
        if not raw_ethical_analysis_result:
            logger.error(f"Ethical analysis (R2) failed or returned no result for model {analysis_config.get('model')}. Check LLM interface logs.")
            # Fix: Ensure existing error is treated as empty string if None
            existing_error = response_payload.get("error", "") or ""
            response_payload["error"] = existing_error + f" Failed to generate analysis (R2) from {analysis_config.get('model')}."
            response_payload["analysis_summary"] = "[No analysis generated or content blocked]"
            response_payload["ethical_scores"] = None # Ensure scores are None on failure
        else:
            # Result should already be the parsed dictionary { "summary_text": ..., "scores_json": ... }
            response_payload["analysis_summary"] = raw_ethical_analysis_result.get("summary_text", "[Analysis summary missing]")
            response_payload["ethical_scores"] = raw_ethical_analysis_result.get("scores_json") # This is the nested scores object
            logger.info("Analysis completed and R2 result processed.")

        return response_payload, 200 # Success (even if parts failed, we have a payload)

    except Exception as e:
        logger.error(f"Error processing analysis request: {e}", exc_info=True)
        # Fix for potential NoneType error
        existing_error = response_payload.get("error", "") or ""
        response_payload["error"] = existing_error + f" Internal server error: {e}"
        return response_payload, 500 # Full failure

# --- API Routes ---

@api_bp.route('/models', methods=['GET'])
def get_models():
    """Return the list of available models"""
    valid_models = [model for model in ALL_MODELS if isinstance(model, str) and model]
    return jsonify({
        "models": valid_models
    })

@api_bp.route('/analyze', methods=['POST'])
def analyze():
    """Generate a response and ethical analysis for the given prompt"""
    data = request.get_json()
    
    # 1. Validate Request Data (models, keys, endpoints)
    validation_error, status_code = _validate_analyze_request(data)
    if validation_error:
        logger.warning(f"analyze: Request validation failed - {status_code}: {validation_error.get('error')}")
        return jsonify(validation_error), status_code

    prompt = data.get('prompt')
    origin_model_input = data.get('origin_model') 
    analysis_model_input = data.get('analysis_model') 
    origin_api_key_input = data.get('origin_api_key') 
    analysis_api_key_input = data.get('analysis_api_key') 
    origin_api_endpoint_input = data.get('origin_api_endpoint') # Added
    analysis_api_endpoint_input = data.get('analysis_api_endpoint') # Added

    # --- Determine R1 Model --- 
    default_r1_model = os.getenv(DEFAULT_LLM_MODEL_ENV)
    if not default_r1_model or default_r1_model not in ALL_MODELS:
        logger.warning(f"analyze: DEFAULT_LLM_MODEL env var '{default_r1_model}' invalid or not set. Falling back to first available model: '{ALL_MODELS[0] if ALL_MODELS else None}'.")
        default_r1_model = ALL_MODELS[0] if ALL_MODELS else None # Fallback to first model in list
        if not default_r1_model:
             logger.error("analyze: No default R1 model in env var and ALL_MODELS list is empty!")
             return jsonify({"error": "Server configuration error: No valid default model available."}), 500
             
    # Use user input if provided (and validated), otherwise use default
    if origin_model_input: # Already validated to be in ALL_MODELS or None
         r1_model_to_use = origin_model_input
         logger.info(f"analyze: Using user-provided Origin Model (R1): '{r1_model_to_use}'")
    else:
         r1_model_to_use = default_r1_model
         logger.info(f"analyze: Using default Origin Model (R1): '{r1_model_to_use}'")

    # --- Get R1 API Configuration --- 
    # Pass model, optional key, optional endpoint
    initial_config = _get_api_config(r1_model_to_use, origin_api_key_input, origin_api_endpoint_input) 
    if initial_config.get("error"):
        config_error_msg = initial_config["error"]
        logger.error(f"analyze: Error getting initial API config for R1 model '{r1_model_to_use}': {config_error_msg}")
        return jsonify({"error": f"Configuration error for model '{r1_model_to_use}': {config_error_msg}"}), 400

    # --- Determine R2 Model and Get Config --- 
    # Pass optional R2 model, key, endpoint
    analysis_config = _get_analysis_api_config(analysis_model_input, analysis_api_key_input, analysis_api_endpoint_input)
    if analysis_config.get("error"):
        config_error_msg = analysis_config["error"]
        logger.error(f"analyze: Error getting analysis API config (selected model: '{analysis_model_input}'): {config_error_msg}")
        return jsonify({"error": f"Server Configuration Error: {config_error_msg}"}), 500
        
    r2_model_to_use = analysis_config.get("model")
    if not r2_model_to_use: 
         logger.error("analyze: Critical internal error - r2_model_to_use is None after config fetch.")
         return jsonify({"error": "Internal server error determining analysis model."}), 500

    # --- Load Ontology --- 
    ontology_text = load_ontology()
    if not ontology_text:
        logger.error(f"analyze: Failed to load ontology text from {ONTOLOGY_FILEPATH}")
        return jsonify({"error": "Internal server error: Could not load ethical ontology."}), 500
    
    # --- Process Request --- 
    logger.info(f"analyze: Processing request - Prompt(start): {prompt[:100]}..., R1 Model: {r1_model_to_use}, R2 Model: {r2_model_to_use}")
    result_payload, error_status_code = _process_analysis_request(
        prompt,
        r1_model_to_use, 
        initial_config,  
        analysis_config, 
        ontology_text
    )
    
    # --- Handle Response --- 
    if error_status_code:
        return jsonify(result_payload), error_status_code
    else:
        logger.info(f"Successfully processed /analyze request.")
        return jsonify(result_payload), 200 