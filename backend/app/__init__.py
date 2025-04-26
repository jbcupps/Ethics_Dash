"""
Backend API for Ethical Review Application
"""
import os
import time
import logging
from flask import Flask
from flask_cors import CORS
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure, ServerSelectionTimeoutError
from werkzeug.middleware.proxy_fix import ProxyFix
from dotenv import load_dotenv  # Load .env file for local development
load_dotenv()  # Load environment variables from .env file

# Dash Imports
import dash
import dash_bootstrap_components as dbc
from dash import html # Correct import
from .dash_layout import create_layout # Use relative import
from .callbacks import register_all_callbacks # Use relative import

# Setup logger for this module
logger = logging.getLogger(__name__)

def wait_for_mongodb(mongo_uri, max_retries=30, retry_interval=2):
    """Wait for MongoDB to become available with retries"""
    logger.info(f"Checking MongoDB connection at {mongo_uri}...")
    
    for attempt in range(1, max_retries + 1):
        try:
            # Create a client with a shorter timeout
            client = MongoClient(mongo_uri, serverSelectionTimeoutMS=5000)
            # Test connection
            client.admin.command('ping')
            logger.info(f"MongoDB connection successful on attempt {attempt}")
            return client
        except (ConnectionFailure, ServerSelectionTimeoutError) as e:
            logger.warning(f"MongoDB connection attempt {attempt}/{max_retries} failed: {e}")
            if attempt < max_retries:
                logger.info(f"Retrying in {retry_interval} seconds...")
                time.sleep(retry_interval)
    
    logger.error("Max retries reached. MongoDB connection failed.")
    return None

def create_app():
    """Factory pattern for creating Flask app with integrated Dash app"""
    server = Flask(__name__) # Rename Flask instance to 'server'
    
    # --- Apply ProxyFix Middleware --- 
    # Trust X-Forwarded-Proto and X-Script-Name (prefix)
    # These are the most critical for URL generation behind a proxy.
    # We trust 1 hop as Nginx is the direct proxy.
    server.wsgi_app = ProxyFix(
        server.wsgi_app, x_proto=1, x_prefix=1
    )
    
    # --- Load Configuration --- 
    # Load general config (e.g., SECRET_KEY, DEBUG - not strictly needed here yet)
    # server.config.from_object('backend.config.DefaultConfig') # Example if using a config file
    
    # Load sensitive/environment-specific config from environment variables
    # Use upper case by convention for Flask config keys
    # Check for both MONGO_URI and MONGODB_URI
    server.config['MONGO_URI'] = (
        os.getenv("MONGO_URI") or 
        os.getenv("MONGODB_URI", "mongodb://ai-mongo:27017/")
    )
    server.config['MONGO_DB_NAME'] = os.getenv("MONGO_DB_NAME", "ethics_db")
    
    # Log the MongoDB config
    logger.info(f"MongoDB URI: {server.config['MONGO_URI']}")
    logger.info(f"MongoDB Database: {server.config['MONGO_DB_NAME']}")
    
    # Load API Keys and Model Config for Analysis
    # Use specific analysis keys if present, otherwise fall back to general keys
    server.config['ANALYSIS_API_KEY'] = (
        os.getenv("ANALYSIS_ANTHROPIC_API_KEY") or
        os.getenv("ANTHROPIC_API_KEY") or
        os.getenv("ANALYSIS_OPENAI_API_KEY") or
        os.getenv("OPENAI_API_KEY") or
        os.getenv("ANALYSIS_GEMINI_API_KEY") or
        os.getenv("GEMINI_API_KEY")
    )
    # Default analysis model (Anthropic Claude Sonnet)
    server.config['ANALYSIS_LLM_MODEL'] = os.getenv("ANALYSIS_LLM_MODEL", "claude-3-sonnet-20240229")
    server.config['ANALYSIS_API_ENDPOINT'] = os.getenv("ANALYSIS_API_ENDPOINT") # Optional
    
    # Enable CORS for frontend and Dash interactions
    CORS(server)
    
    # --- Initialize MongoDB Connection ---
    mongo_uri = server.config['MONGO_URI'] # Use config value
    mongo_db_name = server.config['MONGO_DB_NAME'] # Use config value

    # Try to connect to MongoDB with retries
    server.mongo_client = wait_for_mongodb(mongo_uri)
    
    if server.mongo_client:
        try:
            # Get a handle to the specific database and attach to Flask server instance
            server.db = server.mongo_client[mongo_db_name]
            logger.info(f"Using MongoDB database: {mongo_db_name}")
            
            # --- Ensure Database Indexes Exist ---
            try:
                # Add index for 'name' field in 'ethical_memes' collection
                # Consider if 'name' should be unique. If not, remove unique=True.
                result = server.db.ethical_memes.create_index([('name', 1)], unique=True, name='name_unique_idx')
                logger.info(f"Ensured index '{result}' on ethical_memes.name")
                # Add other indexes here if needed, e.g.:
                # server.db.ethical_memes.create_index([('tags', 1)], name='tags_idx')
                # server.db.ethical_memes.create_index([('ethical_dimension', 1)], name='dimension_idx')
            except Exception as idx_err:
                logger.error(f"Error creating MongoDB index: {idx_err}", exc_info=True)
        except Exception as e:
            logger.error(f"An error occurred with MongoDB database: {e}", exc_info=True)
            server.mongo_client = None
            server.db = None
    else:
        logger.error(f"Failed to connect to MongoDB at {mongo_uri}")
        server.mongo_client = None
        server.db = None

    # --- Import and register Flask blueprints FIRST ---
    from .api import api_bp
    from .memes_api import memes_bp
    server.register_blueprint(api_bp)
    server.register_blueprint(memes_bp)

    # --- Initialize Dash App AFTER blueprints --- 
    dash_app = dash.Dash(
        __name__, 
        server=server, 
        routes_pathname_prefix='/dash/',
        requests_pathname_prefix='/dash/',
        external_stylesheets=[dbc.themes.BOOTSTRAP],
        suppress_callback_exceptions=True
    )

    # Define Layout using the imported function
    dash_app.layout = create_layout()

    # Register Callbacks using the single registration function
    register_all_callbacks(dash_app) 

    # Set Dash app title
    dash_app.title = "Ethical Memes Dashboard"
    
    return server # Return the Flask server instance 