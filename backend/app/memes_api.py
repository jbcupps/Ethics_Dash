"""
API routes for Ethical Memes CRUD operations
"""

import logging
from datetime import datetime, timezone
from flask import Blueprint, request, jsonify, current_app
from bson import ObjectId
from bson.errors import InvalidId
from pydantic import ValidationError, TypeAdapter
import os
# import io # Unused
# import csv # Unused
import json
# import base64 # Unused
from werkzeug.utils import secure_filename
from typing import List, Dict, Any
from pymongo import UpdateOne

# Import the new centralized configuration
from . import config

# Import Pydantic models
from .models import EthicalMemeCreate, EthicalMemeUpdate, EthicalMemeInDB

# Import LLM function (adjust path/name if necessary)
# Ensure relevant API keys/configs are loaded in create_app
from .modules.llm_interface import generate_response # Only import what's needed
# Obsolete commented import removed

# Setup logger for this module
logger = logging.getLogger(__name__)

# --- Blueprint Definition ---
memes_bp = Blueprint('memes_api', __name__, url_prefix='/api/memes')

# Pydantic TypeAdapter for validating a list of memes
EthicalMemeListValidator = TypeAdapter(List[EthicalMemeCreate])

# --- Helper Function for parsing datetime from ISODate string ---
def parse_datetime(iso_str):
    """Parses ISO 8601 string (with Z) to datetime object."""
    if iso_str.endswith('Z'):
        iso_str = iso_str[:-1] + '+00:00'
    try:
        return datetime.fromisoformat(iso_str)
    except ValueError:
        logger.warning(f"Could not parse datetime string: {iso_str}")
        return datetime.now(timezone.utc) # Fallback or raise error

# --- CRUD Routes ---

@memes_bp.route('/', methods=['POST'])
def create_meme():
    """Create a new ethical meme."""
    if current_app.db is None:
        return jsonify({"error": "Database connection not available"}), 503

    data = request.get_json()
    if not data:
        return jsonify({"error": "No JSON data received"}), 400

    try:
        # Validate input data using Pydantic
        meme_data = EthicalMemeCreate(**data)
    except ValidationError as e:
        logger.warning(f"Meme creation validation failed: {e.errors()}")
        return jsonify({"error": "Invalid input data", "details": e.errors()}), 422 # Unprocessable Entity

    try:
        # Add metadata
        now = datetime.now(timezone.utc)
        # Use Pydantic model to structure the document to be inserted
        meme_to_insert = meme_data.model_dump(by_alias=True)
        meme_to_insert['metadata'] = {
            'created_at': now,
            'updated_at': now,
            'version': 1
        }
        
        result = current_app.db.ethical_memes.insert_one(meme_to_insert)
        
        # Fetch the newly created meme to return it
        new_meme_doc = current_app.db.ethical_memes.find_one({"_id": result.inserted_id})
        
        # Validate and structure the response using Pydantic
        response_meme = EthicalMemeInDB(**new_meme_doc)
        # Pydantic v2 uses model_dump_json for direct JSON string output
        return response_meme.model_dump_json(by_alias=True), 201, {'Content-Type': 'application/json'}
    
    except Exception as e:
        logger.error(f"Error creating meme: {e}", exc_info=True)
        return jsonify({"error": "Internal server error creating meme"}), 500

