"""Registers callbacks for the ethical analysis tab."""

import os
import logging
from dash import Input, Output, State, callback
from flask import current_app
from bson import ObjectId
from bson.errors import InvalidId

# Import the analysis function
from backend.app.modules.llm_interface import perform_ethical_analysis, select_relevant_memes
from backend.app.db import get_all_memes_for_selection
from backend.app.api import load_ontology  # add this import

logger = logging.getLogger(__name__)

# --- Registration Function --- 
def register_analysis_callbacks(dash_app):

    # Callback to run the R2 ethical analysis
    # (Moved from original dash_callbacks.py)
    @dash_app.callback(
        Output('analysis-results-output', 'children'),
        Input('run-analysis-button', 'n_clicks'),
        State('analysis-p1-dropdown', 'value'),
        State('analysis-r1-dropdown', 'value'),
        prevent_initial_call=True
    )
    def run_r2_analysis(n_clicks, p1_meme_id, r1_meme_id):
        """Triggers the ethical analysis when the button is clicked."""
        if not n_clicks: return "Click 'Run Analysis' to start."
        if not p1_meme_id or not r1_meme_id: return "Please select both a P1 and an R1 meme."
        db = current_app.db
        if not db: return "Error: DB connection unavailable."
        
        p1_doc, r1_doc = None, None
        p1_meme_text, r1_meme_text = None, None
        try:
            p1_doc = db.ethical_memes.find_one({"_id": ObjectId(p1_meme_id)})
            r1_doc = db.ethical_memes.find_one({"_id": ObjectId(r1_meme_id)})
            if not p1_doc: logger.warning(f"P1 {p1_meme_id} not found."); return f"Error: P1 meme not found."
            if not r1_doc: logger.warning(f"R1 {r1_meme_id} not found."); return f"Error: R1 meme not found."
            p1_meme_text = p1_doc.get('description', ''); r1_meme_text = r1_doc.get('description', '')
            if not p1_meme_text: logger.warning(f"P1 {p1_meme_id} no description."); return f"Error: P1 meme has no description."
            if not r1_meme_text: logger.warning(f"R1 {r1_meme_id} no description."); return f"Error: R1 meme has no description."
        except InvalidId as e: logger.error(f"Invalid ID: {e}"); return f"Error: Invalid meme ID format."
        except Exception as e: logger.error(f"DB error fetching P1/R1: {e}", exc_info=True); return f"Error fetching meme data."
            
        # Load the ontology text using the shared helper
        ontology_content = load_ontology()
        if ontology_content is None:
            logger.error("Error loading ontology via load_ontology helper.")
            return "Error: Could not load ethical ontology."
            
        analysis_api_key = current_app.config.get('ANALYSIS_API_KEY')
        # Use the configured analysis model (Anthropic Claude Sonnet by default)
        analysis_model_name = current_app.config.get('ANALYSIS_LLM_MODEL', 'claude-3-sonnet-20240229')
        analysis_api_endpoint = current_app.config.get('ANALYSIS_API_ENDPOINT')
        
        if not analysis_api_key:
             logger.error("Analysis API Key is missing in Flask config.")
             return "Error: Analysis service API key not configured."

        try:
            # Select relevant memes based on prompt and initial response
            selected_meme_names = []
            available_memes = get_all_memes_for_selection()
            if available_memes:
                meme_selection_result = select_relevant_memes(
                    prompt=p1_meme_text,
                    r1_response=r1_meme_text,
                    available_memes=available_memes,
                    selector_api_key=analysis_api_key,
                    selector_api_endpoint=analysis_api_endpoint
                )
                if meme_selection_result:
                    selected_meme_names = meme_selection_result.selected_memes
                    logger.info(f"Selected memes for analysis: {selected_meme_names}")
                else:
                    logger.warning("Meme selection returned no results.")
            else:
                logger.warning("No memes available for selection.")

            # Perform ethical analysis with selected memes
            analysis_result_dict = perform_ethical_analysis(
                initial_prompt=p1_meme_text,
                generated_response=r1_meme_text,
                ontology=ontology_content,
                analysis_api_key=analysis_api_key,
                analysis_model_name=analysis_model_name,
                analysis_api_endpoint=analysis_api_endpoint,
                selected_meme_names=selected_meme_names
            )

            # Process the result dictionary
            if analysis_result_dict:
                logger.info("Ethical analysis successful via Dash callback.")
                summary = analysis_result_dict.get("summary_text", "[Summary not found in analysis result]")
                return f"### Ethical Analysis Results\n\n**P1 Meme:** {p1_doc.get('name', p1_meme_id)}\n**R1 Meme:** {r1_doc.get('name', r1_meme_id)}\n\n---\n\n{summary}"
            else:
                logger.warning("Ethical analysis returned None via Dash callback.")
                return "Analysis failed. LLM returned no result (check backend logs)."
        except Exception as e:
            logger.error(f"Error during analysis callback: {e}", exc_info=True)
            return f"An unexpected error occurred during analysis: {e}" 