"""
Backend API for Ethical Review Application
"""
import os
import time
import logging
from flask import Flask
from flask_cors import CORS
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure, ServerSelectionTimeoutError, InvalidURI
from werkzeug.middleware.proxy_fix import ProxyFix
from urllib.parse import quote_plus, urlparse, urlunparse # Added imports

# Import the new centralized configuration
from . import config

# Dash Imports
import dash
import dash_bootstrap_components as dbc
from dash import html # Correct import
from .dash_layout import create_layout # Use relative import
from .callbacks import register_all_callbacks # Use relative import

# Setup logger for this module
logger = logging.getLogger(__name__)

def _sanitize_mongo_uri(uri: str) -> str:
    """Sanitizes MongoDB URI for logging by masking credentials."""
    try:
        parsed = urlparse(uri)
        if parsed.username:
            sanitized = parsed._replace(netloc=f"***:***@{parsed.hostname}:{parsed.port}")
            return urlunparse(sanitized)
    except Exception:
        pass
    return "***sanitized***"

def wait_for_mongodb(mongo_uri, max_retries=30, retry_interval=2):
    """Wait for MongoDB to become available with retries."""
    # Use the URI directly
    logger.info(f"Checking MongoDB connection using URI: {_sanitize_mongo_uri(mongo_uri)}...")

    for attempt in range(1, max_retries + 1):
        try:
            # Create a client with a shorter timeout
            # MongoClient handles necessary escaping internally based on standard URI components
            client = MongoClient(mongo_uri, serverSelectionTimeoutMS=5000)
            # Test connection
            client.admin.command('ping')
            logger.info(f"MongoDB connection successful on attempt {attempt}")
            return client
        except (ConnectionFailure, ServerSelectionTimeoutError, InvalidURI) as e:
            logger.warning(f"MongoDB connection attempt {attempt}/{max_retries} failed: {e}")
            if attempt < max_retries:
                logger.info(f"Retrying in {retry_interval} seconds...")
                time.sleep(retry_interval)
            # If InvalidURI occurs, no point retrying with the same URI
            if isinstance(e, InvalidURI):
                 logger.error(f"Invalid MongoDB URI encountered. Aborting wait.")
                 break

    logger.error("Max retries reached or invalid URI. MongoDB connection failed.")
    return None

def create_app():
    """Factory pattern for creating Flask app with integrated Dash app"""
    server = Flask(__name__) # Rename Flask instance to 'server'
    
    # --- Apply ProxyFix Middleware ---
    server.wsgi_app = ProxyFix(
        server.wsgi_app, x_proto=1, x_prefix=1
    )
    
    # --- MongoDB Configuration using centralized config ---
    mongo_uri = config.get_mongo_uri()
    mongo_db_name = config.get_mongo_db_name()

    server.config['MONGO_URI'] = mongo_uri # Store the final URI
    server.config['MONGO_DB_NAME'] = mongo_db_name
    
    # Log the MongoDB config
    logger.info(f"MongoDB URI (constructed): {_sanitize_mongo_uri(mongo_uri)}")
    logger.info(f"MongoDB Database: {mongo_db_name}")
    
    # Enable CORS for frontend and Dash interactions
    CORS(server)
    
    # --- Initialize MongoDB Connection ---
    # Pass the constructed URI directly
    server.mongo_client = wait_for_mongodb(mongo_uri) # Use the final URI
    
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
        logger.error(f"Failed to connect to MongoDB using URI: {_sanitize_mongo_uri(mongo_uri)}")
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