@memes_bp.route('/', methods=['GET'])
def get_memes():
    """Get all ethical memes."""
    if current_app.db is None:
        return jsonify({"error": "Database connection not available"}), 503

    processed_count = 0
    successful_count = 0
    memes_list = []
    try:
        memes_cursor = current_app.db.ethical_memes.find()
        
        for meme in memes_cursor:
            processed_count += 1
            meme_id_str = str(meme.get('_id', 'UNKNOWN_ID'))
            try:
                # Validate using Pydantic v2 model
                validated_meme_obj = EthicalMemeInDB(**meme)
                # Dump to JSON string (handles ObjectId), then load back to dict
                meme_json_str = validated_meme_obj.model_dump_json(by_alias=True)
                memes_list.append(json.loads(meme_json_str))
                successful_count += 1
            except ValidationError as e:
                logger.warning(f"VALIDATION_ERROR skipping meme _id={meme_id_str}: {e.errors()}")
            except Exception as inner_e:
                # Log ANY other exception during processing of a single meme
                logger.error(f"UNEXPECTED_PROCESSING_ERROR for meme _id={meme_id_str}: {inner_e}", exc_info=True)
        
        logger.info(f"Processed {processed_count} memes, successfully validated/serialized {successful_count} for API response.")
        return jsonify(memes_list), 200
        
    except Exception as e:
        logger.error(f"Error retrieving memes (outer try block): {e}", exc_info=True)
        return jsonify({"error": f"Internal server error retrieving memes: {str(e)}"}), 500

@memes_bp.route('/<meme_id>', methods=['GET'])
def get_meme(meme_id):
    """Get a specific ethical meme by its ID."""
    if current_app.db is None:
        return jsonify({"error": "Database connection not available"}), 503

    try:
        try:
            obj_id = ObjectId(meme_id)
        except InvalidId:
            return jsonify({"error": f"Invalid meme ID format: {meme_id}"}), 400
            
        meme_doc = current_app.db.ethical_memes.find_one({"_id": obj_id})
        
        if meme_doc is None:
             return jsonify({"error": f"Meme with ID {meme_id} not found"}), 404
             
        # Validate with Pydantic model
        try:
            validated_meme_obj = EthicalMemeInDB(**meme_doc)
            # Dump to JSON string (handles ObjectId), then load back to dict
            meme_json_str = validated_meme_obj.model_dump_json(by_alias=True)
            return jsonify(json.loads(meme_json_str)), 200
        except ValidationError as e:
            logger.error(f"Error validating meme {meme_id} from DB: {e.errors()}")
            return jsonify({"error": f"Internal server error validating meme data for {meme_id}"}), 500
        except Exception as inner_e:
             logger.error(f"Unexpected error processing meme {meme_id}: {inner_e}", exc_info=True)
             return jsonify({"error": f"Unexpected error processing meme {meme_id}"}), 500
             
    except Exception as e:
        logger.error(f"Error retrieving meme {meme_id}: {e}", exc_info=True)
        return jsonify({"error": f"Internal server error retrieving meme {meme_id}: {str(e)}"}), 500

@memes_bp.route('/<meme_id>', methods=['PUT'])
def update_meme(meme_id):
    """Update an existing ethical meme."""
    if current_app.db is None:
        return jsonify({"error": "Database connection not available"}), 503

    try:
        obj_id = ObjectId(meme_id)
    except InvalidId:
        return jsonify({"error": "Invalid meme ID format"}), 400

    update_data = request.get_json()
    if not update_data:
        return jsonify({"error": "No JSON data received for update"}), 400

    try:
        # Validate the incoming update data (all fields optional)
        meme_update = EthicalMemeUpdate(**update_data)
        # Get validated data, excluding unset fields to avoid overwriting with None
        update_payload_set = meme_update.model_dump(exclude_unset=True)
    except ValidationError as e:
        logger.warning(f"Meme update validation failed for ID {meme_id}: {e.errors()}")
        return jsonify({"error": "Invalid update data", "details": e.errors()}), 422

    if not update_payload_set:
         return jsonify({"error": "No valid fields provided for update"}), 400

    # Prepare the full MongoDB update operation
    mongo_update = {
        "$set": update_payload_set,
        "$currentDate": {"metadata.updated_at": True}, # Use $currentDate for atomic server-side update
        "$inc": {"metadata.version": 1}
    }

    try:
        result = current_app.db.ethical_memes.update_one(
            {"_id": obj_id},
            mongo_update
        )

        if result.matched_count == 0:
            return jsonify({"error": "Meme not found"}), 404
        
        # Fetch and return the updated document, validated by Pydantic
        updated_meme_doc = current_app.db.ethical_memes.find_one({"_id": obj_id})
        response_meme = EthicalMemeInDB(**updated_meme_doc)
        return response_meme.model_dump_json(by_alias=True), 200, {'Content-Type': 'application/json'}

    except ValidationError as e: # Catch validation error on returning the updated doc
        logger.error(f"Error validating updated meme {meme_id} from DB: {e.errors()}")
        return jsonify({"error": f"Internal server error validating updated meme data for {meme_id}"}), 500
    except Exception as e:
        logger.error(f"Error updating meme {meme_id}: {e}", exc_info=True)
        return jsonify({"error": f"Internal server error updating meme {meme_id}"}), 500

