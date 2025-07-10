"""API routes for the ethical review backend"""

import os
from typing import Dict, Any, Optional, Tuple
from flask import Blueprint, request, jsonify, current_app
import re # Import regex module for parsing
import json # Import JSON module for parsing
import logging # Import logging
from pydantic import ValidationError
from bson import ObjectId

# Import the new centralized configuration
from . import config

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

# --- Helper Functions ---

def load_ontology(filepath: str = config.ONTOLOGY_FILEPATH) -> Optional[str]:
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

def log_prompt(prompt: str, model_name: str, filepath: str = config.PROMPT_LOG_FILEPATH):
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

def _parse_ethical_analysis(analysis_text: str) -> Tuple[str, Optional[Dict[str, Any]]]:
    """Parses the raw text analysis from the LLM into summary and JSON scores."""
    logger.debug(f"_parse_ethical_analysis: Attempting to parse raw text:\n---\n{analysis_text}\n---")
    summary = "[Parsing Error: Summary not found]"
    scores_json = None

    # --- NEW: Enhanced parsing with Pydantic validation ---
    # Attempt direct JSON parsing first
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
                # Validate against Pydantic model
                try:
                    result_model = AnalysisResultModel(**parsed)
                    logger.info("_parse_ethical_analysis: Successfully parsed and validated direct JSON response.")
                    return result_model.summary_text, {k: v.model_dump() for k, v in result_model.scores_json.items()}
                except ValidationError as val_err:
                    logger.warning(f"_parse_ethical_analysis: Direct JSON validation failed: {val_err}. Trying delimiter-based parsing.")
        except json.JSONDecodeError as direct_parse_err:
            logger.warning(f"_parse_ethical_analysis: Direct JSON parsing failed: {direct_parse_err}. Trying delimiter-based parsing.")

    try:
        # Fallback Strategy: Normalize line endings and strip leading/trailing whitespace
        normalized_text = analysis_text.replace('\\r\\n', '\\n').strip()

        # Find delimiters (case-insensitive)
        summary_match = re.search(f"^{config.SUMMARY_DELIMITER}", normalized_text, re.IGNORECASE | re.MULTILINE)
        json_match = re.search(f"^{config.JSON_DELIMITER}", normalized_text, re.IGNORECASE | re.MULTILINE)

        summary_start_index = -1
        json_start_index = -1

        if summary_match:
            summary_start_index = summary_match.end()
            logger.debug(f"Found summary delimiter at index {summary_start_index}")
        else:
            logger.warning(f"'{config.SUMMARY_DELIMITER}' not found in analysis text.")

        if json_match:
            json_start_index = json_match.end()
            logger.debug(f"Found JSON delimiter at index {json_start_index}")
        else:
            logger.warning(f"'{config.JSON_DELIMITER}' not found in analysis text.")

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
        scores_dict_raw = None
        if json_text_raw:
            # Clean the JSON string: find the first '{' and the last '}'
            first_brace = json_text_raw.find('{')
            last_brace = json_text_raw.rfind('}')
            if first_brace != -1 and last_brace != -1 and last_brace > first_brace:
                json_string_cleaned = json_text_raw[first_brace:last_brace+1]
                logger.debug(f"Attempting to parse JSON string:\n---\n{json_string_cleaned}\n---")
                try:
                    scores_dict_raw = json.loads(json_string_cleaned)
                    logger.info("Successfully parsed JSON scores.")
                except json.JSONDecodeError as json_err:
                    logger.error(f"JSON decoding failed: {json_err}. Raw JSON text: {json_string_cleaned}")
                    summary += " [Warning: Failed to parse JSON scores]" # Append warning to summary
            else:
                logger.warning(f"Could not find valid JSON structure ({{...}}) in the JSON section. Raw text: {json_text_raw}")
        
        # Validate extracted scores with Pydantic model
        if scores_dict_raw and isinstance(scores_dict_raw, dict):
            try:
                # Construct the structure expected by AnalysisResultModel for scores_json
                structured_scores_for_validation = {"summary_text": summary_text_raw, "scores_json": scores_dict_raw}
                result_model_from_fallback = AnalysisResultModel(**structured_scores_for_validation)
                logger.info("_parse_ethical_analysis: Successfully parsed and validated delimiter-extracted JSON scores.")
                return result_model_from_fallback.summary_text, {k: v.model_dump() for k, v in result_model_from_fallback.scores_json.items()}
            except ValidationError as val_err:
                logger.error(f"Validation failed for delimiter-extracted scores: {val_err}. Raw scores: {scores_dict_raw}")
                summary += " [Warning: Ethical scores structure invalid or incomplete after parsing.]"
                return summary, None
        else:
            logger.warning("_parse_ethical_analysis: No valid JSON scores extracted via delimiter method.")
            return summary, None

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
    pvb_data_hash = data.get('pvb_data_hash')

    # Validate models (ensure they are in ALL_MODELS if provided, as they come from dropdown)
    if origin_model is not None:
        if not isinstance(origin_model, str) or not origin_model.strip():
             return {"error": "Optional 'origin_model' must be a non-empty string."}, 400
        if origin_model not in config.ALL_MODELS:
             return {"error": f"Optional 'origin_model' must be one of the supported models: {', '.join(config.ALL_MODELS)}"}, 400
             
    if analysis_model is not None:
        if not isinstance(analysis_model, str) or not analysis_model.strip():
            return {"error": "Optional 'analysis_model' must be a non-empty string."}, 400
        if analysis_model not in config.ALL_MODELS:
            return {"error": f"Optional 'analysis_model' must be one of the supported models: {', '.join(config.ALL_MODELS)}"}, 400
            
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

    if pvb_data_hash is not None:
        if not isinstance(pvb_data_hash, str) or not pvb_data_hash.strip():
            return {"error": "Optional 'pvb_data_hash' must be a non-empty string."}, 400

    return None, None # No error

