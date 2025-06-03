import os
from dotenv import load_dotenv
import logging
from typing import List, Dict, Any, Optional

logger = logging.getLogger(__name__)
load_dotenv() # Load .env file from project root or backend/

# --- General Application Settings ---
APP_NAME = "EthicsDashboard"
DEBUG_MODE = os.getenv("FLASK_DEBUG", "False").lower() == "true"

# --- LLM Models - Single Source of Truth ---
OPENAI_MODELS: List[str] = [
    "gpt-4o", "gpt-4-turbo", "gpt-3.5-turbo"
]
GEMINI_MODELS: List[str] = [
    "gemini-1.5-pro-latest", "gemini-1.5-flash-latest", "gemini-1.0-pro", "gemini-2.5-pro", "gemini-2.5-flash"
]
ANTHROPIC_MODELS: List[str] = [
    "claude-3-opus-20240229", "claude-3-sonnet-20240229", "claude-3-haiku-20240307"
]
XAI_MODELS: List[str] = [
    "grok-2", "grok-3-mini", "grok-3"
]
ALL_MODELS: List[str] = OPENAI_MODELS + GEMINI_MODELS + ANTHROPIC_MODELS + XAI_MODELS

# --- Default Model Configuration ---
DEFAULT_R1_MODEL_ENV_VAR = "DEFAULT_LLM_MODEL"
DEFAULT_R2_MODEL_ENV_VAR = "ANALYSIS_LLM_MODEL"
# Sensible fallbacks if environment variables are not set
FALLBACK_R1_MODEL = OPENAI_MODELS[0] if OPENAI_MODELS else (ALL_MODELS[0] if ALL_MODELS else None)
FALLBACK_R2_MODEL = ANTHROPIC_MODELS[2] if len(ANTHROPIC_MODELS) > 2 else (ALL_MODELS[0] if ALL_MODELS else None) # Prefer Haiku for R2 fallback

# --- API Key and Endpoint Environment Variable Names ---
# Provider-specific (used as fallback or if no ANALYSIS_ specific var is set)
OPENAI_API_KEY_ENV = "OPENAI_API_KEY"
GEMINI_API_KEY_ENV = "GEMINI_API_KEY"
ANTHROPIC_API_KEY_ENV = "ANTHROPIC_API_KEY"
XAI_API_KEY_ENV = "XAI_API_KEY"

OPENAI_API_ENDPOINT_ENV = "OPENAI_API_ENDPOINT" # e.g., https://api.openai.com/v1
GEMINI_API_ENDPOINT_ENV = "GEMINI_API_ENDPOINT" # e.g., generativelanguage.googleapis.com
ANTHROPIC_API_ENDPOINT_ENV = "ANTHROPIC_API_ENDPOINT" # e.g., https://api.anthropic.com
XAI_API_ENDPOINT_ENV = "XAI_API_ENDPOINT" # e.g., https://api.x.ai/v1

# Analysis-specific (prioritized for R2)
ANALYSIS_OPENAI_API_KEY_ENV = "ANALYSIS_OPENAI_API_KEY"
ANALYSIS_GEMINI_API_KEY_ENV = "ANALYSIS_GEMINI_API_KEY"
ANALYSIS_ANTHROPIC_API_KEY_ENV = "ANALYSIS_ANTHROPIC_API_KEY"
ANALYSIS_XAI_API_KEY_ENV = "ANALYSIS_XAI_API_KEY"

ANALYSIS_OPENAI_API_ENDPOINT_ENV = "ANALYSIS_OPENAI_API_ENDPOINT"
ANALYSIS_GEMINI_API_ENDPOINT_ENV = "ANALYSIS_GEMINI_API_ENDPOINT"
ANALYSIS_ANTHROPIC_API_ENDPOINT_ENV = "ANALYSIS_ANTHROPIC_API_ENDPOINT"
ANALYSIS_XAI_API_ENDPOINT_ENV = "ANALYSIS_XAI_API_ENDPOINT"

# --- File Paths & Directories ---
_APP_DIR = os.path.dirname(os.path.abspath(__file__)) # backend/app/
_BACKEND_DIR = os.path.dirname(_APP_DIR) # backend/
_PROJECT_ROOT_GUESS = os.path.dirname(_BACKEND_DIR) # Project root (one level above backend)

