"""API routes for the ethical review backend"""

import os
from typing import Dict, Any, Optional, Tuple
from flask import Blueprint, request, jsonify
import re # Import regex module for parsing
import json # Import JSON module for parsing
import logging # Import logging

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
XAI_API_KEY_ENV = "XAI_API_KEY"  # Added xAI (Grok) API key env var
OPENAI_API_ENDPOINT_ENV = "OPENAI_API_ENDPOINT"
GEMINI_API_ENDPOINT_ENV = "GEMINI_API_ENDPOINT"
ANTHROPIC_API_ENDPOINT_ENV = "ANTHROPIC_API_ENDPOINT"
XAI_API_ENDPOINT_ENV = "XAI_API_ENDPOINT"  # Added xAI (Grok) API endpoint env var
DEFAULT_LLM_MODEL_ENV = "DEFAULT_LLM_MODEL"

# Environment variables for the Analysis LLM (Added OpenAI)
ANALYSIS_LLM_MODEL_ENV = "ANALYSIS_LLM_MODEL"
ANALYSIS_OPENAI_API_KEY_ENV = "ANALYSIS_OPENAI_API_KEY"
ANALYSIS_GEMINI_API_KEY_ENV = "ANALYSIS_GEMINI_API_KEY"
ANALYSIS_ANTHROPIC_API_KEY_ENV = "ANALYSIS_ANTHROPIC_API_KEY"
ANALYSIS_XAI_API_KEY_ENV = "ANALYSIS_XAI_API_KEY"  # Added xAI (Grok) Analysis API key env var
ANALYSIS_OPENAI_API_ENDPOINT_ENV = "ANALYSIS_OPENAI_API_ENDPOINT"
ANALYSIS_GEMINI_API_ENDPOINT_ENV = "ANALYSIS_GEMINI_API_ENDPOINT"
ANALYSIS_ANTHROPIC_API_ENDPOINT_ENV = "ANALYSIS_ANTHROPIC_API_ENDPOINT"
ANALYSIS_XAI_API_ENDPOINT_ENV = "ANALYSIS_XAI_API_ENDPOINT"  # Added xAI (Grok) Analysis API endpoint env var

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
    "gemini-2.5-pro",
    "gemini-2.5-flash"
]

ANTHROPIC_MODELS = [
    "claude-3-opus-20240229",
    "claude-3-sonnet-20240229",
    "claude-3-haiku-20240307",
]

# New xAI Grok models
XAI_MODELS = [
    "grok-2",
    "grok-3-mini",
    "grok-3"
]