@memes_bp.route('/<meme_id>', methods=['DELETE'])
def delete_meme(meme_id):
    """Delete an ethical meme."""
    if current_app.db is None:
        return jsonify({"error": "Database connection not available"}), 503

    try:
        obj_id = ObjectId(meme_id)
    except InvalidId:
        return jsonify({"error": "Invalid meme ID format"}), 400

    try:
        result = current_app.db.ethical_memes.delete_one({"_id": obj_id})

        if result.deleted_count == 0:
            return jsonify({"error": "Meme not found"}), 404
        else:
            return '', 204 # No content, successful deletion

    except Exception as e:
        logger.error(f"Error deleting meme {meme_id}: {e}", exc_info=True)
        return jsonify({"error": f"Internal server error deleting meme {meme_id}"}), 500

# --- File Upload Route ---
@memes_bp.route('/upload', methods=['POST'])
def upload_memes():
    """Handle file uploads for mass meme import, optionally using an LLM for parsing."""
    if 'file' not in request.files:
        return jsonify({"error": "No file part in the request"}), 400
    
    file = request.files['file']
    if not file or file.filename == '':
        return jsonify({"error": "No selected file or empty filename"}), 400

    use_llm = request.form.get('use_llm', 'false').lower() == 'true'
    filename = secure_filename(file.filename)
    _, file_extension = os.path.splitext(filename)
    allowed_extensions = {".json", ".csv", ".txt"} # Allow various text-based formats
    
    if file_extension.lower() not in allowed_extensions:
        return jsonify({"error": f"Invalid file type '{file_extension}'. Allowed: {allowed_extensions}"}), 400

    if current_app.db is None:
         return jsonify({"error": "Database connection not available"}), 503

    logger.info(f"Received file upload: {filename}, use_llm: {use_llm}")
    
    processed_count = 0
    inserted_count = 0
    validation_errors = []
    llm_feedback = "LLM processing was not requested or failed before feedback generation."
    
    try:
        content_string = file.stream.read().decode("utf-8")
        if not content_string.strip():
             return jsonify({"error": "Uploaded file is empty"}), 400
             
        records_to_process = []

        # --- LLM Processing (if requested) --- 
        if use_llm:
            logger.info(f"Processing '{filename}' content with LLM...")
            
            # Determine LLM config (reuse logic from /analyze or define specific config)
            # Example: Using a default upload LLM or getting config similarly to _get_analysis_api_config
            # For simplicity, using hardcoded model and assuming key is in env
            # Replace with proper config retrieval logic!
            upload_llm_model = os.getenv("UPLOAD_LLM_MODEL", "gpt-4o") # Example
            upload_llm_key = os.getenv("OPENAI_API_KEY") # Example - needs adjustment based on model
            upload_llm_endpoint = None # Example
            
            if not upload_llm_key:
                logger.error("LLM API Key for upload processing not configured.")
                return jsonify({"error": "LLM processing configuration missing on server."}), 500

            try:
                schema_json = json.dumps(EthicalMemeCreate.model_json_schema(), indent=2)
            except Exception as schema_err:
                logger.error(f"Failed to generate Pydantic schema for LLM prompt: {schema_err}")
                schema_json = "Could not generate schema."
                
            llm_prompt = (
                f"You are an assistant that extracts structured data from text. "
                f"Parse the following data content from a file named '{filename}'. "
                f"The goal is to create entries matching the following Pydantic schema:\n\n"
                f"```json\n{schema_json}\n```\n\n"
                f"Focus on extracting fields defined in the schema (name, description, ethical_dimension, etc.). "
                f"Handle potential variations in input format (e.g., CSV, JSON lines, free text). "
                f"If an entry is clearly invalid, incomplete (missing required 'name' or 'description'), or cannot be reasonably mapped to the schema, skip it. "
                f"**Output Format:** Respond with ONLY a single JSON object containing two keys:\n"
                f"1. `extracted_memes`: A JSON array containing valid objects strictly adhering to the schema. Include only successfully parsed entries. \n"
                f"2. `processing_summary`: A brief TEXT string summarizing any issues encountered (e.g., skipped records due to missing fields, format errors, ambiguities). If no issues, state that processing was successful.\n\n"
                f"**DO NOT include any text before or after the main JSON object.**\n\n"
                f"Data Content:\n---{filename} START---\n{content_string}\n---{filename} END---"
            )
            
            logger.debug(f"Sending prompt to LLM ({upload_llm_model}) for file parsing.")
            llm_response_raw = generate_response(
                prompt=llm_prompt, 
                api_key=upload_llm_key, 
                model_name=upload_llm_model,
                api_endpoint=upload_llm_endpoint
            )

            if not llm_response_raw:
                logger.error("LLM did not return a response for file parsing.")
                llm_feedback = "LLM processing failed: No response received from the model."
                # Proceed without LLM results, potentially trying direct parsing below
            else:
                logger.debug("Received raw response from LLM.")
                # --- Parse LLM Response --- 
                try:
                    parsed_llm_output = json.loads(llm_response_raw)
                    if not isinstance(parsed_llm_output, dict) or \
                       'extracted_memes' not in parsed_llm_output or \
                       'processing_summary' not in parsed_llm_output:
                        raise ValueError("LLM JSON response missing required keys ('extracted_memes', 'processing_summary').")
                        
                    extracted_memes_raw = parsed_llm_output.get('extracted_memes', [])
                    llm_feedback = parsed_llm_output.get('processing_summary', "LLM provided no summary.")
                    logger.info(f"LLM Feedback: {llm_feedback}")
                    
                    if not isinstance(extracted_memes_raw, list):
                         raise ValueError("'extracted_memes' key in LLM response is not a list.")
                         
                    records_to_process = extracted_memes_raw # Use LLM output as the source
                    processed_count = len(records_to_process)
                    logger.info(f"LLM extracted {processed_count} potential meme records.")
                    
                except json.JSONDecodeError as json_err:
                    logger.error(f"Failed to decode LLM response as JSON: {json_err}. Response (start): {llm_response_raw[:200]}...", exc_info=True)
                    llm_feedback = f"LLM processing failed: Could not parse model response as valid JSON. Error: {json_err}"
                except ValueError as val_err:
                    logger.error(f"LLM JSON response has invalid structure: {val_err}. Response: {llm_response_raw[:500]}...", exc_info=True)
                    llm_feedback = f"LLM processing failed: {val_err}"
                except Exception as parse_err:
                    logger.error(f"Unexpected error parsing LLM response: {parse_err}. Response: {llm_response_raw[:500]}...", exc_info=True)
                    llm_feedback = f"LLM processing failed: Unexpected error during response parsing."

        # --- Direct Parsing (Fallback or if LLM not used) --- 
        elif file_extension.lower() == '.json':
            logger.info(f"Attempting direct JSON parsing for '{filename}'")
            try:
                # Assume a JSON array of objects or JSON lines
                try:
                    # Try parsing as a single JSON array first
                    records_to_process = json.loads(content_string)
                    if not isinstance(records_to_process, list):
                         raise ValueError("JSON file is not a list of objects.")
                except (json.JSONDecodeError, ValueError):
                    # Try parsing as JSON Lines (objects separated by newlines)
                    records_to_process = []
                    for line in content_string.strip().split('\n'):
                        if line.strip():
                             try: records_to_process.append(json.loads(line))
                             except json.JSONDecodeError:
                                  logger.warning(f"Skipping invalid JSON line in {filename}: {line[:100]}...")
                                  validation_errors.append({"record_index": len(records_to_process), "record_name": "N/A (JSON Line)", "errors": "Invalid JSON format"})
                processed_count = len(records_to_process)
                logger.info(f"Directly parsed {processed_count} records from JSON file.")
            except Exception as e:
                logger.error(f"Failed to directly parse JSON file '{filename}': {e}", exc_info=True)
                return jsonify({"error": "Failed to parse uploaded file."}), 400
        else:
            # Handle other direct parsing (e.g., CSV) if needed, or return error
            logger.warning(f"Direct parsing for file type '{file_extension}' is not implemented. Use LLM or upload JSON.")
            return jsonify({"error": f"Direct parsing for {file_extension} not supported. Please use the LLM option or upload a JSON file."}), 400

        # --- Validate and Insert Records --- 
        if not records_to_process:
            logger.warning(f"No records found to process for file '{filename}' after parsing/LLM stage.")
        else:
            logger.info(f"Validating {len(records_to_process)} parsed/extracted records...")
            now = datetime.now(timezone.utc)
            validated_memes_for_insert = []
            
            for i, record_data in enumerate(records_to_process):
                record_name = record_data.get("name", f"Record {i+1}") # Get name for error reporting
                try:
                    # Validate using Pydantic model
                    meme_validated = EthicalMemeCreate(**record_data)
                    meme_doc = meme_validated.model_dump(by_alias=True)
                    # Add metadata before potential insertion
                    meme_doc['metadata'] = {'created_at': now, 'updated_at': now, 'version': 1}
                    validated_memes_for_insert.append(meme_doc)
                except ValidationError as e:
                    logger.warning(f"Validation failed for record index {i} (Name: '{record_name}'): {e.errors()}")
                    validation_errors.append({"record_index": i, "record_name": record_name, "errors": e.errors()})
                except Exception as val_err:
                    # Catch unexpected errors during validation/dumping
                    logger.error(f"Unexpected error validating record index {i} (Name: '{record_name}'): {val_err}", exc_info=True)
                    validation_errors.append({"record_index": i, "record_name": record_name, "errors": "Unexpected validation error"})
            
            # Bulk insert validated memes if any exist
            if validated_memes_for_insert:
                try:
                    insert_result = current_app.db.ethical_memes.insert_many(validated_memes_for_insert, ordered=False)
                    inserted_count = len(insert_result.inserted_ids)
                    logger.info(f"Successfully inserted {inserted_count} memes from file '{filename}'.")
                except Exception as db_err: # Catch potential bulk write errors
                    logger.error(f"Error during bulk insert from file '{filename}': {db_err}", exc_info=True)
                    # Note: Some records might have been inserted before the error if ordered=False
                    # For simplicity, report a general DB error. More complex handling could check BulkWriteError details.
                    return jsonify({"error": "Database error during bulk insert. Some records may not have been saved."}), 500
            else:
                logger.warning(f"No valid memes found to insert from file '{filename}' after validation.")

    except Exception as e:
        logger.error(f"Unexpected error processing file upload '{filename}': {e}", exc_info=True)
        return jsonify({"error": "An unexpected server error occurred during file processing."}), 500

    # --- Return Results --- 
    final_message = f"Processed file '{filename}'. {inserted_count}/{processed_count if processed_count > 0 else 'N/A'} records inserted."
    if validation_errors:
        final_message += f" {len(validation_errors)} records failed validation."
        
    return jsonify({
        "message": final_message,
        "inserted_count": inserted_count,
        "processed_records": processed_count, # Records attempted after parsing/LLM extraction
        "validation_errors": validation_errors,
        "llm_feedback": llm_feedback
    }), 200 

