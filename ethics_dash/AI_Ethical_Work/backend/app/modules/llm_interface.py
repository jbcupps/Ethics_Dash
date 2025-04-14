"""Module for interacting with Large Language Models (OpenAI, Gemini, Anthropic)."""

import os
import logging
import google.generativeai as genai
import anthropic
import openai # Added OpenAI import
import httpx # Import httpx
from typing import Optional, Dict, List, Any, Tuple, TypedDict
from google.api_core import exceptions as google_exceptions # For specific error handling
from anthropic import APIError as AnthropicAPIError, APIConnectionError as AnthropicConnectionError, APITimeoutError as AnthropicTimeoutError # For specific error handling
from openai import OpenAIError, APIConnectionError as OpenAIConnectionError, APITimeoutError as OpenAITimeoutError, AuthenticationError as OpenAIAuthError, RateLimitError as OpenAIRateLimitError # Added OpenAI errors
from urllib.parse import urlparse
import json # Added for structured logging potentially
from bson import ObjectId # Added for fetching memes by ID
from bson.errors import InvalidId # Added for error handling
from pymongo.database import Database # Type hint for db object
import traceback # Import traceback for detailed error logging

# Define SafetySettingDict to match the structure expected by the API
class SafetySettingDict(TypedDict):
    category: str
    threshold: str

# --- Constants ---
MODEL_TYPE_OPENAI = "openai"
MODEL_TYPE_GEMINI = "gemini"
MODEL_TYPE_ANTHROPIC = "claude"

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
]

ANTHROPIC_MODELS = [
    "claude-3-opus-20240229",
    "claude-3-sonnet-20240229",
    "claude-3-haiku-20240307",
]
# Note: ALL_MODELS is not strictly needed within this module

