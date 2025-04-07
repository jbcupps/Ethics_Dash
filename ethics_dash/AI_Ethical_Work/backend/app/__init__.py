"""
Backend API for Ethical Review Application
"""
import os
import logging
from flask import Flask
from flask_cors import CORS
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure

# Setup logger for this module
logger = logging.getLogger(__name__)

def create_app():
    """Factory pattern for creating Flask app with config"""
    app = Flask(__name__)
    # Enable CORS for frontend
    CORS(app)
    
    # --- Initialize MongoDB Connection ---
    mongo_uri = os.getenv("MONGO_URI", "mongodb://localhost:27017/") # Default for safety
    mongo_db_name = os.getenv("MONGO_DB_NAME", "ethical_memes_db")

    try:
        # Create the MongoDB client
        app.mongo_client = MongoClient(mongo_uri)
        # Test connection (optional, but good practice)
        app.mongo_client.admin.command('ping') 
        logger.info(f"Successfully connected to MongoDB at {mongo_uri}")
        
        # Get a handle to the specific database
        app.db = app.mongo_client[mongo_db_name]
        logger.info(f"Using MongoDB database: {mongo_db_name}")
        
    except ConnectionFailure as e:
        logger.error(f"Could not connect to MongoDB at {mongo_uri}: {e}", exc_info=True)
        # Depending on requirements, you might exit or run without DB functionality
        app.mongo_client = None
        app.db = None
    except Exception as e: # Catch other potential errors during initialization
        logger.error(f"An unexpected error occurred during MongoDB initialization: {e}", exc_info=True)
        app.mongo_client = None
        app.db = None

    # Import and register blueprints
    from backend.app.api import api_bp
    from backend.app.memes_api import memes_bp
    app.register_blueprint(api_bp)
    app.register_blueprint(memes_bp)
    
    return app 