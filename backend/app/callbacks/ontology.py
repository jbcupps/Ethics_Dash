"""Registers callbacks for the ontology display tab."""

import os
import logging
# Removed callback
from dash import Input, Output
# from flask import current_app # Removed

logger = logging.getLogger(__name__)

# Assume ontology file is copied to this path in the container
ONTOLOGY_PATH_IN_CONTAINER = "/app/documents/ontology.md"

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
        # Obsolete comment removed
        logger.info("Loading ontology.md for display.")
        ontology_content = ""
        error_message = ""
        
        # Simplified path logic: Check the expected path in the container
        if os.path.exists(ONTOLOGY_PATH_IN_CONTAINER):
            try:
                with open(ONTOLOGY_PATH_IN_CONTAINER, 'r', encoding='utf-8') as f: 
                    ontology_content = f.read()
                logger.info(f"Successfully loaded {ONTOLOGY_PATH_IN_CONTAINER}.")
            except Exception as e: 
                logger.error(f"Error reading ontology file at {ONTOLOGY_PATH_IN_CONTAINER}: {e}", exc_info=True)
                error_message = f"*Error reading ontology file: {e}*"
        else: 
            logger.error(f"Ontology file not found at expected path: {ONTOLOGY_PATH_IN_CONTAINER}")
            error_message = "*Error: ontology.md file not found.*"

        return error_message if error_message else ontology_content 