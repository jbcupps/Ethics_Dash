from flask import jsonify
from bson.objectid import ObjectId
from flask import current_app
from flask import logger

def get_memes():
    """Get all ethical memes."""
    if current_app.db is None:
        return jsonify({"error": "Database connection not available"}), 503

    try:
        # Get all memes from MongoDB
        memes_cursor = current_app.db.ethical_memes.find()
        
        # Convert the cursor to a list and manually convert ObjectId to string
        memes_list = []
        for meme in memes_cursor:
            # Convert MongoDB _id to string
            if '_id' in meme and isinstance(meme['_id'], ObjectId):
                meme['_id'] = str(meme['_id'])
            
            # Add other conversions if needed
            memes_list.append(meme)
        
        return jsonify(memes_list), 200
    except Exception as e:
        logger.error(f"Error retrieving memes: {e}", exc_info=True)
        return jsonify({"error": "Internal server error retrieving memes"}), 500 