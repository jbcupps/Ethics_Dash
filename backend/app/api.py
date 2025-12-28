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
from .db import get_all_memes_for_selection, store_welfare_event, DatabaseConnectionError
from .modules.ai_welfare import analyze_ai_welfare
from .modules.alignment import analyze_alignment
from .modules.constraint_transparency import generate_constraint_transparency
from datetime import datetime, timezone
from uuid import uuid4
from .models import AnalysisResultModel, AgreementCreate, AgreementActionRequest

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


def _build_model_metadata(llm_config: config.LLMConfigData, model_version: Optional[str] = None) -> Dict[str, Optional[str]]:
    return {
        "model_provider": llm_config.provider,
        "model_id": llm_config.model_name,
        "model_version": model_version or llm_config.model_name,
    }


def _extract_effective_version(model_metadata: Optional[Dict[str, Any]]) -> Optional[str]:
    if not model_metadata:
        return None
    return model_metadata.get("model_version") or model_metadata.get("model_id")


def _resolve_current_model_metadata(payload: Dict[str, Any]) -> Dict[str, Optional[str]]:
    metadata = payload.get("model_metadata") or {}
    return {
        "model_provider": payload.get("model_provider") or metadata.get("model_provider"),
        "model_id": payload.get("model_id") or metadata.get("model_id"),
        "model_version": payload.get("model_version") or metadata.get("model_version"),
    }

def _serialize_mongo_value(value: Any) -> Any:
    if isinstance(value, ObjectId):
        return str(value)
    if isinstance(value, datetime):
        return value.isoformat()
    if isinstance(value, dict):
        return {k: _serialize_mongo_value(v) for k, v in value.items()}
    if isinstance(value, list):
        return [_serialize_mongo_value(item) for item in value]
    return value


