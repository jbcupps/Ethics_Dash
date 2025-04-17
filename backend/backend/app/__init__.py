"""
Backend API for Ethical Review Application
"""
import os
import logging
from flask import Flask
from flask_cors import CORS
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure
from werkzeug.middleware.proxy_fix import ProxyFix
from dotenv import load_dotenv  # Load .env file for local development
load_dotenv()  # Load environment variables from .env file

# Dash Imports
import dash
import dash_bootstrap_components as dbc
from dash import html # Correct import
from backend.app.dash_layout import create_layout # Use absolute import from package
from backend.app.callbacks import register_all_callbacks # Updated import to use the new callbacks package

# Setup logger for this module
logger = logging.getLogger(__name__)

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
    server.config['MONGO_URI'] = os.getenv("MONGO_URI", "mongodb://mongo:27017/") # Default for docker-compose
    server.config['MONGO_DB_NAME'] = os.getenv("MONGO_DB_NAME", "ethical_memes_db")
    
    # Load API Keys and Model Config for Analysis
    server.config['ANALYSIS_API_KEY'] = os.getenv("ANALYSIS_API_KEY")
    server.config['ANALYSIS_MODEL_NAME'] = os.getenv("ANALYSIS_MODEL_NAME", "gpt-4o") # Example default
    server.config['ANALYSIS_API_ENDPOINT'] = os.getenv("ANALYSIS_API_ENDPOINT") # Optional
    
    # Add specific analysis keys (even if None)
    server.config['ANALYSIS_OPENAI_API_KEY'] = os.getenv("ANALYSIS_OPENAI_API_KEY")
    server.config['ANALYSIS_GEMINI_API_KEY'] = os.getenv("ANALYSIS_GEMINI_API_KEY")
    server.config['ANALYSIS_ANTHROPIC_API_KEY'] = os.getenv("ANALYSIS_ANTHROPIC_API_KEY")

    # --- Check for missing ANALYSIS keys and log warnings --- 
    # Determine if *any* specific analysis key is set
    specific_analysis_key_set = (
        server.config['ANALYSIS_OPENAI_API_KEY'] or
        server.config['ANALYSIS_GEMINI_API_KEY'] or
        server.config['ANALYSIS_ANTHROPIC_API_KEY']
    )
    
    # Also check general keys (as fallbacks)
    general_openai_key = os.getenv("OPENAI_API_KEY")
    general_gemini_key = os.getenv("GEMINI_API_KEY")
    general_anthropic_key = os.getenv("ANTHROPIC_API_KEY")
    general_key_set = general_openai_key or general_gemini_key or general_anthropic_key
    
    # Warn if NO analysis key (specific or general fallback) is likely available for the chosen model
    # This logic might need refinement depending on how _get_api_config chooses keys
    if not specific_analysis_key_set and not general_key_set:
         logger.warning("No specific or general API key found for analysis LLM in environment variables. Ethical analysis will likely fail.")
    elif not specific_analysis_key_set:
        logger.info("No specific ANALYSIS_***_API_KEY found. Analysis will rely on general API keys (OPENAI_API_KEY, GEMINI_API_KEY, ANTHROPIC_API_KEY).")

    # Enable CORS for frontend and Dash interactions
    CORS(server)
    
    # --- Initialize MongoDB Connection ---
    mongo_uri = server.config['MONGO_URI'] # Use config value
    mongo_db_name = server.config['MONGO_DB_NAME'] # Use config value

    try:
        # Create the MongoDB client and attach to Flask server instance
        server.mongo_client = MongoClient(mongo_uri)
        # Test connection (optional, but good practice)
        server.mongo_client.admin.command('ping') 
        logger.info(f"Successfully connected to MongoDB at {mongo_uri}")
        
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
            # Decide if this should be a fatal error

    except ConnectionFailure as e:
        logger.error(f"Could not connect to MongoDB at {mongo_uri}: {e}", exc_info=True)
        server.mongo_client = None
        server.db = None
    except Exception as e: # Catch other potential errors during initialization
        logger.error(f"An unexpected error occurred during MongoDB initialization: {e}", exc_info=True)
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