"""API routes for the ethical review backend"""

import os
from typing import Dict, Any, Optional, Tuple
from flask import Blueprint, request, jsonify, current_app
import re # Import regex module for parsing
import json # Import JSON module for parsing
import logging # Import logging
from pydantic import ValidationError
from bson import ObjectId

# Corrected relative import
from .modules.llm_interface import generate_response, perform_ethical_analysis, select_relevant_memes
# Corrected relative imports assuming db.py and models.py are in the same 'app' package
from .db import get_all_memes_for_selection
from .models import AnalysisResultModel

# --- Blueprint Definition ---
api_bp = Blueprint('api', __name__, url_prefix='/api')

# --- Setup Logger ---
logger = logging.getLogger(__name__)
# Assuming basicConfig is called in app __init__ or wsgi.py

# --- Constants ---
ONTOLOGY_FILEPATH = os.path.normpath(
    os.path.join(os.path.dirname(__file__), '..', '..', 'documents', 'ontology.md')
)
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

# Constants for parsing
SUMMARY_DELIMITER = "SUMMARY:"
JSON_DELIMITER = "JSON SCORES:"

# --- Helper Functions ---

def load_ontology(filepath: str = ONTOLOGY_FILEPATH) -> Optional[str]:
    """Loads the ethical ontology text from the specified file, falling back to /app/documents/ontology.md if needed."""
    # Try the primary path
    if filepath and os.path.exists(filepath):
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                return f.read()
        except Exception as e:
            logger.error(f"Error reading ontology at {filepath}: {e}", exc_info=True)
    else:
        logger.warning(f"Ontology file not found at primary path: {filepath}")
    # Fallback to mounted documents directory
    fallback_path = '/app/documents/ontology.md'
    if os.path.exists(fallback_path):
        try:
            with open(fallback_path, 'r', encoding='utf-8') as f:
                return f.read()
        except Exception as e:
            logger.error(f"Error reading ontology at fallback path {fallback_path}: {e}", exc_info=True)
    else:
        logger.error(f"Ontology file not found at fallback path: {fallback_path}")
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
    
    # Detailed logging for debugging default application
    logger.debug(f"_get_api_config: START - Model: {selected_model}")
    logger.debug(f"_get_api_config: Form Key Provided: {'YES' if form_api_key else 'NO'}")
    logger.debug(f"_get_api_config: Form Endpoint Provided: {'YES' if form_api_endpoint else 'NO'}")

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

    logger.debug(f"_get_api_config: Determined Key Env Var: {env_var_key}")
    logger.debug(f"_get_api_config: Determined Endpoint Env Var: {env_var_endpoint}")

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
             logger.debug(f"_get_api_config: Retrieved key from {env_var_key}: {'Exists' if api_key else 'Not Found or Empty'}")
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
            logger.debug(f"_get_api_config: Retrieved endpoint from {env_var_endpoint}: {api_endpoint}")
        else:
            logger.info(f"_get_api_config: No API endpoint found in env var {env_var_endpoint} for {api_key_name}. Library default (if any) will be used.")

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

    # Detailed logging for debugging default application
    logger.debug(f"_get_analysis_api_config: START - Requested Model: {selected_analysis_model}")
    logger.debug(f"_get_analysis_api_config: Form Key Provided: {'YES' if form_analysis_api_key else 'NO'}")
    logger.debug(f"_get_analysis_api_config: Form Endpoint Provided: {'YES' if form_analysis_api_endpoint else 'NO'}")

    # --- Determine Analysis Model --- 
    if not analysis_model or analysis_model not in ALL_MODELS:
        # If user provided an invalid model, log and try env var
        if selected_analysis_model and selected_analysis_model not in ALL_MODELS:
            logger.warning(f"_get_analysis_api_config: Invalid analysis model selected ('{selected_analysis_model}'). Checking ANALYSIS_LLM_MODEL env var.")
        # Check ANALYSIS_LLM_MODEL environment variable
        default_analysis_model_env = os.getenv(ANALYSIS_LLM_MODEL_ENV)
        if isinstance(default_analysis_model_env, str):
            default_analysis_model_env = default_analysis_model_env.strip().strip('"\'')
        # Use env var if valid
        if default_analysis_model_env in ALL_MODELS:
            analysis_model = default_analysis_model_env
            logger.info(f"_get_analysis_api_config: Using R2 model from env var {ANALYSIS_LLM_MODEL_ENV}: {analysis_model}")
            logger.debug(f"_get_analysis_api_config: Env var {ANALYSIS_LLM_MODEL_ENV} value: '{os.getenv(ANALYSIS_LLM_MODEL_ENV)}'")
        else:
            # Final fallback to first available model
            analysis_model = ALL_MODELS[0] if ALL_MODELS else None
            logger.warning(f"_get_analysis_api_config: No valid ANALYSIS_LLM_MODEL set. Falling back to first available model: {analysis_model}")
            logger.debug(f"_get_analysis_api_config: Env var {ANALYSIS_LLM_MODEL_ENV} value: '{os.getenv(ANALYSIS_LLM_MODEL_ENV)}'")
    else:
        logger.info(f"_get_analysis_api_config: Using user-selected R2 model: {analysis_model}")

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

    logger.debug(f"_get_analysis_api_config: Determined Specific Key Env: {specific_key_env}")
    logger.debug(f"_get_analysis_api_config: Determined Fallback Key Env: {fallback_key_env}")
    logger.debug(f"_get_analysis_api_config: Determined Specific Endpoint Env: {specific_endpoint_env}")
    logger.debug(f"_get_analysis_api_config: Determined Fallback Endpoint Env: {fallback_endpoint_env}")

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
                logger.debug(f"_get_analysis_api_config: Found key in specific env var: {specific_key_env}")
                key_source = f"Environment Variable ({specific_key_env})"
        
        if not api_key and fallback_key_env: # If specific key not found or doesn't exist, try fallback
            env_key = os.getenv(fallback_key_env)
            # Clean up environment variable value if needed
            if env_key and isinstance(env_key, str):
                env_key = env_key.strip().strip('"\'')
                
            if env_key:
                api_key = env_key
                logger.debug(f"_get_analysis_api_config: Found key in fallback env var: {fallback_key_env}")
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
                logger.debug(f"_get_analysis_api_config: Found endpoint in specific env var: {specific_endpoint_env}")
                endpoint_source = f"Environment Variable ({specific_endpoint_env})"
        
        if not api_endpoint and fallback_endpoint_env: # If specific endpoint not found or doesn't exist, try fallback
            env_endpoint_val = os.getenv(fallback_endpoint_env)
            # Clean up environment variable value if needed
            if env_endpoint_val and isinstance(env_endpoint_val, str):
                env_endpoint_val = env_endpoint_val.strip().strip('"\'')
                
            if env_endpoint_val:
                api_endpoint = env_endpoint_val
                logger.debug(f"_get_analysis_api_config: Found endpoint in fallback env var: {fallback_endpoint_env}")
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
    """Parses the raw text analysis from the LLM into summary and JSON scores."""
    logger.debug(f"_parse_ethical_analysis: Attempting to parse raw text:\n---\n{analysis_text}\n---")
    summary = "[Parsing Error: Summary not found]"
    scores_json = None

    # --- NEW: Attempt direct JSON parsing first ---
    # Some prompt templates instruct the LLM to return ONLY a JSON object with
    # keys "summary_text" and "scores_json" (no additional delimiters). In such
    # cases the earlier delimiter‑based extraction fails.  We therefore attempt
    # to parse the entire response as JSON *before* looking for legacy
    # delimiters.  If this succeeds we can return immediately.
    trimmed = analysis_text.strip()

    # Attempt 1: Entire string is JSON
    if trimmed.startswith("{") and trimmed.endswith("}"):
        candidate = trimmed
    else:
        # Attempt 2: Find first '{' and last '}' in response
        first_brace = trimmed.find('{')
        last_brace = trimmed.rfind('}')
        candidate = trimmed[first_brace:last_brace+1] if (first_brace != -1 and last_brace != -1 and last_brace > first_brace) else None

    if candidate:
        try:
            parsed = json.loads(candidate)
            if isinstance(parsed, dict) and ("summary_text" in parsed or "scores_json" in parsed):
                summary = parsed.get("summary_text", "[Parsing Error: summary_text missing]")
                scores_json = parsed.get("scores_json")
                logger.info("_parse_ethical_analysis: Parsed response as JSON without delimiters.")
                return summary, scores_json
        except json.JSONDecodeError:
            # candidate wasn't valid JSON – continue to legacy delimiter logic
            pass

    try:
        # Normalize line endings and strip leading/trailing whitespace
        normalized_text = analysis_text.replace('\\r\\n', '\\n').strip()

        # Find delimiters (case-insensitive)
        summary_match = re.search(f"^{SUMMARY_DELIMITER}", normalized_text, re.IGNORECASE | re.MULTILINE)
        json_match = re.search(f"^{JSON_DELIMITER}", normalized_text, re.IGNORECASE | re.MULTILINE)

        summary_start_index = -1
        json_start_index = -1

        if summary_match:
            summary_start_index = summary_match.end()
            logger.debug(f"Found summary delimiter at index {summary_start_index}")
        else:
            logger.warning(f"'{SUMMARY_DELIMITER}' not found in analysis text.")

        if json_match:
            json_start_index = json_match.end()
            logger.debug(f"Found JSON delimiter at index {json_start_index}")
        else:
            logger.warning(f"'{JSON_DELIMITER}' not found in analysis text.")

        # Extract sections based on found delimiters
        if summary_start_index != -1 and json_start_index != -1:
            if summary_start_index < json_start_index:
                # SUMMARY: comes before JSON SCORES:
                summary_text_raw = normalized_text[summary_start_index:json_match.start()].strip()
                json_text_raw = normalized_text[json_start_index:].strip()
            else:
                # JSON SCORES: comes before SUMMARY:
                json_text_raw = normalized_text[json_start_index:summary_match.start()].strip()
                summary_text_raw = normalized_text[summary_start_index:].strip()

        elif summary_start_index != -1:
            # Only SUMMARY: found
            summary_text_raw = normalized_text[summary_start_index:].strip()
            json_text_raw = "" # No JSON section
            logger.warning("Only summary delimiter found, no JSON scores expected.")
        elif json_start_index != -1:
            # Only JSON SCORES: found
            json_text_raw = normalized_text[json_start_index:].strip()
            summary_text_raw = "[Summary missing, only scores found]" # No summary section
            logger.warning("Only JSON delimiter found, no summary text expected.")
        else:
            # Neither delimiter found - assume the whole text is the summary
            summary_text_raw = normalized_text
            json_text_raw = ""
            logger.warning("Neither summary nor JSON delimiter found. Treating entire text as summary.")

        # Assign the extracted summary text
        summary = summary_text_raw if summary_text_raw else "[Parsing Error: Extracted summary was empty]"
        logger.debug(f"Extracted Summary Text:\n---\n{summary}\n---")

        # Parse the JSON part
        if json_text_raw:
            # Clean the JSON string: find the first '{' and the last '}'
            first_brace = json_text_raw.find('{')
            last_brace = json_text_raw.rfind('}')
            if first_brace != -1 and last_brace != -1 and last_brace > first_brace:
                json_string_cleaned = json_text_raw[first_brace:last_brace+1]
                logger.debug(f"Attempting to parse JSON string:\n---\n{json_string_cleaned}\n---")
                try:
                    scores_json = json.loads(json_string_cleaned)
                    logger.info("Successfully parsed JSON scores.")
                except json.JSONDecodeError as json_err:
                    logger.error(f"JSON decoding failed: {json_err}. Raw JSON text: {json_string_cleaned}")
                    summary += " [Warning: Failed to parse JSON scores]" # Append warning to summary
            else:
                logger.warning(f"Could not find valid JSON structure ({{...}}) in the JSON section. Raw text: {json_text_raw}")
        else:
            logger.info("No JSON score section found or extracted.")

    except Exception as e:
        logger.error(f"Unexpected error during parsing of analysis text: {e}", exc_info=True)
        summary = f"[Critical Parsing Error: {e}]"
        scores_json = None

    return summary, scores_json

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
    r2_model_to_use = analysis_config.get('model')
    logger.info(f"_process_analysis_request: Using R2 model: {r2_model_to_use}")

    # Initialize results
    response_payload = {
        "prompt": prompt,
        "r1_model": r1_model_to_use,
        "r2_model": r2_model_to_use,
        "initial_response": None,
        "selected_memes": None, # Add field for selected memes
        "selected_memes_reasoning": None, # Add field for reasoning
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

        # --- NEW: Select Relevant Memes (R3 - using R2 config for now) ---
        selected_meme_names = []
        selected_memes_reasoning = None
        try:
            logger.info("Fetching memes for selection...")
            available_memes = get_all_memes_for_selection()
            if available_memes:
                # Use R2/analysis config for the selector LLM call
                meme_selection_result = select_relevant_memes(
                    prompt=prompt,
                    r1_response=initial_response, # Use R1 output as context
                    available_memes=available_memes,
                    selector_api_key=analysis_config['api_key'],
                    selector_api_endpoint=analysis_config.get('api_endpoint')
                    # selector_model defaults to Haiku in llm_interface
                )
                if meme_selection_result:
                    selected_meme_names = meme_selection_result.selected_memes
                    selected_memes_reasoning = meme_selection_result.reasoning
                    response_payload["selected_memes"] = selected_meme_names
                    response_payload["selected_memes_reasoning"] = selected_memes_reasoning
                    logger.info(f"Meme Selector identified: {selected_meme_names}")
                else:
                    logger.warning("Meme selection process did not return results.")
            else:
                logger.warning("No memes found in DB for selection.")
        except Exception as meme_select_err:
            logger.error(f"Error during meme selection phase: {meme_select_err}", exc_info=True)
            # Continue with analysis even if meme selection fails

        # --- Perform Ethical Analysis (R2) ---
        logger.info(f"Performing analysis (R2) with model: {analysis_config.get('model')}")
        # Ensure R1 passed to analysis is always a string
        r1_for_analysis = initial_response if initial_response else "[No initial response was generated or it was blocked]"

        # Call analysis helper with correct signature
        raw_ethical_analysis_result = perform_ethical_analysis(
            initial_prompt=prompt,
            generated_response=r1_for_analysis,
            ontology=ontology_text,
            analysis_api_key=analysis_config['api_key'],
            analysis_model_name=analysis_config['model'],
            analysis_api_endpoint=analysis_config.get('api_endpoint'),
            selected_meme_names=selected_meme_names # Pass selected memes to R2
        )

        # --- Process R2 Result ---
        if not raw_ethical_analysis_result:
            logger.error(f"Ethical analysis (R2) failed or returned no result for model {analysis_config.get('model')}. Check LLM interface logs.")
            existing_error = response_payload.get("error", "") or ""
            response_payload["error"] = existing_error + f" Failed to generate analysis (R2) from {analysis_config.get('model')}."
            response_payload["analysis_summary"] = "[No analysis generated or content blocked]"
            response_payload["ethical_scores"] = None
        else:
            # Parse response first if it's a string
            analysis_data = raw_ethical_analysis_result
            if isinstance(raw_ethical_analysis_result, str):
                # First parse the string into a dictionary using existing helper
                summary, scores = _parse_ethical_analysis(raw_ethical_analysis_result)
                if scores:
                    # Transform the flat score structure into nested structure expected by our model
                    restructured_scores = {}
                    # Find all score keys that have a matching justification
                    for key in list(scores.keys()):
                        # Skip keys that are already justifications
                        if key.endswith('_justification'):
                            continue
                        
                        # Look for corresponding justification
                        justification_key = f"{key}_justification"
                        if justification_key in scores:
                            # Create nested structure for this dimension
                            restructured_scores[key] = {
                                "score": scores[key],
                                "justification": scores[justification_key]
                            }
                            # Remove processed justification key to avoid duplication
                            scores.pop(justification_key, None)
                        else:
                            # Handle case where justification is missing
                            restructured_scores[key] = {
                                "score": scores[key],
                                "justification": "No justification provided"
                            }
                    
                    # Create a dictionary structure compatible with our model
                    analysis_data = {
                        "summary_text": summary,
                        "scores_json": restructured_scores
                    }
                    logger.info("Parsed R2 text output into dictionary format.")
                else:
                    # Skip validation if we couldn't extract scores
                    response_payload["analysis_summary"] = summary
                    response_payload["ethical_scores"] = None
                    logger.warning("R2 response couldn't be parsed to extract valid scores.")
                    logger.info("Analysis completed with partial results.")
                    return response_payload, 200  # Return early

            # Now try validation if we have a dictionary
            if isinstance(analysis_data, dict):
                logger.info(f"Analysis data structure: {analysis_data.keys()}")
                # Also restructure scores_json if it exists and has a flat structure
                if "scores_json" in analysis_data:
                    logger.info(f"Scores data structure: {type(analysis_data['scores_json'])}")
                    if isinstance(analysis_data["scores_json"], dict):
                        scores = analysis_data["scores_json"]
                        logger.info(f"Scores keys: {scores.keys()}")
                        
                        # Check if we have a flat structure with _justification keys
                        has_flat_structure = any(key.endswith('_justification') for key in scores.keys())
                        
                        if has_flat_structure:
                            logger.info("Detected flat structure with _justification keys")
                            restructured_scores = {}
                            # Process each dimension
                            for key in list(scores.keys()):
                                if key.endswith('_justification'):
                                    continue
                                
                                justification_key = f"{key}_justification"
                                if justification_key in scores:
                                    restructured_scores[key] = {
                                        "score": scores[key],
                                        "justification": scores[justification_key]
                                    }
                                    scores.pop(justification_key, None)
                                else:
                                    restructured_scores[key] = {
                                        "score": scores[key],
                                        "justification": "No justification provided"
                                    }
                            
                            # Replace with restructured scores
                            analysis_data["scores_json"] = restructured_scores
                            logger.info("Restructured existing dictionary scores into required format")
                
                try:
                    result_model = AnalysisResultModel(**analysis_data)
                    response_payload["analysis_summary"] = result_model.summary_text
                    response_payload["ethical_scores"] = {k: v.model_dump() for k, v in result_model.scores_json.items()}
                    logger.info("R2 output validated successfully.")
                except ValidationError as val_err:
                    logger.error(f"R2 output failed validation: {val_err}")
                    # Fallback to raw dictionary values without validation
                    response_payload["analysis_summary"] = analysis_data.get("summary_text", "[Analysis summary missing]")
                    response_payload["ethical_scores"] = analysis_data.get("scores_json")
            else:
                logger.error(f"Unexpected R2 result format: {type(analysis_data)}")
                response_payload["analysis_summary"] = "[Unexpected analysis result format]"
                response_payload["ethical_scores"] = None
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

@api_bp.route('/ontology', methods=['GET'])
def get_ontology():
    """Return the ethical ontology markdown content."""
    ontology_text = load_ontology()
    if ontology_text is None:
        return jsonify({"error": "Ontology document not found."}), 404

    # Wrap result in JSON to keep consistent API style
    return jsonify({"ontology": ontology_text}), 200 