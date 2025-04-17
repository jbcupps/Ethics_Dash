"""Registers callbacks for the ontology display tab."""

import os
import logging
from dash import Input, Output, callback
from flask import current_app

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
        # ... (Implementation from previous step) ...
        logger.info("Loading ontology.md for display.")
        ontology_content = ""
        error_message = ""
        ontology_path = os.path.join(current_app.root_path, 'ontology.md')
        if not os.path.exists(ontology_path):
             ontology_path_alt = os.path.join(os.path.dirname(__file__), '..', 'ontology.md') # Adjust path relative to ontology.py
             if os.path.exists(ontology_path_alt): ontology_path = ontology_path_alt
             else: logger.error(f"ontology.md not found: {ontology_path} or {ontology_path_alt}"); error_message = "*Error: ontology.md file not found.*"; ontology_path = None

        if ontology_path:
            try:
                with open(ontology_path, 'r', encoding='utf-8') as f: ontology_content = f.read()
                logger.info("Successfully loaded ontology.md.")
            except Exception as e: logger.error(f"Error reading ontology: {e}", exc_info=True); error_message = f"*Error reading ontology file: {e}*"

        return error_message if error_message else ontology_content 