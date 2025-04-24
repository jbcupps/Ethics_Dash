"""Registers callbacks for loading data into components (dropdowns, tables)."""

import requests
import logging
import os  # To read env var for backend URL
import traceback
from dash import Input, Output, callback

logger = logging.getLogger(__name__)

# Config
# Build the backend API base URL dynamically from environment variable to avoid
# hard‑coding the Docker hostname. Docker‑compose sets BACKEND_API_URL to
# something like `http://ai-backend:5000/api` – we ensure there is no trailing
# slash and then append the `/memes` segment that this callback module needs.

# Fix API URL construction - need to handle both internal Docker networking and local routes
_base_api_url = os.getenv("BACKEND_API_URL", "/api")
# Remove any trailing slash
_base_api_url = _base_api_url.rstrip("/")
# If given as a relative path (starts with '/'), convert to absolute URL pointing to Flask inside container
if not _base_api_url.startswith("http"):
    _base_api_url = f"http://localhost:5000{_base_api_url}"
# Assemble full endpoint URL for memes
BACKEND_API_URL = f"{_base_api_url}/memes"

logger.info(f"Data loading callbacks configured to use API URL: {BACKEND_API_URL}")

# --- Registration Function --- 
def register_data_loading_callbacks(dash_app):

    # Callback to update STATIC meme dropdowns (merged, analysis)
    @dash_app.callback(
        Output('meme-merged-from', 'options'),
        Input('meme-update-trigger-store', 'data'), # Triggered by successful saves
        Input('meme-initial-load', 'n_intervals'), # Also trigger on initial load
        prevent_initial_call=False
    )
    def update_static_meme_dropdowns(trigger_data, n_intervals):
        """Fetches memes from the API and populates STATIC dropdown options (merged)."""
        logger.info(f"Updating STATIC meme dropdowns triggered by store update: {trigger_data} or intervals: {n_intervals}")
        options = []
        try:
            url = BACKEND_API_URL + "/"
            logger.info(f"Requesting memes from: {url}")
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            memes = response.json() # Assumes API returns simple JSON list for this
            if isinstance(memes, list):
                options = [{'label': meme.get('name', 'Unnamed Meme'), 'value': meme.get('_id')}
                           for meme in memes if meme.get('_id') and meme.get('name')]
                logger.info(f"Successfully fetched {len(options)} memes for dropdowns")
            else:
                logger.error(f"API returned non-list data for meme dropdowns: {type(memes)}")
        except requests.exceptions.Timeout: 
            logger.error(f"Timeout fetching memes from {url} for dropdowns.")
        except requests.exceptions.RequestException as e: 
            logger.error(f"Error fetching memes from {url} for dropdowns: {e}", exc_info=True)
        except Exception as e: 
            logger.error(f"Unexpected error processing memes for dropdowns: {e}", exc_info=True)
            
        # Emergency debugging for empty options
        if not options:
            logger.warning(f"Empty dropdown options returned, debugging info: {traceback.format_exc()}")
        return options

    # Callback to populate the meme data table
    @dash_app.callback(
        Output('meme-database-table', 'data'),
        Input('meme-update-trigger-store', 'data'), # Triggered by successful saves
        Input('meme-initial-load', 'n_intervals'), # Also trigger on initial load
        prevent_initial_call=False
    )
    def update_meme_table(trigger_data, n_intervals):
        """Fetches memes from the API and populates the DataTable."""
        logger.info(f"Updating meme table triggered by store update: {trigger_data} or intervals: {n_intervals}")
        memes_data = []
        try:
            url = BACKEND_API_URL + "/"
            logger.info(f"Requesting memes from: {url}")
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            logger.info(f"Response status: {response.status_code}, Content length: {len(response.content)}")
            
            memes = response.json() # Assumes API returns simple JSON list for this
            if isinstance(memes, list):
                logger.info(f"Received {len(memes)} memes from API")
                for meme in memes:
                    # Ensure all required string fields for the table exist
                    meme['ethical_dimension_str'] = ", ".join(meme.get('ethical_dimension', []) or [])
                    meme['tags_str'] = ", ".join(meme.get('tags', []) or [])
                    # Format the boolean is_merged_token for display
                    meme['is_merged_token'] = "Yes" if meme.get('is_merged_token', False) else "No" 
                    # Ensure description exists (even if empty) for markdown rendering
                    meme['description'] = meme.get('description', '') 
                memes_data = memes
                logger.info(f"Successfully fetched {len(memes_data)} memes for table.")
            else: 
                logger.error(f"API returned non-list data for memes table: {type(memes)}")
        except requests.exceptions.Timeout: 
            logger.error(f"Timeout fetching memes from {url} for table.")
        except requests.exceptions.RequestException as e: 
            logger.error(f"Error fetching memes from {url} for table: {e}", exc_info=True)
        except Exception as e: 
            logger.error(f"Unexpected error processing memes for table: {e}\n{traceback.format_exc()}")
            
        # Emergency debugging for empty table
        if not memes_data:
            logger.warning(f"Empty table data returned, debugging info: {traceback.format_exc()}")
        return memes_data 