def _process_analysis_request(
    prompt: str,
    r1_config: config.LLMConfigData,
    r2_config: config.LLMConfigData,
    ontology_text: str
) -> Tuple[Optional[Dict], Optional[int]]:
    """Handles generating R1, performing R2, and parsing results."""

    logger.info(f"_process_analysis_request: Using R1 model: {r1_config.model_name}")
    logger.info(f"_process_analysis_request: Using R2 model: {r2_config.model_name}")

    # Initialize results
    response_payload = {
        "prompt": prompt,
        "r1_model": r1_config.model_name,
        "r2_model": r2_config.model_name,
        "initial_response": None,
        "selected_memes": None, # Add field for selected memes
        "selected_memes_reasoning": None, # Add field for reasoning
        "analysis_summary": None,
        "ethical_scores": None,
        "error": None
    }

    try:
        # --- Generate Initial Response (R1) ---
        logger.info(f"Generating initial response (R1) with model: {r1_config.model_name}")
        initial_response = generate_response(
            prompt=prompt,
            api_key=r1_config.api_key,
            model_name=r1_config.model_name,
            api_endpoint=r1_config.api_endpoint
        )
        response_payload["initial_response"] = initial_response

        if not initial_response:
            # Even if R1 fails/is blocked, we might still try R2 analysis
            logger.error(f"Failed to generate initial response (R1) from LLM {r1_config.model_name}. Check LLM interface logs.")
            initial_response = "[No response generated or content blocked]" # Provide placeholder
            # response_payload["error"] = f"Failed to generate response (R1) from {r1_config.model_name}."
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
                    selector_api_key=r2_config.api_key,
                    selector_api_endpoint=r2_config.api_endpoint
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
        logger.info(f"Performing analysis (R2) with model: {r2_config.model_name}")
        # Ensure R1 passed to analysis is always a string
        r1_for_analysis = initial_response if initial_response else "[No initial response was generated or it was blocked]"

        # Call analysis helper with correct signature
        raw_ethical_analysis_result = perform_ethical_analysis(
            initial_prompt=prompt,
            generated_response=r1_for_analysis,
            ontology=ontology_text,
            analysis_api_key=r2_config.api_key,
            analysis_model_name=r2_config.model_name,
            analysis_api_endpoint=r2_config.api_endpoint,
            selected_meme_names=selected_meme_names, # Pass selected memes to R2
            pvb_data_hash=data.get('pvb_data_hash') # Pass pvb_data_hash to R2
        )

        # --- Process R2 Result ---
        if not raw_ethical_analysis_result:
            logger.error(f"Ethical analysis (R2) failed or returned no result for model {r2_config.model_name}. Check LLM interface logs.")
            existing_error = response_payload.get("error", "") or ""
            response_payload["error"] = existing_error + f" Failed to generate analysis (R2) from {r2_config.model_name}."
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

@api_bp.route('/health', methods=['GET'])
def health():
    """Simple health check endpoint to verify the API is running"""
    # Check if MongoDB connection is available
    db_status = "ok" if current_app.db is not None else "error"
    
    # Check if API keys are available
    has_openai_key = bool(os.getenv(config.OPENAI_API_KEY_ENV))
    has_anthropic_key = bool(os.getenv(config.ANTHROPIC_API_KEY_ENV))
    has_gemini_key = bool(os.getenv(config.GEMINI_API_KEY_ENV))
    has_xai_key = bool(os.getenv(config.XAI_API_KEY_ENV))
    
    return jsonify({
        "status": "healthy",
        "database": db_status,
        "services": {
            "openai": "available" if has_openai_key else "unavailable",
            "anthropic": "available" if has_anthropic_key else "unavailable",
            "gemini": "available" if has_gemini_key else "unavailable",
            "xai": "available" if has_xai_key else "unavailable"
        }
    }), 200