ALL_MODELS = OPENAI_MODELS + GEMINI_MODELS + ANTHROPIC_MODELS + XAI_MODELS

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
    elif selected_model in XAI_MODELS:
        api_key_name = "Origin xAI (Grok)"
        env_var_key = XAI_API_KEY_ENV
        env_var_endpoint = XAI_API_ENDPOINT_ENV
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
        # Log a masked version of the key for debugging
        if api_key:
            masked_key = f"{api_key[:5]}...{api_key[-5:]}" if len(api_key) > 10 else "***masked***"
            logger.info(f"_get_api_config: Form API key format check - Length: {len(api_key)}, Start/End: {masked_key}")
    # 2. Fallback to environment variable if form key wasn't provided AND we know the variable name
    elif env_var_key:
        api_key = os.getenv(env_var_key)
        # Ensure any surrounding quotes are removed (common in environment variables)
        if api_key and isinstance(api_key, str):
            api_key = api_key.strip().strip('"\'')
            
        if api_key:
             key_source = f"Environment Variable ({env_var_key})"
             logger.info(f"_get_api_config: Using API key from env var {env_var_key} for {api_key_name}.")
             # Log a masked version of the key for debugging
             masked_key = f"{api_key[:5]}...{api_key[-5:]}" if len(api_key) > 10 else "***masked***"
             logger.info(f"_get_api_config: Env API key format check - Length: {len(api_key)}, Start/End: {masked_key}")
        else:
             logger.warning(f"_get_api_config: No API key found in env var {env_var_key} for {api_key_name}. This may cause request failure.")

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
            # Ensure any surrounding quotes are removed
            api_endpoint = env_endpoint_val.strip().strip('"\'')
            endpoint_source = f"Environment Variable ({env_var_endpoint})"
            logger.info(f"_get_api_config: Using API endpoint from env var {env_var_endpoint}: {api_endpoint}")
        else:
            logger.warning(f"_get_api_config: No API endpoint found in env var {env_var_endpoint} for {api_key_name}. Using default if available.")

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
    else:
        logger.error(f"_get_api_config: Configuration error for {selected_model}: {error}")
        
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
        # Clean up environment variable value if needed
        if default_analysis_model_env and isinstance(default_analysis_model_env, str):
            default_analysis_model_env = default_analysis_model_env.strip().strip('"\'')
            
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
    elif analysis_model in XAI_MODELS:
        api_key_name = "Analysis xAI (Grok)"
        specific_key_env = ANALYSIS_XAI_API_KEY_ENV
        fallback_key_env = XAI_API_KEY_ENV
        specific_endpoint_env = ANALYSIS_XAI_API_ENDPOINT_ENV
        fallback_endpoint_env = XAI_API_ENDPOINT_ENV
    # No else needed as model validity is checked above

    # 1. Prioritize API key provided in the form
    if form_analysis_api_key and isinstance(form_analysis_api_key, str) and form_analysis_api_key.strip():
        api_key = form_analysis_api_key.strip()
        key_source = "User Input"
        logger.info(f"_get_analysis_api_config: Using API key provided via form for {api_key_name}.")
        # Log a masked version of the key for debugging
        if api_key:
            masked_key = f"{api_key[:5]}...{api_key[-5:]}" if len(api_key) > 10 else "***masked***"
            logger.info(f"_get_analysis_api_config: Form API key format check - Length: {len(api_key)}, Start/End: {masked_key}")
    # 2. Fallback to environment variables if form key wasn't provided
    else:
        # Check specific analysis key first, then standard key
        if specific_key_env:
            env_key = os.getenv(specific_key_env)
            # Clean up environment variable value if needed
            if env_key and isinstance(env_key, str):
                env_key = env_key.strip().strip('"\'')
                
            if env_key:
                api_key = env_key
                key_source = f"Environment Variable ({specific_key_env})"
        
        if not api_key and fallback_key_env: # If specific key not found or doesn't exist, try fallback
            env_key = os.getenv(fallback_key_env)
            # Clean up environment variable value if needed
            if env_key and isinstance(env_key, str):
                env_key = env_key.strip().strip('"\'')
                
            if env_key:
                api_key = env_key
                key_source = f"Environment Variable ({fallback_key_env})"
        
        if api_key:
            logger.info(f"_get_analysis_api_config: Using API key from {key_source} for {api_key_name}.")
            # Log a masked version of the key for debugging
            masked_key = f"{api_key[:5]}...{api_key[-5:]}" if len(api_key) > 10 else "***masked***"
            logger.info(f"_get_analysis_api_config: Env API key format check - Length: {len(api_key)}, Start/End: {masked_key}")

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
            # Clean up environment variable value if needed
            if env_endpoint_val and isinstance(env_endpoint_val, str):
                env_endpoint_val = env_endpoint_val.strip().strip('"\'')
                
            if env_endpoint_val:
                api_endpoint = env_endpoint_val
                endpoint_source = f"Environment Variable ({specific_endpoint_env})"
        
        if not api_endpoint and fallback_endpoint_env: # If specific endpoint not found or doesn't exist, try fallback
            env_endpoint_val = os.getenv(fallback_endpoint_env)
            # Clean up environment variable value if needed
            if env_endpoint_val and isinstance(env_endpoint_val, str):
                env_endpoint_val = env_endpoint_val.strip().strip('"\'')
                
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
    """Parses the ethical analysis text to separate textual summary and structured JSON scores."""
    if not analysis_text or analysis_text == "[No analysis generated or content blocked]": # Handle placeholder
        logger.warning("Ethical analysis text was empty or indicated generation failure.")
        return analysis_text if analysis_text else "", None # Return placeholder or empty, and None scores

    textual_summary = ""
    json_scores = None
    raw_json_string = None # Keep track of the raw string for logging

    try:
        # Attempt to find the textual summary first
        summary_marker = "**Ethical Review Summary:**"
        scoring_marker = "**Ethical Scoring:**"
        summary_start_index = analysis_text.find(summary_marker)
        scoring_start_index = analysis_text.find(scoring_marker)

        if summary_start_index != -1 and scoring_start_index != -1 and summary_start_index < scoring_start_index:
            textual_summary = analysis_text[summary_start_index + len(summary_marker):scoring_start_index].strip()
        elif summary_start_index != -1: # If only summary marker is found
             textual_summary = analysis_text[summary_start_index + len(summary_marker):].strip()
        else: # Fallback if markers are missing or out of order
            textual_summary = analysis_text # Assign full text if structure isn't as expected
            logger.warning("Could not reliably find summary/scoring markers in analysis text.")

        # Attempt to find and parse the JSON block for scores
        json_match = re.search(r"```json\s*(\{.*?\})\s*```", analysis_text, re.DOTALL)
        
        if json_match:
            json_string = json_match.group(1)
            raw_json_string = json_string # Store for logging on error
            try: # Outer try for json.loads
                parsed_json = json.loads(json_string)
                # Validation block starts here
                try: # Inner try for validation accessing parsed_json content
                     # Basic validation of the parsed JSON structure
                     required_standard_dims = ["deontology", "teleology", "virtue_ethics"]
                     required_memetic_dim = "memetics"
                     required_memetic_keys = ["transmissibility_score", "persistence_score", "adaptability_score", "confidence_score", "justification"]
                     
                     is_valid = False
                     if isinstance(parsed_json, dict): 
                         # Check standard dimensions
                         standard_dims_present = all(dim in parsed_json for dim in required_standard_dims)
                         standard_dims_valid = all(isinstance(parsed_json[dim], dict) and 
                                                 all(key in parsed_json[dim] for key in ["adherence_score", "confidence_score", "justification"]) 
                                                 for dim in required_standard_dims if dim in parsed_json) # Check structure only if present
                         
                         # Check memetics dimension
                         memetics_present = required_memetic_dim in parsed_json
                         memetics_valid = False
                         if memetics_present and isinstance(parsed_json[required_memetic_dim], dict):
                             memetics_valid = all(key in parsed_json[required_memetic_dim] for key in required_memetic_keys)
                             
                         # Final validation check (all standard dims + memetics must be present and validly structured)
                         if standard_dims_present and standard_dims_valid and memetics_present and memetics_valid:
                            is_valid = True
                     
                     if is_valid:
                        json_scores = parsed_json
                        # Trim summary if needed (same logic as before)
                        if scoring_start_index != -1 and summary_start_index != -1:
                             textual_summary = analysis_text[summary_start_index + len(summary_marker):scoring_start_index].strip()
                        elif scoring_start_index == -1 and textual_summary.endswith(json_match.group(0)):
                             textual_summary = textual_summary[:-len(json_match.group(0))].strip()
                     else:
                         # Validation failed
                         logger.warning(f"Parsed JSON does not have the expected 4-dimension structure (including memetics). JSON: {json_string[:200]}...")
                         json_scores = None # Ensure it's None if validation fails
                except (TypeError, KeyError) as key_err: # Handles errors during validation access
                     logger.error(f"Error accessing keys in parsed JSON structure: {key_err}. JSON: {json_string[:200]}...", exc_info=True)
                     json_scores = None # Ensure it's None on structure access error
                # End of inner try-except block for validation

            except json.JSONDecodeError as json_err: # Handles errors during json.loads
                logger.error(f"Error decoding JSON from analysis: {json_err}. Raw JSON string: {raw_json_string[:200]}...", exc_info=True)
                json_scores = None # Explicitly set to None on JSON decode error
        else: # if json_match failed
            logger.warning("Could not find JSON block for ethical scores in analysis text.")
            json_scores = None # Ensure it's None if JSON block not found

    except Exception as e:
        logger.error(f"Error parsing ethical analysis structure: {e}", exc_info=True)
        textual_summary = analysis_text
        json_scores = None # Ensure scores are None on major parsing failure

    # Rename for clarity in return and API response
    ethical_analysis_text = textual_summary
    ethical_scores = json_scores # This will be None if any parsing/validation step failed

    return ethical_analysis_text, ethical_scores

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
    """Handles LLM calls and response parsing for the /analyze endpoint."""
        
    selected_model = r1_model_to_use # Use the model determined in the main 'analyze' function
    analysis_model_name = analysis_config.get("model") # Get the model determined by _get_analysis_api_config

    # Ensure analysis model name is valid before proceeding
    if not analysis_model_name:
         logger.error("_process_analysis_request: Analysis model name missing from analysis_config.")
         # This indicates an issue in _get_analysis_api_config logic
         return {"error": "Internal Server Error: Failed to determine analysis model."}, 500

    logger.info(f"_process_analysis_request: Using R1 model: {selected_model}")
    logger.info(f"_process_analysis_request: Using R2 model: {analysis_model_name}")

    # 1. Generate initial response
    logger.info(f"Generating initial response (R1) with model: {selected_model}")
    # Use the API key/endpoint from initial_config (which was fetched based on selected_model)
    initial_response = generate_response(
        prompt,
        initial_config["api_key"], 
        selected_model, 
        api_endpoint=initial_config.get("api_endpoint") # Use .get for safety
    )
    if initial_response is None:
        logger.error(f"Failed to generate initial response (R1) from LLM {selected_model}. Check LLM interface logs.")
        return {"error": f"Failed to generate response (R1) from the upstream language model: {selected_model}."}, 502

    # 2. Generate ethical analysis
    logger.info(f"Performing analysis (R2) with model: {analysis_model_name}")
    # Use the API key/endpoint from analysis_config (fetched based on analysis_model_name)
    raw_ethical_analysis = perform_ethical_analysis(
        prompt,
        initial_response,
        ontology_text,
        analysis_config["api_key"],
        analysis_model_name,
        analysis_api_endpoint=analysis_config.get("api_endpoint") # Use .get for safety
    )
    if raw_ethical_analysis is None:
        logger.error(f"Failed to generate ethical analysis (R2) from LLM {analysis_model_name}. Check LLM interface logs.")
        error_payload = {
            "error": f"Generated initial response (R1), but failed to generate ethical analysis (R2) from the upstream language model: {analysis_model_name}.",
            "prompt": prompt,
            "model": selected_model, # R1 model used
            "analysis_model": analysis_model_name, # R2 model attempted
            "initial_response": initial_response
        }
        return error_payload, 502

    # 3. Parse the analysis
    logger.info("Parsing ethical analysis response.")
    ethical_analysis_text, ethical_scores = _parse_ethical_analysis(raw_ethical_analysis)

    # 4. Prepare successful result dictionary
    result_payload = {
        "prompt": prompt,
        "model": selected_model, # R1 model actually used
        "analysis_model": analysis_model_name, # R2 model actually used
        "initial_response": initial_response,
        "ethical_analysis_text": ethical_analysis_text,
        "ethical_scores": ethical_scores
    }
    # Log the final models used
    log_prompt(prompt, f"R1: {selected_model}, R2: {analysis_model_name}")
    return result_payload, None # No error

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
    
    # Ensure default model value is properly cleaned
    if default_r1_model and isinstance(default_r1_model, str):
        default_r1_model = default_r1_model.strip().strip('"\'')
        logger.info(f"analyze: Retrieved default model from env: {default_r1_model}")
    else:
        logger.warning(f"analyze: DEFAULT_LLM_MODEL env var is empty or not a string")
        
    # Check against known models list
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
         
    # Log which model provider is being used    
    if r1_model_to_use in ANTHROPIC_MODELS:
        logger.info(f"analyze: Selected model '{r1_model_to_use}' is an Anthropic Claude model")
    elif r1_model_to_use in GEMINI_MODELS:
        logger.info(f"analyze: Selected model '{r1_model_to_use}' is a Google Gemini model")
    elif r1_model_to_use in OPENAI_MODELS:
        logger.info(f"analyze: Selected model '{r1_model_to_use}' is an OpenAI model")
    elif r1_model_to_use in XAI_MODELS:
        logger.info(f"analyze: Selected model '{r1_model_to_use}' is an xAI Grok model")
    else:
        logger.warning(f"analyze: Selected model '{r1_model_to_use}' is not in any known model list")

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