"""
API routes for Ethical Memes CRUD operations
"""

import logging
from datetime import datetime, timezone
from flask import Blueprint, request, jsonify, current_app
from bson import ObjectId
from bson.errors import InvalidId
from pydantic import ValidationError

# Import Pydantic models
from .models import EthicalMemeCreate, EthicalMemeUpdate, EthicalMemeInDB

# Setup logger for this module
logger = logging.getLogger(__name__)

# --- Blueprint Definition ---
memes_bp = Blueprint('memes_api', __name__, url_prefix='/api/memes')

# --- Helper Function for ObjectId Conversion ---
def _convert_objectid(doc):
    """Converts MongoDB ObjectId to string for JSON serialization."""
    if doc and '_id' in doc and isinstance(doc['_id'], ObjectId):
        doc['_id'] = str(doc['_id'])
    return doc

# --- CRUD Routes ---

@memes_bp.route('/', methods=['POST'])
def create_meme():
    """Create a new ethical meme."""
    if not current_app.db:
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
    if not current_app.db:
        return jsonify({"error": "Database connection not available"}), 503

    try:
        memes_cursor = current_app.db.ethical_memes.find()
        # Validate and serialize each meme using the Pydantic model
        memes_list = [EthicalMemeInDB(**meme).model_dump(by_alias=True) for meme in memes_cursor]
        return jsonify(memes_list), 200
    except ValidationError as e:
        # This might happen if DB data doesn't match the model
        logger.error(f"Error validating memes from DB: {e.errors()}")
        return jsonify({"error": "Internal server error validating meme data"}), 500
    except Exception as e:
        logger.error(f"Error retrieving memes: {e}", exc_info=True)
        return jsonify({"error": "Internal server error retrieving memes"}), 500

@memes_bp.route('/<meme_id>', methods=['GET'])
def get_meme(meme_id):
    """Get a single ethical meme by its ID."""
    if not current_app.db:
        return jsonify({"error": "Database connection not available"}), 503

    try:
        obj_id = ObjectId(meme_id)
    except InvalidId:
        return jsonify({"error": "Invalid meme ID format"}), 400

    try:
        meme_doc = current_app.db.ethical_memes.find_one({"_id": obj_id})
        if meme_doc:
            # Validate and structure the response using Pydantic
            response_meme = EthicalMemeInDB(**meme_doc)
            return response_meme.model_dump_json(by_alias=True), 200, {'Content-Type': 'application/json'}
        else:
            return jsonify({"error": "Meme not found"}), 404
    except ValidationError as e:
        logger.error(f"Error validating meme {meme_id} from DB: {e.errors()}")
        return jsonify({"error": f"Internal server error validating meme data for {meme_id}"}), 500
    except Exception as e:
        logger.error(f"Error retrieving meme {meme_id}: {e}", exc_info=True)
        return jsonify({"error": f"Internal server error retrieving meme {meme_id}"}), 500

@memes_bp.route('/<meme_id>', methods=['PUT'])
def update_meme(meme_id):
    """Update an existing ethical meme."""
    if not current_app.db:
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
    if not current_app.db:
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