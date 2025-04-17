import os
import logging
from typing import List, Dict, Any, Optional
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure, ServerSelectionTimeoutError, OperationFailure
from dotenv import load_dotenv
from bson import ObjectId

# Load environment variables from .env file (especially MONGO_URI and MONGO_DB_NAME)
load_dotenv()

logger = logging.getLogger(__name__)

# --- MongoDB Connection Details ---
MONGO_URI = os.getenv("MONGO_URI", "mongodb://ai-mongo:27017/")
DB_NAME = os.getenv("MONGO_DB_NAME", "ethics_db")
MEME_COLLECTION_NAME = "ethical_memes" # Assuming this is your collection name

# --- Global MongoDB Client ---
# Reuse the client across requests for efficiency
mongo_client: Optional[MongoClient] = None

def get_mongo_client() -> MongoClient:
    """Returns a MongoClient instance, creating it if necessary."""
    global mongo_client
    if mongo_client is None:
        try:
            logger.info(f"Connecting to MongoDB at {MONGO_URI}...")
            mongo_client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=5000) # 5 second timeout
            # The ismaster command is cheap and does not require auth.
            mongo_client.admin.command('ismaster')
            logger.info("MongoDB connection successful.")
        except (ConnectionFailure, ServerSelectionTimeoutError) as e:
            logger.error(f"Failed to connect to MongoDB: {e}")
            mongo_client = None # Reset client on failure
            raise # Re-raise the exception to be handled by the caller
    return mongo_client

def get_db():
    """Returns the MongoDB database instance."""
    client = get_mongo_client()
    if client:
        return client[DB_NAME]
    return None

# --- Meme Specific Functions ---

def get_all_memes_for_selection() -> List[Dict[str, Any]]:
    """
    Fetches a list of all memes, returning only their _id, name, and description.
    Used for providing context to the meme selection LLM.
    Returns an empty list if connection fails or no memes are found.
    """
    memes_list = []
    try:
        db = get_db()
        if db:
            collection = db[MEME_COLLECTION_NAME]
            # Project only necessary fields
            cursor = collection.find({}, {"_id": 1, "name": 1, "description": 1})
            memes_list = list(cursor)
            # Convert ObjectId to string for easier handling later if needed,
            # although keeping it as ObjectId might be fine.
            for meme in memes_list:
                meme['_id'] = str(meme['_id'])
            logger.info(f"Fetched {len(memes_list)} memes for selection (name, description).")
        else:
            logger.error("Failed to get DB connection in get_all_memes_for_selection.")
    except OperationFailure as e:
        logger.error(f"MongoDB operation failed while fetching memes for selection: {e}")
    except Exception as e:
        logger.error(f"Unexpected error fetching memes for selection: {e}", exc_info=True)

    return memes_list

# Add other DB interaction functions here as needed (e.g., get_meme_by_id, create_meme, etc.)

# Example of how to close the connection (e.g., in app shutdown)
def close_mongo_connection():
    """Closes the global MongoDB client connection."""
    global mongo_client
    if mongo_client:
        mongo_client.close()
        mongo_client = None
        logger.info("MongoDB connection closed.") 