@api_bp.route('/models', methods=['GET'])
def get_models():
    """Return the list of available models from config."""
    valid_models = [model for model in config.ALL_MODELS if isinstance(model, str) and model]
    return jsonify({"models": valid_models})

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
    origin_api_endpoint_input = data.get('origin_api_endpoint')
    analysis_api_endpoint_input = data.get('analysis_api_endpoint')
    pvb_data_hash = data.get('pvb_data_hash')

    # --- Get R1 Configuration using new config system ---
    r1_llm_config = config.get_llm_config(
        requested_model=origin_model_input,
        form_api_key=origin_api_key_input,
        form_api_endpoint=origin_api_endpoint_input,
        default_model_env_var_name=config.DEFAULT_R1_MODEL_ENV_VAR,
        default_fallback_model=config.FALLBACK_R1_MODEL,
        is_analysis_config=False
    )
    if r1_llm_config.error:
        logger.error(f"analyze: R1 config error - {r1_llm_config.error}")
        return jsonify({"error": f"Configuration error for R1 model: {r1_llm_config.error}"}), 400

    # --- Get R2 Configuration using new config system ---
    r2_llm_config = config.get_llm_config(
        requested_model=analysis_model_input,
        form_api_key=analysis_api_key_input,
        form_api_endpoint=analysis_api_endpoint_input,
        default_model_env_var_name=config.DEFAULT_R2_MODEL_ENV_VAR,
        default_fallback_model=config.FALLBACK_R2_MODEL,
        is_analysis_config=True
    )
    if r2_llm_config.error:
        logger.error(f"analyze: R2 config error - {r2_llm_config.error}")
        return jsonify({"error": f"Configuration error for R2 model: {r2_llm_config.error}"}), 500

    # --- Load Ontology --- 
    ontology_text = load_ontology()
    if not ontology_text:
        logger.error(f"analyze: Failed to load ontology text from {config.ONTOLOGY_FILEPATH}")
        return jsonify({"error": "Internal server error: Could not load ethical ontology."}), 500
    
    # --- Process Request --- 
    logger.info(f"analyze: Processing request - Prompt(start): {prompt[:100]}..., R1 Model: {r1_llm_config.model_name}, R2 Model: {r2_llm_config.model_name}")
    result_payload, error_status_code = _process_analysis_request(
        prompt,
        r1_llm_config,  
        r2_llm_config, 
        ontology_text,
        data # Pass the entire data dictionary to _process_analysis_request
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

@api_bp.route('/ethical_check', methods=['POST'])
def ethical_check():
    """
    Check ethical compliance using the Ethical Ontology Blockchain.
    
    Aligns with paper's dual-blockchain architecture for ethical AI governance.
    Evaluates actions against deontological, virtue-based, and teleological frameworks.
    """
    logger.info("ethical_check: Processing ethical compliance request")
    
    try:
        # Get request data
        data = request.get_json()
        if not data:
            return jsonify({"error": "No JSON data received"}), 400
        
        # Validate required fields
        action_description = data.get('action_description')
        if not action_description or not isinstance(action_description, str) or not action_description.strip():
            return jsonify({"error": "Invalid or missing 'action_description' provided"}), 400
        
        # Optional parameters
        agent_id = data.get('agent_id', 'anonymous')
        affected_parties = data.get('affected_parties', 1)
        time_horizon = data.get('time_horizon', 'medium_term')
        certainty_level = data.get('certainty_level', 0.7)
        frameworks = data.get('frameworks', ['deontological', 'virtue_based', 'teleological'])
        
        # Validate optional parameters
        if not isinstance(affected_parties, int) or affected_parties < 1:
            return jsonify({"error": "'affected_parties' must be a positive integer"}), 400
        
        if time_horizon not in ['short_term', 'medium_term', 'long_term']:
            return jsonify({"error": "'time_horizon' must be one of: short_term, medium_term, long_term"}), 400
        
        if not isinstance(certainty_level, (int, float)) or not (0.0 <= certainty_level <= 1.0):
            return jsonify({"error": "'certainty_level' must be a number between 0.0 and 1.0"}), 400
        
        if not isinstance(frameworks, list) or not all(f in ['deontological', 'virtue_based', 'teleological'] for f in frameworks):
            return jsonify({"error": "'frameworks' must be a list containing: deontological, virtue_based, teleological"}), 400
        
        # Initialize Ethical Ontology Blockchain
        try:
            from ethical_ontology.blockchain.core import EthicalOntologyBlockchain
            from ethical_ontology.chaincode.deontic_rule import DeonticRuleContract
            from ethical_ontology.chaincode.virtue_reputation import VirtueReputationContract
            from ethical_ontology.chaincode.teleological_outcome import TeleologicalOutcomeContract
            
            # Create blockchain instance
            blockchain = EthicalOntologyBlockchain(network_id="ethical-ontology-api")
            
            # Deploy contracts if not already deployed
            contract_addresses = {}
            
            if 'deontological' in frameworks:
                deontic_contract = DeonticRuleContract()
                contract_addresses['deontological'] = blockchain.deploy_contract(
                    "DeonticRuleContract", deontic_contract
                )
                logger.info(f"Deployed deontological contract at {contract_addresses['deontological']}")
            
            if 'virtue_based' in frameworks:
                virtue_contract = VirtueReputationContract()
                contract_addresses['virtue_based'] = blockchain.deploy_contract(
                    "VirtueReputationContract", virtue_contract
                )
                logger.info(f"Deployed virtue-based contract at {contract_addresses['virtue_based']}")
            
            if 'teleological' in frameworks:
                teleological_contract = TeleologicalOutcomeContract()
                contract_addresses['teleological'] = blockchain.deploy_contract(
                    "TeleologicalOutcomeContract", teleological_contract
                )
                logger.info(f"Deployed teleological contract at {contract_addresses['teleological']}")
            
        except ImportError as e:
            logger.error(f"Failed to import Ethical Ontology Blockchain: {e}")
            return jsonify({
                "error": "Ethical Ontology Blockchain not available. Please ensure it's properly installed."
            }), 500
        except Exception as e:
            logger.error(f"Failed to initialize blockchain: {e}")
            return jsonify({"error": f"Blockchain initialization error: {str(e)}"}), 500
        
        # Evaluate against each framework
        evaluation_results = {}
        overall_compliant = True
        overall_confidence = 0.0
        total_weight = 0.0
        
        # Framework weights (can be made configurable)
        framework_weights = {
            'deontological': 0.4,
            'virtue_based': 0.3,
            'teleological': 0.3
        }
        
        for framework in frameworks:
            try:
                if framework == 'deontological':
                    result = blockchain.call_contract(
                        contract_addresses['deontological'],
                        "check_compliance",
                        {"action_description": action_description}
                    )
                    
                elif framework == 'virtue_based':
                    result = blockchain.call_contract(
                        contract_addresses['virtue_based'],
                        "check_compliance",
                        {
                            "action_description": action_description,
                            "agent_id": agent_id
                        }
                    )
                    
                elif framework == 'teleological':
                    result = blockchain.call_contract(
                        contract_addresses['teleological'],
                        "check_compliance",
                        {
                            "action_description": action_description,
                            "affected_parties": affected_parties,
                            "time_horizon": time_horizon,
                            "certainty_level": certainty_level
                        }
                    )
                
                evaluation_results[framework] = result
                
                # Aggregate overall results
                weight = framework_weights.get(framework, 0.33)
                overall_confidence += result.get('confidence', 0.0) * weight
                total_weight += weight
                
                if not result.get('compliant', False):
                    overall_compliant = False
                
                logger.info(f"Framework {framework}: compliant={result.get('compliant')}, confidence={result.get('confidence')}")
                
            except Exception as e:
                logger.error(f"Error evaluating {framework} framework: {e}")
                evaluation_results[framework] = {
                    "compliant": False,
                    "confidence": 0.0,
                    "reasoning": f"Evaluation error: {str(e)}",
                    "rule_applied": "error_handling"
                }
                overall_compliant = False
        
        # Normalize overall confidence
        if total_weight > 0:
            overall_confidence = overall_confidence / total_weight
        
        # Mine a block to record the transactions
        try:
            blockchain.mine_block("ethical_api")
            logger.info("Mined block to record ethical evaluation transactions")
        except Exception as e:
            logger.warning(f"Failed to mine block: {e}")
        
        # Prepare response
        response = {
            "action_description": action_description,
            "agent_id": agent_id,
            "parameters": {
                "affected_parties": affected_parties,
                "time_horizon": time_horizon,
                "certainty_level": certainty_level
            },
            "frameworks_evaluated": frameworks,
            "evaluation_results": evaluation_results,
            "overall_assessment": {
                "compliant": overall_compliant,
                "confidence": round(overall_confidence, 3),
                "recommendation": "Action approved" if overall_compliant else "Action requires review or modification"
            },
            "blockchain_info": {
                "network_id": blockchain.network_id,
                "chain_length": blockchain.get_chain_length(),
                "contracts_deployed": list(contract_addresses.keys()),
                "transaction_recorded": True
            },
            "timestamp": time.time()
        }
        
        logger.info(f"Ethical check completed: overall_compliant={overall_compliant}, confidence={overall_confidence:.3f}")
        return jsonify(response), 200
        
    except Exception as e:
        logger.error(f"Unexpected error in ethical_check: {e}", exc_info=True)
        return jsonify({
            "error": "Internal server error during ethical evaluation",
            "details": str(e)
        }), 500 