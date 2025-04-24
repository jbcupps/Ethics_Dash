"""Registers callbacks for graph visualization."""

import requests
import logging
import os
from dash import Input, Output
from bson.json_util import loads
# from bson import ObjectId # Removed unused import

logger = logging.getLogger(__name__)

# Config - derive from environment variable so it works in multiple environments
# (local vs Docker Compose vs cloud). We rely on BACKEND_API_URL variable set in
# `.env` or runtime environment, defaulting to the docker‑compose service name.

_base_api_url = os.getenv("BACKEND_API_URL", "http://ai-backend:5000/api").rstrip("/")
BACKEND_API_URL = f"{_base_api_url}/memes"

def register_visualization_callbacks(dash_app):

    @dash_app.callback(
        Output('meme-cytoscape-graph', 'elements'),
        Input('meme-update-trigger-store', 'data') # Update when memes change
        # prevent_initial_call=True # Might want to load initially
    )
    def update_meme_graph(trigger_data):
        """Fetches memes and constructs graph elements for Cytoscape."""
        logger.info(f"Updating meme graph triggered by store update: {trigger_data}")
        nodes = []
        edges = []
        
        try:
            url = BACKEND_API_URL + "/"
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            # Use loads to handle potential BSON types like ObjectId
            memes = loads(response.text) 
            
            if isinstance(memes, list):
                logger.info(f"Generating graph elements for {len(memes)} memes.")
                for meme in memes:
                    meme_id_str = str(meme.get('_id'))
                    if not meme_id_str:
                        continue # Skip memes without ID
                        
                    # Create node for the meme
                    nodes.append({
                        'data': {
                            'id': meme_id_str, 
                            'label': meme.get('name', 'Unnamed')[:20] # Short label
                        }
                    })
                    
                    # Create edges for morphisms
                    morphisms = meme.get('morphisms', [])
                    if isinstance(morphisms, list):
                        for morph in morphisms:
                            if isinstance(morph, dict):
                                target_id = morph.get('target_meme_id')
                                target_id_str = str(target_id) if target_id else None
                                morph_type = morph.get('type', 'relates')
                                
                                if target_id_str:
                                    # Ensure target node exists for valid edge
                                    # (Cytoscape might handle missing targets, but good practice)
                                    # For simplicity here, we assume target exists if ID is present
                                    edges.append({
                                        'data': {
                                            # Edge ID needs source+target to be unique-ish
                                            'id': f"{meme_id_str}-{target_id_str}-{morph_type}", 
                                            'source': meme_id_str,
                                            'target': target_id_str,
                                            'label': morph_type # Display morphism type
                                        }
                                    })
            else:
                logger.error(f"API returned non-list data for graph: {type(memes)}")

        except requests.exceptions.RequestException as e:
            logger.error(f"Error fetching memes for graph: {e}", exc_info=True)
        except Exception as e:
             logger.error(f"Unexpected error processing memes for graph: {e}", exc_info=True)

        return nodes + edges 