# --- New Route for Mass Population ---
@memes_bp.route('/populate', methods=['POST'])
def populate_memes():
    """Populates the database with predefined memes, checking for existence first."""
    if current_app.db is None:
         return jsonify({"error": "Database connection not available"}), 503
    
    memes_collection = current_app.db.ethical_memes
    inserted_count = 0
    skipped_count = 0
    errors = []

    try:
        # Load meme data from external file
        with open(config.MEMES_JSON_FILEPATH, 'r', encoding='utf-8-sig') as f:
            # Use json_util.loads to handle MongoDB extended JSON like {"$date": ...} if present
            # If memes.json uses standard ISO dates, json.load(f) is fine and Pydantic handles parsing.
            # Assuming memes.json might have $date, use json_util
            from bson import json_util
            predefined_memes_raw = json_util.loads(f.read())
        logger.info(f"Loaded {len(predefined_memes_raw)} memes from {config.MEMES_JSON_FILEPATH}")
    except Exception as e:
        logger.error(f"Error loading memes from {config.MEMES_JSON_FILEPATH}: {e}", exc_info=True)
        return jsonify({"error": f"Failed to load meme data file: {e}"}), 500

    # Ensure that datetime parsing logic is robust. Pydantic models should handle ISO strings.
    # If converting from {"$date": ...} to datetime objects:
    now = datetime.now(timezone.utc)
    processed_memes = []
    for meme_data in predefined_memes_raw:
        if 'metadata' in meme_data and isinstance(meme_data['metadata'], dict):
            for date_field in ['created_at', 'updated_at']:
                if date_field in meme_data['metadata']:
                    if isinstance(meme_data['metadata'][date_field], dict) and '$date' in meme_data['metadata'][date_field]:
                        try:
                            # bson.json_util.loads already converts $date to datetime
                            # If it's still a dict here, it means it wasn't standard BSON $date
                            # For safety, attempt parsing if it's a string, else use `now`
                            if isinstance(meme_data['metadata'][date_field]['$date'], str):
                                 meme_data['metadata'][date_field] = parse_datetime(meme_data['metadata'][date_field]['$date'])
                            else: # if $date value is not string, log warning and use now
                                logger.warning(f"Unexpected $date format for {date_field} in meme {meme_data.get('name')}, using current time.")
                                meme_data['metadata'][date_field] = now
                        except ValueError as ve:
                            logger.warning(f"Could not parse date string {meme_data['metadata'][date_field]} for {date_field} in meme {meme_data.get('name')}: {ve}. Using current time.")
                            meme_data['metadata'][date_field] = now
                    elif isinstance(meme_data['metadata'][date_field], str): # Already an ISO string
                        try:
                            meme_data['metadata'][date_field] = parse_datetime(meme_data['metadata'][date_field])
                        except ValueError:
                             meme_data['metadata'][date_field] = now # Fallback
                    else: # Not a dict with $date, not a string
                        meme_data['metadata'][date_field] = now
        else: # No metadata block
            meme_data['metadata'] = {'created_at': now, 'updated_at': now, 'version': 1}
        processed_memes.append(meme_data)
    predefined_memes = processed_memes # Use the list with parsed dates

    try:
        for meme_data in predefined_memes:
            name = meme_data.get("name")
            if not name:
                logger.warning("Skipping predefined meme with no name.")
                skipped_count += 1
                continue

            # Check if a meme with the same name already exists
            existing_meme = memes_collection.find_one({"name": name})
            if existing_meme:
                logger.info(f"Meme '{name}' already exists. Skipping.")
                skipped_count += 1
                continue

            try:
                # Validate with Pydantic before inserting
                validated_meme = EthicalMemeCreate(**meme_data)
                meme_doc_to_insert = validated_meme.model_dump(by_alias=True)
                # Re-add metadata as it might not be part of EthicalMemeCreate
                meme_doc_to_insert['metadata'] = meme_data['metadata']
                
                # Insert the new meme
                result = memes_collection.insert_one(meme_doc_to_insert)
                if result.inserted_id:
                    inserted_count += 1
                    logger.debug(f"Inserted meme '{name}' with ID: {result.inserted_id}")
                else:
                    errors.append(f"Failed to insert meme '{name}'.")
                    
            except ValidationError as e:
                logger.warning(f"Validation failed for predefined meme '{name}': {e.errors()}")
                errors.append(f"Validation failed for '{name}': {e.errors()}")
            except Exception as insert_err:
                logger.error(f"Error processing or inserting predefined meme '{name}': {insert_err}", exc_info=True)
                errors.append(f"Error processing '{name}'. See server logs for details.")

        status_code = 200 if not errors else 207 # Multi-status if errors occurred
        return jsonify({
            "message": f"Population complete. Inserted: {inserted_count}, Skipped (already exists): {skipped_count}.",
            "errors": errors
        }), status_code
        
    except Exception as e:
         logger.error(f"Error populating memes collection: {e}", exc_info=True)
         return jsonify({"error": "Internal server error populating memes. See server logs for details."}), 500

