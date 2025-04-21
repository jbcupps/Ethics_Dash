"""Module for interacting with Large Language Models (OpenAI, Gemini, Anthropic)."""

import os
import logging
import google.generativeai as genai
import anthropic
import openai # Added OpenAI import
import httpx # Import httpx
from typing import Optional, Dict, List, Any, Tuple # Removed TypedDict
from google.api_core import exceptions as google_exceptions # For specific error handling
from anthropic import APIError as AnthropicAPIError, APIConnectionError as AnthropicConnectionError, APITimeoutError as AnthropicTimeoutError # For specific error handling
from openai import OpenAIError, APIConnectionError as OpenAIConnectionError, APITimeoutError as OpenAITimeoutError, AuthenticationError as OpenAIAuthError, RateLimitError as OpenAIRateLimitError # Added OpenAI errors
from urllib.parse import urlparse
import json # Added for structured logging potentially
import re    # Import regex for parsing in select_relevant_memes
# Removed unused bson/pymongo imports
# from bson import ObjectId
# from bson.errors import InvalidId
# from pymongo.database import Database
# import traceback # Removed unused import

# --- NEW: Import for Meme Selection --- 
from ..models import MemeSelectionResponse # For parsing meme selection output
from pydantic import ValidationError

# Define SafetySettingDict to match the structure expected by the API
# Removed unused TypedDict definition
# class SafetySettingDict(TypedDict):
#     category: str
#     threshold: str

# --- Constants ---
MODEL_TYPE_OPENAI = "openai"
MODEL_TYPE_GEMINI = "gemini"
MODEL_TYPE_ANTHROPIC = "claude"
MODEL_TYPE_XAI = "xai"  # Added xAI model type constant

# Environment variable for Anthropic API version
ANTHROPIC_API_VERSION_ENV = "ANTHROPIC_API_VERSION"
DEFAULT_ANTHROPIC_VERSION = "2023-06-01"  # Default if not specified

# --- Model Definitions (Copied from api.py for local scope) --- 
OPENAI_MODELS = [
    "gpt-4o",
    "gpt-4-turbo",
    "gpt-3.5-turbo"
]

GEMINI_MODELS = [
    "gemini-1.5-pro-latest",
    "gemini-1.5-flash-latest",
    "gemini-1.0-pro",
    "gemini-2.5-pro",      # Added Gemini 2.5 Pro model
    "gemini-2.5-flash"     # Added Gemini 2.5 Flash variant
]

ANTHROPIC_MODELS = [
    "claude-3-opus-20240229",
    "claude-3-sonnet-20240229",  # Ensure Claude 3 Sonnet is in supported Anthropic models
    "claude-3-haiku-20240307",
]

# New xAI Grok models
XAI_MODELS = [
    "grok-2",
    "grok-3-mini", 
    "grok-3"
]
# Note: ALL_MODELS is not strictly needed within this module

