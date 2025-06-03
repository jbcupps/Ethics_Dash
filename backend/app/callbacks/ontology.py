"""Registers callbacks for the ontology display tab."""

import os
import logging
# Removed callback
from dash import Input, Output
# from flask import current_app # Removed

# Import the new centralized configuration
from .. import config

logger = logging.getLogger(__name__)

# --- Registration Function --- 
def register_ontology_callbacks(dash_app):

    # Callback to load and display the ontology file
    # (Moved from original dash_callbacks.py)
    @dash_app.callback(
        Output('ontology-display', 'children'),
        Input('meme-update-trigger-store', 'data'), 
        prevent_initial_call=False
    )
    def load_ontology_display(trigger_data):
        """Reads the ontology.md file and displays it."""
        logger.info("Loading ontology.md for display.")
        ontology_content = ""
        error_message = ""
        
        # Use config for ontology file path
        ontology_path = config.ONTOLOGY_FILEPATH
        if os.path.exists(ontology_path):
            try:
                with open(ontology_path, 'r', encoding='utf-8') as f: 
                    ontology_content = f.read()
                logger.info(f"Successfully loaded {ontology_path}.")
            except Exception as e: 
                logger.error(f"Error reading ontology file at {ontology_path}: {e}", exc_info=True)
                error_message = f"*Error reading ontology file: {e}*"
        else: 
            logger.error(f"Ontology file not found at expected path: {ontology_path}")
            error_message = "*Error: ontology.md file not found.*"

        return error_message if error_message else ontology_content 