@memes_bp.route('/batch', methods=['POST'])
def batch_upload_memes():
    """Accepts a JSON payload with a list of memes and inserts/updates them in bulk.

    Expected JSON schema::
        {
            "memes": [ {<EthicalMemeCreate>}, ... ],
            "use_llm_processing": false
        }
    The *use_llm_processing* key is accepted for forward-compatibility but currently ignored because the
    Dash admin UI already performs LLM-based pre-processing if requested.  
    The route performs *upsert* semantics using the **name** field as a natural key so that repeated calls
    do not create duplicates.
    """
    if current_app.db is None:
        return jsonify({"error": "Database connection not available"}), 503

    try:
        payload = request.get_json(force=True, silent=False)
    except Exception as err:
        logger.error(f"batch_upload_memes: invalid JSON payload – {err}")
        return jsonify({"error": "Request body must be valid JSON."}), 400

    if not payload or "memes" not in payload or not isinstance(payload["memes"], list):
        return jsonify({"error": "Payload must contain a 'memes' array."}), 400

    memes_raw = payload["memes"]
    validated_docs = []
    validation_errors = []
    now = datetime.now(timezone.utc)

    for idx, meme_data in enumerate(memes_raw):
        record_name = meme_data.get("name", f"index_{idx}")
        try:
            meme_obj = EthicalMemeCreate(**meme_data)
            meme_doc = meme_obj.model_dump(by_alias=True)
            # ensure metadata exists
            meme_doc.setdefault("metadata", {})
            meme_doc["metadata"].update({"created_at": now, "updated_at": now, "version": 1})
            validated_docs.append(meme_doc)
        except ValidationError as ve:
            validation_errors.append({
                "record_index": idx,
                "record_name": record_name,
                "errors": ve.errors()
            })
        except Exception as ex:
            logger.error(f"Unexpected validation error for record {idx}: {ex}", exc_info=True)
            validation_errors.append({
                "record_index": idx,
                "record_name": record_name,
                "errors": "Unexpected validation error"
            })

    inserted = 0
    updated = 0

    if validated_docs:
        operations = []
        for doc in validated_docs:
            operations.append(
                UpdateOne(
                    {"name": doc.get("name")},
                    {"$set": doc, "$setOnInsert": {"metadata.created_at": now}},
                    upsert=True,
                )
            )
        try:
            result = current_app.db.ethical_memes.bulk_write(operations, ordered=False)
            inserted = len(result.upserted_ids) if result.upserted_ids else 0
            updated = result.modified_count
            logger.info(f"batch_upload_memes: {inserted} inserted, {updated} updated, {len(validation_errors)} errors")
        except Exception as db_err:
            logger.error(f"Error during bulk_write in batch_upload_memes: {db_err}", exc_info=True)
            return jsonify({"error": "Database error during batch operation."}), 500

    return jsonify({
        "processed": len(memes_raw),
        "inserted": inserted,
        "updated": updated,
        "validation_errors": validation_errors,
    }), 200 