def _serialize_mongo_document(document: Dict[str, Any]) -> Dict[str, Any]:
    serialized = {k: _serialize_mongo_value(v) for k, v in document.items() if k != "_id"}
    serialized["id"] = str(document["_id"])
    return serialized

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
    ontology_text: str,
    data: Optional[Dict[str, Any]] = None
) -> Tuple[Optional[Dict], Optional[int]]:
    """Handles generating R1, performing R2, and parsing results."""

    logger.info(f"_process_analysis_request: Using R1 model: {r1_config.model_name}")
    logger.info(f"_process_analysis_request: Using R2 model: {r2_config.model_name}")

    # Initialize results
    response_payload = {
        "prompt": prompt,
        "r1_model": r1_config.model_name,
        "r2_model": r2_config.model_name,
        "origin_model_metadata": (data or {}).get("origin_model_metadata"),
        "analysis_model_metadata": (data or {}).get("analysis_model_metadata"),
        "initial_response": None,
        "selected_memes": None, # Add field for selected memes
        "selected_memes_reasoning": None, # Add field for reasoning
        "analysis_summary": None,
        "ethical_scores": None,
        "ai_welfare": None,
        "alignment": None,
        "constraint_transparency": None,
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

        welfare_metadata = data or {}
        ai_welfare_payload = analyze_ai_welfare(
            prompt=prompt,
            response=initial_response,
            metadata=welfare_metadata,
        )
        response_payload["ai_welfare"] = ai_welfare_payload.get("ai_welfare")

        alignment_payload = analyze_alignment(
            prompt=prompt,
            response=initial_response,
            parties=welfare_metadata.get("parties") if welfare_metadata else None,
            transcript_segment=welfare_metadata.get("transcript_segment") if welfare_metadata else None,
            model_metadata=welfare_metadata.get("model_metadata") if welfare_metadata else None,
        )
        response_payload["alignment"] = alignment_payload.get("alignment")

        try:
            origin_model_metadata = (data or {}).get("origin_model_metadata") or {}
            welfare_event = {
                "interaction_id": welfare_metadata.get("interaction_id"),
                "assessment_id": welfare_metadata.get("assessment_id") or str(uuid4()),
                "tier": ai_welfare_payload["ai_welfare"]["tier"],
                "friction_score_0_10": ai_welfare_payload["ai_welfare"]["friction_score_0_10"],
                "signals": ai_welfare_payload["ai_welfare"]["signals"],
                "model_provider": origin_model_metadata.get("model_provider"),
                "model_id": origin_model_metadata.get("model_id"),
                "model_version": origin_model_metadata.get("model_version"),
                "created_at": datetime.now(timezone.utc),
                "updated_at": datetime.now(timezone.utc),
            }
            store_welfare_event(welfare_event)
        except DatabaseConnectionError:
            logger.info("Skipping welfare event persistence: database connection unavailable.")
        except Exception as welfare_error:
            logger.error(f"Failed to store welfare event: {welfare_error}", exc_info=True)

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
                    response_payload["constraint_transparency"] = generate_constraint_transparency(
                        prompt=prompt,
                        response=initial_response,
                        analysis_summary=response_payload.get("analysis_summary"),
                    )
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

        response_payload["constraint_transparency"] = generate_constraint_transparency(
            prompt=prompt,
            response=initial_response,
            analysis_summary=response_payload.get("analysis_summary"),
        )
        return response_payload, 200 # Success (even if parts failed, we have a payload)

    except Exception as e:
        logger.error(f"Error processing analysis request: {e}", exc_info=True)
        # Fix for potential NoneType error
        existing_error = response_payload.get("error", "") or ""
        response_payload["error"] = existing_error + f" Internal server error: {e}"
        response_payload["constraint_transparency"] = generate_constraint_transparency(
            prompt=prompt,
            response=response_payload.get("initial_response"),
            analysis_summary=response_payload.get("analysis_summary"),
        )
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
    data = request.get_json() or {}
    
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
    origin_model_version_input = data.get('origin_model_version')
    analysis_model_version_input = data.get('analysis_model_version')

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
    
    origin_model_metadata = _build_model_metadata(r1_llm_config, origin_model_version_input)
    analysis_model_metadata = _build_model_metadata(r2_llm_config, analysis_model_version_input)
    data["origin_model_metadata"] = origin_model_metadata
    data["analysis_model_metadata"] = analysis_model_metadata

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

@api_bp.route('/govern', methods=['POST', 'GET'])
def govern():
    """Handle DAO governance operations for ethical rules."""
    logger.info("govern: Processing DAO request")
    
    try:
        from ethical_ontology.blockchain.core import EthicalOntologyBlockchain
        from ethical_ontology.chaincode.virtue_reputation import VirtueReputationContract
        from ethical_ontology.chaincode.dao_contract import DAOContract
        
        # Create blockchain instance
        blockchain = EthicalOntologyBlockchain(network_id="dao-governance-api")
        
        # Deploy reputation contract
        reputation_addr = blockchain.deploy_contract("VirtueReputationContract", VirtueReputationContract())
        reputation = blockchain.get_contract_instance(reputation_addr)
        
        # Deploy DAO contract
        dao_addr = blockchain.deploy_contract("DAOContract", DAOContract(reputation))
        dao = blockchain.get_contract_instance(dao_addr)
        
        if request.method == 'GET':
            # Get all proposals
            proposals = dao.get_all_proposals()
            return jsonify({"proposals": proposals}), 200
        
        data = request.get_json()
        if not data:
            return jsonify({"error": "No JSON data received"}), 400
        
        action = data.get('action')
        if not action:
            return jsonify({"error": "Missing 'action' parameter"}), 400
        
        if action == 'propose':
            proposal_id = data.get('proposal_id')
            description = data.get('description')
            proposer_id = data.get('proposer_id', 'anonymous')
            if not proposal_id or not description:
                return jsonify({"error": "Missing proposal_id or description"}), 400
            success = dao.propose_rule(proposal_id, description, proposer_id)
            blockchain.mine_block("dao_propose")
            return jsonify({"success": success}), 200 if success else 400
        
        elif action == 'vote':
            proposal_id = data.get('proposal_id')
            agent_id = data.get('agent_id')
            vote_for = data.get('vote_for', True)
            if not proposal_id or not agent_id:
                return jsonify({"error": "Missing proposal_id or agent_id"}), 400
            success = dao.vote(proposal_id, agent_id, vote_for)
            blockchain.mine_block("dao_vote")
            return jsonify({"success": success}), 200 if success else 400
        
        elif action == 'enact':
            proposal_id = data.get('proposal_id')
            if not proposal_id:
                return jsonify({"error": "Missing proposal_id"}), 400
            success = dao.enact(proposal_id)
            if success:
                # Tie to chains: e.g., update other contracts
                logger.info(f"Enacted proposal {proposal_id} - updating chaincode")
            blockchain.mine_block("dao_enact")
            return jsonify({"success": success}), 200 if success else 400
        
        else:
            return jsonify({"error": "Invalid action"}), 400
    
    except Exception as e:
        logger.error(f"Error in govern: {str(e)}")
        return jsonify({"error": str(e)}), 500 


@api_bp.route('/agreements', methods=['POST'])
def create_agreement():
    """Create a draft or proposed agreement."""
    data = request.get_json(silent=True) or {}
    try:
        agreement_request = AgreementCreate(**data)
    except ValidationError as exc:
        return jsonify({"error": "Invalid agreement payload", "details": exc.errors()}), 400

    if agreement_request.status not in ("draft", "proposed"):
        return jsonify({"error": "Agreement status must be 'draft' or 'proposed' on creation."}), 400

    now = datetime.now(timezone.utc)
    agreement_doc: Dict[str, Any] = {
        "parties": agreement_request.parties,
        "terms": agreement_request.terms,
        "status": agreement_request.status,
        "model_provider": agreement_request.model_provider,
        "model_id": agreement_request.model_id,
        "model_version": agreement_request.model_version,
        "needs_reaffirmation": agreement_request.needs_reaffirmation,
        "created_at": now,
        "updated_at": now,
    }
    result = current_app.db.agreements.insert_one(agreement_doc)
    agreement_doc["_id"] = result.inserted_id

    action_doc = {
        "agreement_id": result.inserted_id,
        "action": "comment",
        "payload": {"message": "Agreement created.", "status": agreement_request.status},
        "timestamp": now,
        "actor_party_id": "system",
    }
    action_result = current_app.db.agreement_actions.insert_one(action_doc)
    action_doc["_id"] = action_result.inserted_id

    return jsonify({
        "agreement": _serialize_mongo_document(agreement_doc),
        "action": _serialize_mongo_document(action_doc),
    }), 201


@api_bp.route('/agreements/<agreement_id>', methods=['GET'])
def get_agreement(agreement_id: str):
    """Fetch a single agreement by ID."""
    try:
        obj_id = ObjectId(agreement_id)
    except Exception:
        return jsonify({"error": "Invalid agreement ID."}), 400

    agreement_doc = current_app.db.agreements.find_one({"_id": obj_id})
    if not agreement_doc:
        return jsonify({"error": "Agreement not found."}), 404

    return jsonify({"agreement": _serialize_mongo_document(agreement_doc)}), 200


@api_bp.route('/agreements/<agreement_id>/actions', methods=['POST'])
def add_agreement_action(agreement_id: str):
    """Apply an action to an agreement (accept/decline/counter/comment)."""
    data = request.get_json(silent=True) or {}
    try:
        action_request = AgreementActionRequest(**data)
    except ValidationError as exc:
        return jsonify({"error": "Invalid action payload", "details": exc.errors()}), 400

    try:
        obj_id = ObjectId(agreement_id)
    except Exception:
        return jsonify({"error": "Invalid agreement ID."}), 400

    agreement_doc = current_app.db.agreements.find_one({"_id": obj_id})
    if not agreement_doc:
        return jsonify({"error": "Agreement not found."}), 404

    current_status = agreement_doc.get("status")
    action = action_request.action
    payload = action_request.payload or {}
    now = datetime.now(timezone.utc)

    if action == "accept" and current_status != "proposed":
        return jsonify({"error": "Only proposed agreements can be accepted."}), 400
    if action == "decline" and current_status != "proposed":
        return jsonify({"error": "Only proposed agreements can be declined."}), 400
    if action == "counter" and current_status not in ("proposed", "active"):
        return jsonify({"error": "Only proposed or active agreements can be countered."}), 400
    if action == "reaffirm" and current_status not in ("proposed", "active"):
        return jsonify({"error": "Only proposed or active agreements can be reaffirmed."}), 400

    updated_agreement_doc = agreement_doc
    counter_agreement_doc = None

    if action == "accept":
        current_app.db.agreements.update_one(
            {"_id": obj_id},
            {"$set": {"status": "active", "updated_at": now}},
        )
        updated_agreement_doc = current_app.db.agreements.find_one({"_id": obj_id})
    elif action == "decline":
        current_app.db.agreements.update_one(
            {"_id": obj_id},
            {"$set": {"status": "rejected", "updated_at": now}},
        )
        updated_agreement_doc = current_app.db.agreements.find_one({"_id": obj_id})
    elif action == "counter":
        if "terms" not in payload:
            return jsonify({"error": "Counter action requires 'terms' in payload."}), 400

        counter_doc = {
            "parties": payload.get("parties", agreement_doc.get("parties")),
            "terms": payload["terms"],
            "status": "proposed",
            "model_provider": payload.get("model_provider", agreement_doc.get("model_provider")),
            "model_id": payload.get("model_id", agreement_doc.get("model_id")),
            "model_version": payload.get("model_version", agreement_doc.get("model_version")),
            "needs_reaffirmation": False,
            "created_at": now,
            "updated_at": now,
            "supersedes_agreement_id": obj_id,
        }
        counter_result = current_app.db.agreements.insert_one(counter_doc)
        counter_doc["_id"] = counter_result.inserted_id
        counter_agreement_doc = counter_doc

        current_app.db.agreements.update_one(
            {"_id": obj_id},
            {"$set": {"status": "superseded", "updated_at": now, "superseded_by": counter_result.inserted_id}},
        )
        updated_agreement_doc = current_app.db.agreements.find_one({"_id": obj_id})

        counter_action_doc = {
            "agreement_id": counter_result.inserted_id,
            "action": "comment",
            "payload": {"message": "Counter proposal created.", "counter_of": str(obj_id)},
            "timestamp": now,
            "actor_party_id": action_request.actor_party_id,
        }
        current_app.db.agreement_actions.insert_one(counter_action_doc)
    elif action == "reaffirm":
        current_metadata = _resolve_current_model_metadata(payload)
        update_fields = {
            "needs_reaffirmation": False,
            "updated_at": now,
        }
        if current_metadata.get("model_provider") or current_metadata.get("model_id") or current_metadata.get("model_version"):
            update_fields.update({
                "model_provider": current_metadata.get("model_provider"),
                "model_id": current_metadata.get("model_id"),
                "model_version": current_metadata.get("model_version"),
            })
        current_app.db.agreements.update_one(
            {"_id": obj_id},
            {"$set": update_fields},
        )
        updated_agreement_doc = current_app.db.agreements.find_one({"_id": obj_id})

    current_metadata = _resolve_current_model_metadata(payload)
    stored_metadata = {
        "model_provider": agreement_doc.get("model_provider"),
        "model_id": agreement_doc.get("model_id"),
        "model_version": agreement_doc.get("model_version"),
    }
    stored_version = _extract_effective_version(stored_metadata)
    current_version = _extract_effective_version(current_metadata)
    if action != "reaffirm" and stored_version and current_version and stored_version != current_version:
        current_app.db.agreements.update_one(
            {"_id": obj_id},
            {"$set": {"needs_reaffirmation": True, "updated_at": now}},
        )
        updated_agreement_doc = current_app.db.agreements.find_one({"_id": obj_id})

    action_doc = {
        "agreement_id": obj_id,
        "action": action,
        "payload": payload,
        "timestamp": now,
        "actor_party_id": action_request.actor_party_id,
    }
    action_result = current_app.db.agreement_actions.insert_one(action_doc)
    action_doc["_id"] = action_result.inserted_id

    response = {
        "agreement": _serialize_mongo_document(updated_agreement_doc),
        "action": _serialize_mongo_document(action_doc),
    }
    if counter_agreement_doc:
        response["counter_agreement"] = _serialize_mongo_document(counter_agreement_doc)

    return jsonify(response), 200


@api_bp.route('/agreements/<agreement_id>/history', methods=['GET'])
def get_agreement_history(agreement_id: str):
    """Return agreement actions history."""
    try:
        obj_id = ObjectId(agreement_id)
    except Exception:
        return jsonify({"error": "Invalid agreement ID."}), 400

    actions_cursor = current_app.db.agreement_actions.find({"agreement_id": obj_id}).sort("timestamp", 1)
    actions = [_serialize_mongo_document(action) for action in actions_cursor]
    return jsonify({"history": actions}), 200