DOCUMENTS_DIR = os.path.join(_PROJECT_ROOT_GUESS, 'documents') # documents/
PROMPTS_DIR = os.path.join(_APP_DIR, 'prompts') # backend/app/prompts/

ONTOLOGY_FILENAME = "ontology.md"
ONTOLOGY_FILEPATH = os.path.join(DOCUMENTS_DIR, ONTOLOGY_FILENAME)

ETHICAL_ANALYSIS_PROMPT_FILENAME = "ethical_analysis_prompt.txt"
ETHICAL_ANALYSIS_PROMPT_FILEPATH = os.path.join(PROMPTS_DIR, ETHICAL_ANALYSIS_PROMPT_FILENAME)

MEMES_JSON_FILENAME = "memes.json"
MEMES_JSON_FILEPATH = os.path.join(DOCUMENTS_DIR, MEMES_JSON_FILENAME)

LOG_DIR = os.path.join(_BACKEND_DIR, "logs")
PROMPT_LOG_FILENAME = "logged_prompts.txt"
PROMPT_LOG_FILEPATH = os.path.join(LOG_DIR, PROMPT_LOG_FILENAME)
# Create log directory if it doesn't exist
os.makedirs(LOG_DIR, exist_ok=True)


# --- LLM Interface Settings ---
ANTHROPIC_API_VERSION_ENV = "ANTHROPIC_API_VERSION"
DEFAULT_ANTHROPIC_VERSION = "2023-06-01"
DEFAULT_GEMINI_SAFETY_SETTINGS: List[Dict[str, str]] = [
    {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
    {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
    {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
    {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"}
]
R2_MEME_CONTEXT_MAX_CHARS = int(os.getenv("R2_MEME_CONTEXT_MAX_CHARS", "5000")) # Increased default

# --- R2 Analysis Parsing Delimiters (fallback) ---
SUMMARY_DELIMITER = "SUMMARY:"
JSON_DELIMITER = "JSON SCORES:"

# --- Database Configuration ---
MONGO_HOST = os.getenv("MONGO_HOST", "ai-mongo")
MONGO_PORT = os.getenv("MONGO_PORT", "27017")
MONGO_USERNAME = os.getenv("MONGO_USERNAME")
MONGO_PASSWORD = os.getenv("MONGO_PASSWORD")
MONGO_DB_NAME = os.getenv("MONGO_DB_NAME", "ethics_db")
MONGO_URI_ENV_VAR = os.getenv("MONGO_URI") # Full connection string from env

# --- Dash UI settings ---
MAX_UPLOAD_SIZE_MB = 10 # For meme management uploads


class LLMConfigData:
    def __init__(self, model_name: str, api_key: Optional[str], api_endpoint: Optional[str], source_info: str, error: Optional[str] = None):
        self.model_name = model_name
        self.api_key = api_key
        self.api_endpoint = api_endpoint
        self.source_info = source_info
        self.error = error
        if not self.api_key and not self.error: # If no key and no pre-existing error
            self.error = f"API Key for {self.model_name} ({self.source_info}) not found or empty."

    def __repr__(self):
        masked_key_status = "Provided" if self.api_key else "Not Provided/Empty"
        return (f"LLMConfigData(model='{self.model_name}', key_status='{masked_key_status}', "
                f"endpoint='{self.api_endpoint or 'Default'}', source='{self.source_info}', error='{self.error}')")

def get_llm_config(
    requested_model: Optional[str],
    form_api_key: Optional[str],
    form_api_endpoint: Optional[str],
    default_model_env_var_name: str, # e.g., DEFAULT_R1_MODEL_ENV_VAR
    default_fallback_model: Optional[str], # e.g., FALLBACK_R1_MODEL
    is_analysis_config: bool = False
) -> LLMConfigData:
    """
    Determines the LLM configuration (model, API key, endpoint).
    Priority: Form inputs > Specific Env Vars (if analysis) > General Env Vars > Defaults.
    """
    final_model = requested_model
    model_source_info = "user_form_model"

    # 1. Determine Model Name
    if not final_model or final_model not in ALL_MODELS:
        env_model_name = os.getenv(default_model_env_var_name)
        if env_model_name and isinstance(env_model_name, str):
            env_model_name = env_model_name.strip().strip('"\'')
        if env_model_name in ALL_MODELS:
            final_model = env_model_name
            model_source_info = f"env_var_for_model ({default_model_env_var_name})"
        elif default_fallback_model and default_fallback_model in ALL_MODELS:
            final_model = default_fallback_model
            model_source_info = "hardcoded_fallback_model"
            logger.warning(f"Requested model '{requested_model}' invalid, and default env model from '{default_model_env_var_name}' ('{env_model_name}') is invalid or not set. Using hardcoded fallback: {final_model}")
        else:
            error_msg = f"No valid model found for request. Requested: '{requested_model}', EnvVar '{default_model_env_var_name}': '{env_model_name}', Fallback: '{default_fallback_model}'. Critical: No models available."
            logger.error(error_msg)
            return LLMConfigData(requested_model or "Unknown", None, None, "error_no_valid_model", error_msg)
    logger.info(f"Using model: {final_model} (Source: {model_source_info}, User Requested: {requested_model})")

    # 2. Determine API Key and Endpoint based on the final_model
    provider_key_env, provider_endpoint_env = None, None
    specific_analysis_key_env, specific_analysis_endpoint_env = None, None # For analysis-specific vars
    api_provider_name = "UnknownProvider"

    if final_model in OPENAI_MODELS:
        api_provider_name = "OpenAI"
        provider_key_env, provider_endpoint_env = OPENAI_API_KEY_ENV, OPENAI_API_ENDPOINT_ENV
        if is_analysis_config:
            specific_analysis_key_env, specific_analysis_endpoint_env = ANALYSIS_OPENAI_API_KEY_ENV, ANALYSIS_OPENAI_API_ENDPOINT_ENV
    elif final_model in GEMINI_MODELS:
        api_provider_name = "Gemini"
        provider_key_env, provider_endpoint_env = GEMINI_API_KEY_ENV, GEMINI_API_ENDPOINT_ENV
        if is_analysis_config:
            specific_analysis_key_env, specific_analysis_endpoint_env = ANALYSIS_GEMINI_API_KEY_ENV, ANALYSIS_GEMINI_API_ENDPOINT_ENV
    elif final_model in ANTHROPIC_MODELS:
        api_provider_name = "Anthropic"
        provider_key_env, provider_endpoint_env = ANTHROPIC_API_KEY_ENV, ANTHROPIC_API_ENDPOINT_ENV
        if is_analysis_config:
            specific_analysis_key_env, specific_analysis_endpoint_env = ANALYSIS_ANTHROPIC_API_KEY_ENV, ANALYSIS_ANTHROPIC_API_ENDPOINT_ENV
    elif final_model in XAI_MODELS:
        api_provider_name = "xAI"
        provider_key_env, provider_endpoint_env = XAI_API_KEY_ENV, XAI_API_ENDPOINT_ENV
        if is_analysis_config:
            specific_analysis_key_env, specific_analysis_endpoint_env = ANALYSIS_XAI_API_KEY_ENV, ANALYSIS_XAI_API_ENDPOINT_ENV

    # Key resolution
    key_source_debug = "user_form_key"
    final_api_key = form_api_key.strip() if form_api_key and isinstance(form_api_key, str) and form_api_key.strip() else None

    if not final_api_key:
        if is_analysis_config and specific_analysis_key_env: # Try specific analysis key first
            final_api_key = os.getenv(specific_analysis_key_env)
            key_source_debug = f"env_analysis_specific ({specific_analysis_key_env})"
        if not final_api_key and provider_key_env: # Then try general provider key
            final_api_key = os.getenv(provider_key_env)
            key_source_debug = f"env_provider_general ({provider_key_env})"
        if final_api_key and isinstance(final_api_key, str):
            final_api_key = final_api_key.strip().strip('"\'') # Clean up
            if not final_api_key: # Was it just quotes?
                key_source_debug += " (empty_after_strip)"
                final_api_key = None


    # Endpoint resolution
    endpoint_source_debug = "user_form_endpoint"
    final_api_endpoint = None
    if form_api_endpoint and isinstance(form_api_endpoint, str) and form_api_endpoint.strip().startswith(("http://", "https://")):
        final_api_endpoint = form_api_endpoint.strip()
    else:
        if form_api_endpoint and form_api_endpoint.strip(): # Log if provided but invalid format
            logger.warning(f"Form endpoint '{form_api_endpoint}' for {api_provider_name} is invalid. Checking env.")

        if is_analysis_config and specific_analysis_endpoint_env: # Try specific analysis endpoint
            final_api_endpoint = os.getenv(specific_analysis_endpoint_env)
            endpoint_source_debug = f"env_analysis_specific ({specific_analysis_endpoint_env})"
        if not final_api_endpoint and provider_endpoint_env: # Then try general provider endpoint
            final_api_endpoint = os.getenv(provider_endpoint_env)
            endpoint_source_debug = f"env_provider_general ({provider_endpoint_env})"

        if final_api_endpoint and isinstance(final_api_endpoint, str):
            final_api_endpoint = final_api_endpoint.strip().strip('"\'') # Clean up
            if final_api_endpoint and not final_api_endpoint.startswith(("http://", "https://")): # Validate env endpoint format
                logger.warning(f"Env endpoint '{final_api_endpoint}' from {endpoint_source_debug} for {api_provider_name} is invalid. Will use library default for this provider.")
                final_api_endpoint = None # Reset to use library default for this provider
            elif not final_api_endpoint: # Was it just quotes?
                 endpoint_source_debug += " (empty_after_strip)"
                 final_api_endpoint = None


    config_source_info = (f"model_source: {model_source_info}; key_source: {key_source_debug}; "
                          f"endpoint_source: {endpoint_source_debug}")
    llm_config_instance = LLMConfigData(final_model, final_api_key, final_api_endpoint, config_source_info)
    logger.info(f"Resolved LLM config for {api_provider_name} (is_analysis={is_analysis_config}): {llm_config_instance}")
    return llm_config_instance

def get_mongo_uri() -> str:
    """Constructs the MongoDB URI from environment variables."""
    if MONGO_URI_ENV_VAR:
        logger.info(f"Using MongoDB URI from environment variable: MONGO_URI")
        return MONGO_URI_ENV_VAR

    user = MONGO_USERNAME
    password = MONGO_PASSWORD
    host = MONGO_HOST
    port = MONGO_PORT
    db_name = MONGO_DB_NAME # DB name in path for some drivers

    if user and password:
        from urllib.parse import quote_plus
        user_encoded = quote_plus(user)
        password_encoded = quote_plus(password)
        uri = f"mongodb://{user_encoded}:{password_encoded}@{host}:{port}/{db_name}?authSource=admin"
        logger.info("Constructed MongoDB URI with credentials.")
    else:
        uri = f"mongodb://{host}:{port}/{db_name}"
        logger.warning("MONGO_USERNAME or MONGO_PASSWORD not set. Using unauthenticated MongoDB URI.")
    return uri

def get_mongo_db_name() -> str:
    """Gets the MongoDB database name, potentially parsing from MONGO_URI if MONGO_DB_NAME is not set."""
    if MONGO_DB_NAME:
        return MONGO_DB_NAME
    if MONGO_URI_ENV_VAR:
        try:
            from urllib.parse import urlparse
            parsed_uri = urlparse(MONGO_URI_ENV_VAR)
            db_name_from_uri = parsed_uri.path.lstrip('/')
            if db_name_from_uri:
                logger.info(f"Parsed DB name '{db_name_from_uri}' from MONGO_URI.")
                return db_name_from_uri
        except Exception as e:
            logger.warning(f"Could not parse DB name from MONGO_URI: {e}. Falling back to default.")
    return "ethics_db"

# Ensure prompt log directory exists on import
try:
    os.makedirs(LOG_DIR, exist_ok=True)
except Exception as e:
    logger.error(f"Failed to create log directory at {LOG_DIR}: {e}") 