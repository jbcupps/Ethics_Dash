"""Registers callbacks for loading data into components (dropdowns, tables)."""

import requests
import logging
from dash import Input, Output, callback

logger = logging.getLogger(__name__)

# Config
BACKEND_API_URL = "http://backend:5000/api/memes" 

# --- Registration Function --- 
def register_data_loading_callbacks(dash_app):

    # Callback to update STATIC meme dropdowns (merged, analysis)
    @dash_app.callback(
        Output('meme-merged-from', 'options'),
        Output('analysis-p1-dropdown', 'options'),
        Output('analysis-r1-dropdown', 'options'),
        Input('meme-update-trigger-store', 'data'), # Triggered by successful saves
        prevent_initial_call=False
    )
    def update_static_meme_dropdowns(trigger_data):
        """Fetches memes from the API and populates STATIC dropdown options (merged, analysis)."""
        # ... (Implementation from meme_management.py) ...
        logger.info(f"Updating STATIC meme dropdowns triggered by store update: {trigger_data}")
        options = []
        try:
            url = BACKEND_API_URL + "/"
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            memes = response.json() # Assumes API returns simple JSON list for this
            if isinstance(memes, list):
                options = [{'label': meme.get('name', 'Unnamed Meme'), 'value': meme.get('_id')}
                           for meme in memes if meme.get('_id') and meme.get('name')]
        except Exception as e:
            logger.error(f"Error fetching memes for static dropdowns: {e}")
        return options, options, options

    # Callback to populate the meme data table
    @dash_app.callback(
        Output('meme-database-table', 'data'),
        Input('meme-update-trigger-store', 'data'), # Triggered by successful saves
        prevent_initial_call=False
    )
    def update_meme_table(trigger_data):
        """Fetches memes from the API and populates the DataTable."""
        # ... (Implementation from meme_management.py) ...
        logger.info(f"Updating meme table triggered by store update: {trigger_data}")
        memes_data = []
        try:
            url = BACKEND_API_URL + "/"
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            memes = response.json() # Assumes API returns simple JSON list for this
            if isinstance(memes, list):
                for meme in memes:
                    meme['ethical_dimension_str'] = ", ".join(meme.get('ethical_dimension', []) or [])
                    meme['tags_str'] = ", ".join(meme.get('tags', []) or [])
                memes_data = memes
                logger.info(f"Successfully fetched {len(memes_data)} memes for table.")
            else: logger.error(f"API returned non-list data for memes table: {type(memes)}")
        except requests.exceptions.Timeout: logger.error(f"Timeout fetching memes from {url} for table.")
        except requests.exceptions.RequestException as e: logger.error(f"Error fetching memes from {url} for table: {e}", exc_info=True)
        except Exception as e: logger.error(f"Unexpected error processing memes for table: {e}", exc_info=True)
        return memes_data 