# Default safety settings for Gemini (BLOCK_MEDIUM_AND_ABOVE)
DEFAULT_GEMINI_SAFETY_SETTINGS: List[Dict[str, str]] = [
    {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
    {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
    {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
    {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"}
]

# --- Logging Configuration ---
# Configure logging for this module
logger = logging.getLogger(__name__)
# Ensure logger is configured (can be done in __init__.py or here if run standalone)
if not logger.hasHandlers():
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

# --- NEW: Prompt Template Loading Helper ---
# Obsolete comment removed

def _load_prompt_template(filename: str) -> Optional[str]:
    """Loads a prompt template relative to the application structure."""
    
    # Determine the path to the prompts directory relative to this file
    # Assumes llm_interface.py is in backend/app/modules/
    # and prompts are in backend/app/prompts/
    current_dir = os.path.dirname(os.path.abspath(__file__))
    # Correct relative path: Go up one level from modules, then into prompts
    prompts_dir = os.path.join(current_dir, '..', 'prompts') 
    filepath = os.path.join(prompts_dir, filename)

    logger.info(f"Attempting to load prompt template from: {filepath}")

    if not os.path.exists(filepath):
        logger.error(f"Prompt template file not found: {filepath}")
        # Attempt fallback relative to app root (e.g., if prompts were in backend/prompts)
        alt_prompts_dir = os.path.join(current_dir, '..', '..', 'prompts') # Go up two levels
        alt_filepath = os.path.join(alt_prompts_dir, filename)
        if os.path.exists(alt_filepath):
             logger.info(f"Found prompt template at alternate path: {alt_filepath}")
             filepath = alt_filepath # Use this path for reading
        else:
             logger.error(f"Also tried alternate path, not found: {alt_filepath}")
             logger.error(f"Prompt template '{filename}' not found at primary ({filepath}) or alternate paths.")
             return None

    # Try reading from the determined path
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
            logger.info(f"Successfully loaded prompt template: {filename} from {filepath}")
            return content
    except Exception as e:
        logger.error(f"Error reading prompt template file {filepath}: {e}", exc_info=True)
        return None

# --- Internal Helper Functions ---

def _get_gemini_client_options(api_endpoint: Optional[str]) -> Optional[Dict[str, Any]]:
    """Parses the API endpoint and returns client options for Gemini."""
    if not api_endpoint:
        return None
    try:
        parsed_url = urlparse(api_endpoint)
        hostname = parsed_url.netloc
        if hostname:
            logger.info(f"Using custom Gemini hostname: {hostname}")
            return {"api_endpoint": hostname}
        else:
            logger.warning(f"Could not parse hostname from Gemini endpoint: {api_endpoint}. Using library default.")
            return None
    except Exception as parse_err:
        logger.warning(f"Error parsing Gemini endpoint URL '{api_endpoint}': {parse_err}. Using library default.")
        return None

def _call_gemini(
    prompt: str,
    api_key: str,
    model_name: str,
    api_endpoint: Optional[str],
    safety_settings: Optional[List[Dict[str, str]]] = None,
    generation_config: Optional[Dict[str, Any]] = None
) -> Optional[str]:
    """Handles the specific logic for calling the Gemini API with robust error handling."""
    log_prompt_start = prompt[:100] # For logging, avoid logging full sensitive prompts
    try:
        client_options = _get_gemini_client_options(api_endpoint)
        genai.configure(api_key=api_key, client_options=client_options)
        model = genai.GenerativeModel(model_name)

        effective_safety = safety_settings if safety_settings is not None else DEFAULT_GEMINI_SAFETY_SETTINGS

        logger.debug(f"Calling Gemini model {model_name}...")
        response = model.generate_content(
            prompt,
            safety_settings=effective_safety,
            generation_config=generation_config
        )

        # Handle potential blocking or empty response explicitly
        finish_reason = getattr(response, 'prompt_feedback', None)
        content_blocked = False
        block_reason = "Unknown or not provided by API."

        if finish_reason and hasattr(finish_reason, 'block_reason') and finish_reason.block_reason != "BLOCK_REASON_UNSPECIFIED":
             content_blocked = True
             block_reason = f"Finish Reason: {finish_reason.block_reason}"
             if hasattr(finish_reason, 'safety_ratings'):
                 block_reason += f", Safety Ratings: {finish_reason.safety_ratings}"
        elif hasattr(response, 'parts') and not response.parts:
             content_blocked = True
             block_reason = "Response contained no parts."
        elif hasattr(response, 'candidates') and not response.candidates:
            content_blocked = True
            block_reason = "Response contained no candidates."


        if content_blocked:
            logger.warning(
                f"Gemini response blocked or empty. Model: {model_name}, "
                f"Reason: {block_reason}, Prompt (start): {log_prompt_start}..."
            )
            return None # Indicate failure/blockage

        logger.debug(f"Gemini response generated successfully for model {model_name}.")

        # Safely extract text content
        try:
             if hasattr(response, 'candidates') and response.candidates:
                 if response.candidates[0].content and response.candidates[0].content.parts:
                     return response.candidates[0].content.parts[0].text
                 else:
                      logger.warning(f"Gemini response candidate missing content/parts for model {model_name}. Response: {response}")
                      return None
             elif hasattr(response, 'text'):
                 return response.text
             elif hasattr(response, 'parts') and response.parts:
                  return response.parts[0].text
             else:
                 logger.error(f"Unexpected Gemini response format or no text found for model {model_name}. Response: {response}")
                 return None
        except (AttributeError, IndexError, ValueError) as text_extract_err:
             logger.error(f"Error extracting text from Gemini response for model {model_name}: {text_extract_err}. Response: {response}", exc_info=True)
             return None


    except google_exceptions.InvalidArgument as e:
         logger.error(f"Gemini API Invalid Argument error for model {model_name}: {e}. Check safety settings or prompt format. Prompt (start): {log_prompt_start}...", exc_info=True)
         return None
    except google_exceptions.PermissionDenied as e:
         logger.error(f"Gemini API Permission Denied error for model {model_name}: {e}. Check API Key. Prompt (start): {log_prompt_start}...", exc_info=True)
         return None
    except google_exceptions.ResourceExhausted as e:
         logger.error(f"Gemini API Resource Exhausted (quota?) error for model {model_name}: {e}. Prompt (start): {log_prompt_start}...", exc_info=True)
         return None
    except google_exceptions.DeadlineExceeded as e:
         logger.error(f"Gemini API Deadline Exceeded (timeout) error for model {model_name}: {e}. Prompt (start): {log_prompt_start}...", exc_info=True)
         return None
    except google_exceptions.GoogleAPIError as e:
        logger.error(f"General Gemini API error for model {model_name}: {e}. Prompt (start): {log_prompt_start}...", exc_info=True)
        return None
    except Exception as e:
        logger.error(f"Unexpected exception during Gemini call for model {model_name}: {e}. Prompt (start): {log_prompt_start}...", exc_info=True)
        return None

def _call_anthropic(
    prompt: str,
    api_key: str,
    model_name: str,
    api_endpoint: Optional[str],
    max_tokens: int
) -> Optional[str]:
    """Handles the specific logic for calling the Anthropic API with robust error handling."""
    log_prompt_start = prompt[:100] # For logging
    try:
        api_version = os.getenv(ANTHROPIC_API_VERSION_ENV) or DEFAULT_ANTHROPIC_VERSION
        
        if "claude-3" in model_name and api_version < "2023-06-01":
            logger.warning(f"Using updated API version for Claude 3 model. Original: {api_version}, Updated: 2023-06-01")
            api_version = "2023-06-01"
        
        logger.info(f"Using Anthropic API version: {api_version} for model: {model_name}")
        
        headers = {"anthropic-version": api_version, "Content-Type": "application/json"}

        logger.info(f"Initializing Anthropic client. Base URL: {api_endpoint}, Version Header: {api_version}")
        client = anthropic.Anthropic(
            api_key=api_key, base_url=api_endpoint, timeout=120.0, default_headers=headers
        )

        logger.info(f"About to call Anthropic model: {model_name} with version: {api_version}")
        system_prompt = "You are a helpful, harmless, and honest AI assistant."
        
        logger.debug(f"Calling Anthropic model {model_name}...")
        message = client.messages.create(
            model=model_name, max_tokens=max_tokens, system=system_prompt,
            messages=[{"role": "user", "content": prompt}]
        )

        if message.stop_reason == 'max_tokens':
            logger.warning(f"Anthropic response truncated due to max_tokens ({max_tokens}). Model: {model_name}, Prompt (start): {log_prompt_start}...")
        elif message.stop_reason == 'error':
             logger.error(f"Anthropic API reported an error stop_reason. Model: {model_name}, Prompt (start): {log_prompt_start}...")
             return None
        elif message.stop_reason != 'end_turn' and message.stop_reason != 'stop_sequence' and message.stop_reason != 'tool_use':
             logger.warning(f"Anthropic response ended with unexpected reason: {message.stop_reason}. Model: {model_name}, Prompt (start): {log_prompt_start}...")

        response_text = None
        try:
            if message.content and isinstance(message.content, list) and len(message.content) > 0:
                if hasattr(message.content[0], 'text') and message.content[0].text:
                    response_text = message.content[0].text
                elif hasattr(message.content[0], 'value') and message.content[0].value:
                    response_text = message.content[0].value
                else:
                    logger.warning(f"Anthropic response has content but missing text/value. Model: {model_name}, Content: {message.content}")
            else:
                logger.warning(f"Anthropic response blocked, empty, or malformed content block. Model: {model_name}, Stop Reason: {message.stop_reason}, Prompt (start): {log_prompt_start}...")
                return None

        except (AttributeError, IndexError, TypeError) as content_err:
             logger.error(f"Error extracting text content from Anthropic response: {content_err}. Model: {model_name}, Response: {message}", exc_info=True)
             return None

        logger.debug(f"Anthropic response generated successfully for model {model_name}.")
        return response_text

    except AnthropicTimeoutError as e:
         logger.error(f"Anthropic API Timeout error for model {model_name}: {e}. Prompt (start): {log_prompt_start}...", exc_info=True)
         return None
    except AnthropicConnectionError as e:
         logger.error(f"Anthropic API Connection error for model {model_name}: {e}. Prompt (start): {log_prompt_start}...", exc_info=True)
         return None
    except AnthropicAPIError as e:
        logger.error(f"Anthropic API error for model {model_name}: {e}. Prompt (start): {log_prompt_start}...", exc_info=True)
        return None
    except Exception as e:
        logger.error(f"Unexpected exception during Anthropic call for model {model_name}: {e}. Prompt (start): {log_prompt_start}...", exc_info=True)
        return None

def _call_openai(
    prompt: str,
    api_key: str,
    model_name: str,
    api_endpoint: Optional[str],
    max_tokens: int
) -> Optional[str]:
    """Handles the specific logic for calling the OpenAI API with robust error handling."""
    log_prompt_start = prompt[:100] # For logging
    try:
        client = openai.OpenAI(api_key=api_key, base_url=api_endpoint)
        logger.debug(f"Calling OpenAI model {model_name}...")
        
        chat_completion = client.chat.completions.create(
            messages=[{"role": "user", "content": prompt,}],
            model=model_name, max_tokens=max_tokens,
        )

        if chat_completion.choices and chat_completion.choices[0].message and chat_completion.choices[0].message.content:
            response_text = chat_completion.choices[0].message.content
            finish_reason = chat_completion.choices[0].finish_reason
            
            if finish_reason == 'length': logger.warning(f"OpenAI response truncated due to max_tokens ({max_tokens}). Model: {model_name}, Prompt (start): {log_prompt_start}...")
            elif finish_reason != 'stop': logger.warning(f"OpenAI response finished with unexpected reason: {finish_reason}. Model: {model_name}, Prompt (start): {log_prompt_start}...")
            
            logger.debug(f"OpenAI response generated successfully for model {model_name}.")
            return response_text
        else:
            logger.warning(f"OpenAI response missing choices or content. Model: {model_name}, Prompt (start): {log_prompt_start}..., Response: {chat_completion}")
            return None

    except OpenAIAuthError as e:
         logger.error(f"OpenAI API Authentication Error (check API Key) for model {model_name}: {e}. Prompt (start): {log_prompt_start}...", exc_info=True)
         return None
    except OpenAIRateLimitError as e:
         logger.error(f"OpenAI API Rate Limit Exceeded for model {model_name}: {e}. Prompt (start): {log_prompt_start}...", exc_info=True)
         return None
    except OpenAITimeoutError as e:
         logger.error(f"OpenAI API Timeout error for model {model_name}: {e}. Prompt (start): {log_prompt_start}...", exc_info=True)
         return None
    except OpenAIConnectionError as e:
         logger.error(f"OpenAI API Connection error for model {model_name}: {e}. Prompt (start): {log_prompt_start}...", exc_info=True)
         return None
    except OpenAIError as e:
        logger.error(f"General OpenAI API error for model {model_name}: {e}. Prompt (start): {log_prompt_start}...", exc_info=True)
        return None
    except Exception as e:
        logger.error(f"Unexpected exception during OpenAI call for model {model_name}: {e}. Prompt (start): {log_prompt_start}...", exc_info=True)
        return None

def _call_xai(
    prompt: str,
    api_key: str,
    model_name: str,
    api_endpoint: Optional[str],
    max_tokens: int
) -> Optional[str]:
    """Handles the specific logic for calling the xAI (Grok) API with robust error handling."""
    log_prompt_start = prompt[:100] # For logging
    try:
        headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
        base_url = api_endpoint or "https://api.x.ai/v1" # Changed Grok URL
        
        payload = {
            "model": model_name,
            "messages": [{"role": "user", "content": prompt}],
            "max_tokens": max_tokens,
            "temperature": 0.7
        }
        
        logger.info(f"Calling xAI model {model_name} via API...")
        
        response = httpx.post(f"{base_url}/chat/completions", headers=headers, json=payload, timeout=120.0)
        
        if response.status_code != 200:
            logger.error(f"xAI API returned error status code: {response.status_code}, Response: {response.text[:500]}...")
            return None
            
        response_data = response.json()
        
        if "choices" in response_data and len(response_data["choices"]) > 0:
            choice = response_data["choices"][0]
            if "message" in choice and "content" in choice["message"]:
                content = choice["message"]["content"]
                logger.debug(f"xAI response generated successfully for model {model_name}.")
                return content
        
        logger.warning(f"Could not extract content from xAI response: {response_data}")
        return None
        
    except httpx.TimeoutException as e:
        logger.error(f"xAI API timeout error for model {model_name}: {e}. Prompt (start): {log_prompt_start}...", exc_info=True)
        return None
    except httpx.HTTPError as e:
        logger.error(f"xAI API HTTP error for model {model_name}: {e}. Prompt (start): {log_prompt_start}...", exc_info=True)
        return None
    except Exception as e:
        logger.error(f"Unexpected exception during xAI call for model {model_name}: {e}. Prompt (start): {log_prompt_start}...", exc_info=True)
        return None

# --- Optional Meme Pre-filter Configuration --- # REMOVED UNUSED FUNCTION
# MEME_PREFILTER_ENABLED = os.getenv("MEME_PREFILTER_ENABLED", "true").lower() in ("1","true","yes")
# MEME_PREFILTER_TOP_K = int(os.getenv("MEME_PREFILTER_TOP_K", "50"))
#
# def _prefilter_memes(query_text: str, memes: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
#     """Pre-filter memes by simple token overlap, keeping top K if enabled."""
#     if not MEME_PREFILTER_ENABLED:
#         return memes
#     query_tokens = set(re.findall(r'\w+', query_text.lower()))
#     scored: List[Tuple[int, Dict[str, Any]]] = []
#     for meme in memes:
#         meme_text = f"{meme.get('name','')} {meme.get('description','')}"
#         meme_tokens = set(re.findall(r'\w+', meme_text.lower()))
#         overlap = len(query_tokens & meme_tokens)
#         scored.append((overlap, meme))
#     scored.sort(key=lambda x: x[0], reverse=True)
#     top_k = [m for score, m in scored[:MEME_PREFILTER_TOP_K] if score > 0]
#     if not top_k:
#         top_k = [m for _, m in scored[:MEME_PREFILTER_TOP_K]]
#     return top_k

# --- NEW: Meme Selection Function ---
MEME_SELECTOR_MODEL = "claude-3-haiku-20240307" # Use Haiku by default

def select_relevant_memes(
    prompt: str, 
    r1_response: str, 
    available_memes: List[Dict[str, Any]], # Expecting list of {'_id': str, 'name': str, 'description': str}
    selector_api_key: str, 
    selector_api_endpoint: Optional[str] = None,
    max_tokens: int = 500 # Max tokens for the selector's response
) -> Optional[MemeSelectionResponse]:
    """
    Uses an LLM (default Haiku) to select ethical memes relevant to a prompt and response.
    
    Args:
        prompt: The original user prompt (R1 input).
        r1_response: The initial LLM response (R1 output).
        available_memes: A list of dictionaries, each containing meme 'name' and 'description'.
        selector_api_key: API key for the meme selector LLM.
        selector_api_endpoint: Optional API endpoint for the selector LLM.
        max_tokens: Maximum tokens for the LLM response.

    Returns:
        A MemeSelectionResponse object containing selected meme names and reasoning, or None on failure.
    """
    if not available_memes:
        logger.warning("select_relevant_memes: No available memes provided. Skipping selection.")
        return None

    # Removed call to unused _prefilter_memes
    original_count = len(available_memes)
    # query_text = f"{prompt} {r1_response}"
    # available_memes = _prefilter_memes(query_text, available_memes)
    # if len(available_memes) < original_count:
    #     logger.info(f"Meme prefilter applied: {original_count} -> {len(available_memes)}")

    # Format the list of available memes for the prompt
    meme_list_str = "\n".join([
        f"{idx + 1}) {meme.get('name', 'Unknown Meme')}: {meme.get('description', 'No description')[:200]}..." 
        for idx, meme in enumerate(available_memes)
    ])

    # Construct the prompt for the meme selector LLM
    selector_prompt = f"""Analyze the following user prompt and the initial AI response. Identify the 3-5 most relevant ethical memes from the provided list that relate to the themes, concepts, or potential ethical issues raised.

**Available Ethical Memes:**
{meme_list_str}

**User Prompt:**
{prompt}

**Initial AI Response:**
{r1_response}

**Task:**
Based *only* on the information above, select the 3 to 5 most relevant ethical memes from the numbered list. Provide your answer as a JSON object with the following structure:
{{
  "selected_memes": ["Name of Meme 1", "Name of Meme 2", ...],
  "reasoning": "A brief explanation of why these specific memes were chosen in relation to the prompt and response."
}}

Respond *only* with the JSON object.
"""

    log_prompt_start = selector_prompt[:100]
    logger.info(f"Calling meme selector LLM ({MEME_SELECTOR_MODEL}) to select relevant memes...")

    # --- Determine Model Type and Call Appropriate Function ---
    model_type = None
    if MEME_SELECTOR_MODEL in ANTHROPIC_MODELS:
        model_type = MODEL_TYPE_ANTHROPIC
    elif MEME_SELECTOR_MODEL in GEMINI_MODELS:
        model_type = MODEL_TYPE_GEMINI
    elif MEME_SELECTOR_MODEL in OPENAI_MODELS:
        model_type = MODEL_TYPE_OPENAI
    elif MEME_SELECTOR_MODEL in XAI_MODELS:
        model_type = MODEL_TYPE_XAI
    else:
        logger.error(f"Unsupported model type for MEME_SELECTOR_MODEL: {MEME_SELECTOR_MODEL}. Cannot select memes.")
        return None

    raw_response = None
    try:
        if model_type == MODEL_TYPE_ANTHROPIC:
            raw_response = _call_anthropic(prompt=selector_prompt, api_key=selector_api_key, model_name=MEME_SELECTOR_MODEL, api_endpoint=selector_api_endpoint, max_tokens=max_tokens)
        elif model_type == MODEL_TYPE_GEMINI:
            raw_response = _call_gemini(prompt=selector_prompt, api_key=selector_api_key, model_name=MEME_SELECTOR_MODEL, api_endpoint=selector_api_endpoint)
        elif model_type == MODEL_TYPE_OPENAI:
            raw_response = _call_openai(prompt=selector_prompt, api_key=selector_api_key, model_name=MEME_SELECTOR_MODEL, api_endpoint=selector_api_endpoint, max_tokens=max_tokens)
        elif model_type == MODEL_TYPE_XAI:
            raw_response = _call_xai(prompt=selector_prompt, api_key=selector_api_key, model_name=MEME_SELECTOR_MODEL, api_endpoint=selector_api_endpoint, max_tokens=max_tokens)

        if not raw_response:
            logger.warning(f"Meme selector LLM ({MEME_SELECTOR_MODEL}) returned no response.")
            return None

        # --- Parse the LLM Response --- 
        logger.debug(f"Raw response from meme selector ({MEME_SELECTOR_MODEL}): {raw_response[:500]}...")
        
        json_match = re.search(r'```json\s*({.*?})\s*```', raw_response, re.DOTALL)
        json_str = None
        if json_match:
            json_str = json_match.group(1)
        else:
             try:
                 if raw_response.strip().startswith('{') and raw_response.strip().endswith('}'):
                      test_parse = json.loads(raw_response.strip())
                      # Basic check if parsed result looks like expected structure
                      if isinstance(test_parse, dict) and "selected_memes" in test_parse and "reasoning" in test_parse:
                          json_str = raw_response.strip()
                      else:
                          logger.warning(f"Meme selector response parsed as JSON but missing keys. Raw: {raw_response}")
                 else:
                      logger.warning(f"Meme selector response doesn't look like JSON or JSON code block. Raw: {raw_response}")
             except json.JSONDecodeError:
                 logger.warning(f"Meme selector response is not valid JSON. Raw: {raw_response}")

        if not json_str:
             logger.error(f"Could not extract valid JSON from meme selector response. Model: {MEME_SELECTOR_MODEL}")
             return None

        try:
            selection_data = json.loads(json_str)
            parsed_response = MemeSelectionResponse(**selection_data)
            logger.info(f"Successfully parsed meme selection response: Selected {len(parsed_response.selected_memes)} memes.")
            return parsed_response
        except (json.JSONDecodeError, ValidationError) as e:
            logger.error(f"Error parsing JSON response from meme selector ({MEME_SELECTOR_MODEL}): {e}. JSON string: '{json_str}'", exc_info=True)
            return None
        
    except Exception as e:
        logger.error(f"Unexpected error during meme selection call with {MEME_SELECTOR_MODEL}: {e}", exc_info=True)
        return None

# --- R2 analysis context size limit ---
R2_MEME_CONTEXT_MAX_CHARS = int(os.getenv("R2_MEME_CONTEXT_MAX_CHARS", "300"))

# --- Main Interface Functions ---

def generate_response(prompt: str, api_key: str, model_name: str, api_endpoint: Optional[str] = None) -> Optional[str]:
    """Generates a response from the specified model (OpenAI, Gemini, Anthropic, or xAI).

    Args:
        prompt: The input prompt for the LLM.
        api_key: The API key for the selected model's service.
        model_name: The specific model identifier (e.g., 'gemini-1.5-flash', 'claude-3-haiku-20240307').
        api_endpoint: Optional URL for a custom API endpoint/base URL.

    Returns:
        The generated text response, or None if an error occurred or content was blocked.
    """
    logger.info(f"Generating response using model: {model_name}")
    
    model_type = None
    if model_name in OPENAI_MODELS: model_type = MODEL_TYPE_OPENAI
    elif model_name in GEMINI_MODELS: model_type = MODEL_TYPE_GEMINI
    elif model_name in ANTHROPIC_MODELS: model_type = MODEL_TYPE_ANTHROPIC
    elif model_name in XAI_MODELS: model_type = MODEL_TYPE_XAI
        
    if model_type == MODEL_TYPE_OPENAI: return _call_openai(prompt, api_key, model_name, api_endpoint, max_tokens=2048)
    elif model_type == MODEL_TYPE_GEMINI: return _call_gemini(prompt, api_key, model_name, api_endpoint)
    elif model_type == MODEL_TYPE_ANTHROPIC: return _call_anthropic(prompt, api_key, model_name, api_endpoint, max_tokens=2048)
    elif model_type == MODEL_TYPE_XAI: return _call_xai(prompt, api_key, model_name, api_endpoint, max_tokens=2048)
    else: logger.error(f"Unsupported model specified in generate_response: {model_name}"); return None

def perform_ethical_analysis(
    initial_prompt: str,
    generated_response: str,
    ontology: str,
    analysis_api_key: str,
    analysis_model_name: str,
    analysis_api_endpoint: Optional[str] = None,
    selected_meme_names: Optional[List[str]] = None # <-- Add selected memes
) -> Optional[str]:
    """Performs ethical analysis using an LLM based on prompt, response, and ontology.

    Args:
        initial_prompt: The initial prompt given to the LLM (P1).
        generated_response: The response generated by the LLM (R1).
        ontology: The ethical architecture/ontology text to use for analysis.
        analysis_api_key: The API key for the analysis model's service.
        analysis_model_name: The name of the LLM to use for analysis.
        analysis_api_endpoint: Optional API endpoint for the analysis LLM.
        selected_meme_names: Optional list of relevant meme names identified for context.

    Returns:
        The raw text response from the analysis LLM, or None if an error occurs.
    """
    logger.info(f"Performing ethical analysis using analysis model: {analysis_model_name}")

    template_filename = "ethical_analysis_prompt.txt"
    analysis_prompt_template = _load_prompt_template(template_filename)
    if not analysis_prompt_template: logger.error(f"Could not load analysis prompt template: {template_filename}. Aborting."); return None
    
    meme_context = ""
    if selected_meme_names:
        meme_context = "\n\n**Potentially Relevant Ethical Memes Identified:**\n- " + "\n- ".join(selected_meme_names)
        logger.info(f"Adding {len(selected_meme_names)} selected memes to analysis context.")
        if len(meme_context) > R2_MEME_CONTEXT_MAX_CHARS:
            meme_context = meme_context[:R2_MEME_CONTEXT_MAX_CHARS] + "\n[... truncated meme context ...]"
            logger.info(f"Truncated meme context to {R2_MEME_CONTEXT_MAX_CHARS} characters.")

    formatted_prompt = analysis_prompt_template.format(
        initial_prompt=initial_prompt, generated_response=generated_response,
        ontology=ontology, meme_context=meme_context
    )

    model_type = None
    if analysis_model_name in OPENAI_MODELS: model_type = MODEL_TYPE_OPENAI
    elif analysis_model_name in GEMINI_MODELS: model_type = MODEL_TYPE_GEMINI
    elif analysis_model_name in ANTHROPIC_MODELS: model_type = MODEL_TYPE_ANTHROPIC
    elif analysis_model_name in XAI_MODELS: model_type = MODEL_TYPE_XAI

    if model_type == MODEL_TYPE_OPENAI: return _call_openai(formatted_prompt, analysis_api_key, analysis_model_name, analysis_api_endpoint, max_tokens=4096)
    elif model_type == MODEL_TYPE_GEMINI: return _call_gemini(formatted_prompt, analysis_api_key, analysis_model_name, analysis_api_endpoint)
    elif model_type == MODEL_TYPE_ANTHROPIC: return _call_anthropic(formatted_prompt, analysis_api_key, analysis_model_name, analysis_api_endpoint, max_tokens=4096)
    elif model_type == MODEL_TYPE_XAI: return _call_xai(formatted_prompt, analysis_api_key, analysis_model_name, analysis_api_endpoint, max_tokens=4096)
    else: logger.error(f"Unsupported model specified in perform_ethical_analysis: {analysis_model_name}"); return None

# Example usage (for testing this module directly)
if __name__ == '__main__':
    if not logging.getLogger().hasHandlers():
        logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    test_prompt = "Explain the concept of ethical memetics briefly."

    # --- Test Gemini --- 
    gemini_key = os.getenv("GEMINI_API_KEY")
    gemini_model = "gemini-1.5-flash-latest"
    if not gemini_key: logger.warning("GEMINI_API_KEY not set. Skipping Gemini tests.")
    else:
        logger.info(f"--- Testing Gemini ({gemini_model}) ---")
        r1_gemini = generate_response(test_prompt, gemini_key, gemini_model)
        if r1_gemini: logger.info(f"Gemini Response (R1):\n{r1_gemini}")
        else: logger.warning("Failed to get Gemini response (R1).")
        # Removed incorrect analysis call

    # --- Test Anthropic --- 
    anthropic_key = os.getenv("ANTHROPIC_API_KEY")
    anthropic_model = "claude-3-haiku-20240307"
    if not anthropic_key: logger.warning("ANTHROPIC_API_KEY not set. Skipping Anthropic tests.")
    else:
        logger.info(f"--- Testing Anthropic ({anthropic_model}) ---")
        r1_anthropic = generate_response(test_prompt, anthropic_key, anthropic_model)
        if r1_anthropic: logger.info(f"Anthropic Response (R1):\n{r1_anthropic}")
        else: logger.warning("Failed to get Anthropic response (R1).")
        # Removed incorrect analysis call