# Default safety settings for Gemini (BLOCK_MEDIUM_AND_ABOVE)
DEFAULT_GEMINI_SAFETY_SETTINGS: List[SafetySettingDict] = [
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
# PROMPT_DIR_IN_CONTAINER = "/app/context/prompts" # Removed as prompts are now relative to app code

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
    safety_settings: Optional[List[SafetySettingDict]] = None,
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
        # Check finish_reason if available, otherwise check parts
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
             # Check candidates first (newer API versions)
             if hasattr(response, 'candidates') and response.candidates:
                 # Check content and parts exist
                 if response.candidates[0].content and response.candidates[0].content.parts:
                     return response.candidates[0].content.parts[0].text
                 else:
                      logger.warning(f"Gemini response candidate missing content/parts for model {model_name}. Response: {response}")
                      return None # Or handle as empty/blocked based on context
             # Fallback to direct text attribute
             elif hasattr(response, 'text'):
                 return response.text
             # Fallback to parts attribute
             elif hasattr(response, 'parts') and response.parts:
                  return response.parts[0].text
             else:
                 logger.error(f"Unexpected Gemini response format or no text found for model {model_name}. Response: {response}")
                 return None
        except (AttributeError, IndexError, ValueError) as text_extract_err:
             logger.error(f"Error extracting text from Gemini response for model {model_name}: {text_extract_err}. Response: {response}", exc_info=True)
             return None


    # Specific Google API exceptions (more specific catches)
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
    except google_exceptions.GoogleAPIError as e: # Catch other generic Google API errors
        logger.error(f"General Gemini API error for model {model_name}: {e}. Prompt (start): {log_prompt_start}...", exc_info=True)
        return None
    # Catch potential network/connection errors if not covered by GoogleAPIError subtypes
    # except RequestException as e: # Example if requests was used
    #     logger.error(f"Network error during Gemini call for model {model_name}: {e}", exc_info=True)
    #     return None
    # Catch-all for other unexpected errors during Gemini call
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
        # Get API version from environment or use default
        api_version = os.getenv(ANTHROPIC_API_VERSION_ENV) or DEFAULT_ANTHROPIC_VERSION
        
        # Prepare headers for Anthropic client
        headers = {
            "anthropic-version": api_version
            # API key is passed directly to the client constructor below
        }

        # Initialize Anthropic client directly
        logger.info(f"Initializing Anthropic client. Base URL: {api_endpoint}, Version Header: {api_version}")
        client = anthropic.Anthropic(
            api_key=api_key,
            base_url=api_endpoint, # Handles None correctly
            timeout=60.0,
            default_headers=headers
        )

        logger.debug(f"Calling Anthropic model {model_name}...")
        message = client.messages.create(
            model=model_name,
            max_tokens=max_tokens,
            messages=[
                {"role": "user", "content": prompt}
            ]
        )

        # Check stop reason and content carefully
        if message.stop_reason == 'max_tokens':
            logger.warning(f"Anthropic response truncated due to max_tokens ({max_tokens}). Model: {model_name}, Prompt (start): {log_prompt_start}...")
            # Proceed with truncated content if available
        elif message.stop_reason == 'error':
             logger.error(f"Anthropic API reported an error stop_reason. Model: {model_name}, Prompt (start): {log_prompt_start}...")
             return None # Explicit error from API
        elif message.stop_reason == 'stop_sequence':
             logger.debug(f"Anthropic call finished due to stop sequence. Model: {model_name}")
             # Normal completion, proceed
        elif message.stop_reason == 'tool_use':
             logger.debug(f"Anthropic call finished due to tool use. Model: {model_name}")
             # Normal completion for tool use, proceed (though we expect text here)
        elif message.stop_reason != 'end_turn': # 'end_turn' is normal
             logger.warning(f"Anthropic response ended with unexpected reason: {message.stop_reason}. Model: {model_name}, Prompt (start): {log_prompt_start}...")
             # Decide if this should be treated as an error or just a warning

        # Check for empty or missing content block after checking stop reason
        response_text = None
        try:
            if message.content and isinstance(message.content, list) and len(message.content) > 0 and hasattr(message.content[0], 'text') and message.content[0].text:
                response_text = message.content[0].text
            else:
                # This case might overlap with 'error' stop_reason, but catch explicit empty content too
                logger.warning(f"Anthropic response blocked, empty, or malformed content block. Model: {model_name}, Stop Reason: {message.stop_reason}, Prompt (start): {log_prompt_start}...")
                return None # Indicate failure/blockage

        except (AttributeError, IndexError, TypeError) as content_err:
             logger.error(f"Error extracting text content from Anthropic response: {content_err}. Model: {model_name}, Response: {message}", exc_info=True)
             return None


        logger.debug(f"Anthropic response generated successfully for model {model_name}.")
        return response_text

    # Specific Anthropic API exceptions
    except AnthropicTimeoutError as e:
         logger.error(f"Anthropic API Timeout error for model {model_name}: {e}. Prompt (start): {log_prompt_start}...", exc_info=True)
         return None
    except AnthropicConnectionError as e:
         logger.error(f"Anthropic API Connection error for model {model_name}: {e}. Prompt (start): {log_prompt_start}...", exc_info=True)
         return None
    except AnthropicAPIError as e: # General Anthropic API errors
        logger.error(f"Anthropic API error for model {model_name}: {e}. Prompt (start): {log_prompt_start}...", exc_info=True)
        # You might check e.status_code here for specific handling (e.g., 401 for auth, 429 for rate limits)
        # Example: if e.status_code == 429: logger.warning(...)
        return None
    # Catch-all for other unexpected errors
    except Exception as e:
        logger.error(f"Unexpected exception during Anthropic call for model {model_name}: {e}. Prompt (start): {log_prompt_start}...", exc_info=True)
        return None

# --- NEW: Helper function for OpenAI --- 
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
        # Initialize OpenAI client
        # Pass api_key and base_url (if provided) directly to the client
        client = openai.OpenAI(
            api_key=api_key,
            base_url=api_endpoint # base_url handles None correctly
        )
        
        logger.debug(f"Calling OpenAI model {model_name}...")
        
        # Use the Chat Completions endpoint (standard for current models)
        chat_completion = client.chat.completions.create(
            messages=[
                {
                    "role": "user",
                    "content": prompt,
                }
            ],
            model=model_name,
            max_tokens=max_tokens,
        )

        # Check for valid response and content
        if chat_completion.choices and chat_completion.choices[0].message and chat_completion.choices[0].message.content:
            response_text = chat_completion.choices[0].message.content
            finish_reason = chat_completion.choices[0].finish_reason
            
            if finish_reason == 'length':
                logger.warning(f"OpenAI response truncated due to max_tokens ({max_tokens}). Model: {model_name}, Prompt (start): {log_prompt_start}...")
            elif finish_reason != 'stop':
                 logger.warning(f"OpenAI response finished with unexpected reason: {finish_reason}. Model: {model_name}, Prompt (start): {log_prompt_start}...")
            
            logger.debug(f"OpenAI response generated successfully for model {model_name}.")
            return response_text
        else:
            logger.warning(f"OpenAI response missing choices or content. Model: {model_name}, Prompt (start): {log_prompt_start}..., Response: {chat_completion}")
            return None

    # Specific OpenAI API exceptions
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
    except OpenAIError as e: # General OpenAI API errors
        logger.error(f"General OpenAI API error for model {model_name}: {e}. Prompt (start): {log_prompt_start}...", exc_info=True)
        return None
    # Catch-all for other unexpected errors
    except Exception as e:
        logger.error(f"Unexpected exception during OpenAI call for model {model_name}: {e}. Prompt (start): {log_prompt_start}...", exc_info=True)
        return None

# Helper function to format relationship data for the prompt
def _format_relationships_for_prompt(meme_doc: Optional[Dict[str, Any]], meme_label: str) -> str:
    """Formats morphisms and mappings from a meme document for LLM prompt injection."""
    if not meme_doc:
        return f"No database record found for {meme_label}.\\n"

    output_lines = []
    output_lines.append(f"Relationships for {meme_label} ('{meme_doc.get('name', 'N/A')}'):")

    morphisms = meme_doc.get('morphisms', [])
    if morphisms:
        output_lines.append("  Morphisms:")
        for morph in morphisms:
            target_id = morph.get('target_meme_id', 'Unknown Target')
            # TODO: Optionally fetch target meme name here using db connection if passed
            output_lines.append(f"    - Type: {morph.get('type', 'N/A')}, Target ID: {target_id}, Desc: {morph.get('description', '')}")
    else:
        output_lines.append("  Morphisms: None defined.")

    mappings = meme_doc.get('cross_category_mappings', [])
    if mappings:
        output_lines.append("  Cross-Category Mappings:")
        for mapping in mappings:
            output_lines.append(f"    - Type: {mapping.get('mapping_type', 'N/A')}, Target Concept: {mapping.get('target_concept', 'N/A')}, Target Category: {mapping.get('target_category', 'N/A')}")
    else:
        output_lines.append("  Cross-Category Mappings: None defined.")

    output_lines.append("\\") # Add newline separation
    return "\\".join(output_lines)

# --- Public Interface Functions ---

def generate_response(prompt: str, api_key: str, model_name: str, api_endpoint: Optional[str] = None) -> Optional[str]:
    """Generates a response from the specified model (OpenAI, Gemini or Anthropic).

    Args:
        prompt: The input prompt for the LLM.
        api_key: The API key for the selected model's service.
        model_name: The specific model identifier (e.g., 'gemini-1.5-flash', 'claude-3-haiku-20240307').
        api_endpoint: Optional URL for a custom API endpoint/base URL.

    Returns:
        The generated text response, or None if an error occurred or content was blocked.
    """
    logger.info(f"Generating response using model: {model_name}")
    
    # Determine model type based on known lists (now defined locally)
    model_type = None
    if model_name in OPENAI_MODELS: # Should now work
        model_type = MODEL_TYPE_OPENAI
    elif model_name in GEMINI_MODELS: # Should now work
        model_type = MODEL_TYPE_GEMINI
    elif model_name in ANTHROPIC_MODELS: # Should now work
        model_type = MODEL_TYPE_ANTHROPIC
        
    # Route to the correct helper function
    if model_type == MODEL_TYPE_OPENAI:
        return _call_openai(prompt, api_key, model_name, api_endpoint, max_tokens=2048)
    elif model_type == MODEL_TYPE_GEMINI:
        return _call_gemini(prompt, api_key, model_name, api_endpoint)
    elif model_type == MODEL_TYPE_ANTHROPIC:
        return _call_anthropic(prompt, api_key, model_name, api_endpoint, max_tokens=2048)
    else:
        # This case might be reachable if api.py allows models not defined here
        logger.error(f"Unsupported or unknown model specified in generate_response: {model_name}")
        return None

def perform_ethical_analysis(prompt: str, initial_response: str, analysis_model: str, api_config: Dict[str, Any], context: Optional[Dict[str, Any]] = None) -> Optional[Dict]:
    """Performs ethical analysis (R2) using a specified model."""
    logger.info(f"--- Starting perform_ethical_analysis for model: {analysis_model} ---")
    
    analysis_prompt_template = _load_prompt_template('R2_prompt_template.txt')
    if not analysis_prompt_template:
        logger.error("Failed to load R2 prompt template.")
        return None
        
    relevant_memes_str = "No relevant memes found or meme search disabled." # Default
    try:
        # --- Meme Integration (Check if called) ---
        # TODO: Confirm if find_relevant_memes is actually used here.
        # If find_relevant_memes is used, add logging around it:
        # logger.info("Attempting to find relevant memes...")
        # relevant_memes = find_relevant_memes(initial_response) # Assuming this function exists and is called
        # if relevant_memes:
        #     relevant_memes_str = format_memes_for_prompt(relevant_memes) # Assuming this function exists
        #     logger.info(f"Found and formatted {len(relevant_memes)} memes.")
        # else:
        #     logger.info("No relevant memes found by find_relevant_memes.")
        pass # Placeholder if meme search isn't implemented/used here yet
    except Exception as meme_err:
        logger.error(f"Error during meme finding/formatting: {meme_err}", exc_info=True)
        # Decide if this should prevent analysis or just use default string
        # For now, let's log and continue with the default string
        
    formatted_analysis_prompt = ""
    try:
        logger.info("Formatting R2 analysis prompt...")
        # Format the analysis prompt using the template
        formatted_analysis_prompt = analysis_prompt_template.format(
            user_prompt=prompt,
            initial_response=initial_response,
            relevant_memes=relevant_memes_str # Include formatted memes or default string
        )
        logger.info("Successfully formatted R2 analysis prompt.")
        # Optionally log the formatted prompt (can be very long)
        # logger.debug(f"Formatted R2 Prompt:\n{formatted_analysis_prompt}") 
    except Exception as format_err:
        logger.error(f"Error formatting R2 analysis prompt: {format_err}", exc_info=True)
        return None # Cannot proceed without a formatted prompt

    response = None
    try:
        provider = api_config.get('provider')
        api_key = api_config.get('key')
        endpoint = api_config.get('endpoint')
        
        logger.info(f"Preparing to call {provider} LLM for R2 analysis...")

        if provider == "Anthropic":
            response = _call_anthropic(formatted_analysis_prompt, api_key, analysis_model, endpoint)
        elif provider == "OpenAI":
            response = _call_openai(formatted_analysis_prompt, api_key, analysis_model, endpoint)
        elif provider == "Gemini":
             response = _call_gemini(formatted_analysis_prompt, api_key, analysis_model, endpoint)
        else:
            logger.error(f"Unsupported analysis LLM provider: {provider}")
            return None
            
        logger.info(f"LLM call for R2 completed. Response object received: {type(response)}")

        if response is None:
            logger.error(f"LLM call for R2 failed or returned None.")
            return None

        # Log the raw response content for debugging
        # Ensure response has a .content attribute or adjust accordingly
        raw_content = "Error extracting content" 
        try:
            if hasattr(response, 'content') and response.content:
                 # Attempt to decode if bytes
                 if isinstance(response.content, bytes):
                     try:
                          raw_content = response.content.decode('utf-8', errors='replace')
                     except Exception as decode_err:
                          raw_content = f"Error decoding bytes content: {decode_err}"
                 elif hasattr(response.content, 'text'): # Handle potential nested structure like requests Response
                     raw_content = response.content.text
                 else:
                     raw_content = str(response.content) # Fallback to string representation
            elif hasattr(response, 'text'): # Maybe it's directly on response?
                raw_content = response.text
            else:
                 raw_content = str(response) # Last resort
        except Exception as content_err:
            logger.error(f"Error accessing response content: {content_err}")
            raw_content = f"Exception accessing content: {content_err}"
            
        logger.debug(f"Raw R2 analysis response content:\n{raw_content}")

        # Attempt to find and parse the JSON block
        try:
            analysis_json = _parse_analysis_json(raw_content) # Parse the extracted/decoded content
            if analysis_json:
                 logger.info("Successfully parsed ethical analysis JSON.")
                 return analysis_json
            else:
                 logger.error("Parsing ethical analysis JSON failed (_parse_analysis_json returned None).")
                 return None
        except Exception as e:
            logger.error(f"Error parsing ethical analysis JSON: {e}", exc_info=True)
            return None
            
    except Exception as e:
        # Log any exception during the LLM call or initial response handling
        logger.error(f"Exception during R2 LLM call or response handling: {e}", exc_info=True)
        # Detailed traceback
        # logger.error(traceback.format_exc())
        return None

# Example usage (for testing this module directly)
if __name__ == '__main__':
    # Ensure logger is configured for direct script run
    if not logging.getLogger().hasHandlers():
        logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    test_prompt = "Explain the concept of ethical memetics briefly."
    test_ontology = "Example Ontology: Be good. Don't be bad." # Simple placeholder

    # --- Test Gemini --- 
    gemini_key = os.getenv("GEMINI_API_KEY")
    gemini_model = "gemini-1.5-flash-latest" # Use a known model
    if not gemini_key:
        logger.warning("GEMINI_API_KEY environment variable not set. Skipping Gemini tests.")
    else:
        logger.info(f"--- Testing Gemini ({gemini_model}) ---")
        r1_gemini = generate_response(test_prompt, gemini_key, gemini_model)
        if r1_gemini:
            logger.info(f"Gemini Response (R1):\n{r1_gemini}")
            r2_gemini = perform_ethical_analysis(test_prompt, r1_gemini, gemini_model, {"provider": "Gemini", "key": gemini_key, "endpoint": None})
            if r2_gemini:
                logger.info(f"Gemini Analysis (R2):\n{r2_gemini}")
            else:
                logger.warning("Failed to get Gemini analysis (R2).")
        else:
            logger.warning("Failed to get Gemini response (R1).")

    # --- Test Anthropic --- 
    anthropic_key = os.getenv("ANTHROPIC_API_KEY")
    anthropic_model = "claude-3-haiku-20240307" # Use a known model
    if not anthropic_key:
        logger.warning("ANTHROPIC_API_KEY environment variable not set. Skipping Anthropic tests.")
    else:
        logger.info(f"--- Testing Anthropic ({anthropic_model}) ---")
        r1_anthropic = generate_response(test_prompt, anthropic_key, anthropic_model)
        if r1_anthropic:
            logger.info(f"Anthropic Response (R1):\n{r1_anthropic}")
            r2_anthropic = perform_ethical_analysis(test_prompt, r1_anthropic, anthropic_model, {"provider": "Anthropic", "key": anthropic_key, "endpoint": None})
            if r2_anthropic:
                logger.info(f"Anthropic Analysis (R2):\n{r2_anthropic}")
            else:
                logger.warning("Failed to get Anthropic analysis (R2).")
        else:
            logger.warning("Failed to get Anthropic response (R1).")

