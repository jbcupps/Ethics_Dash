"""Registers callbacks for the ethical analysis tab."""

import os
import logging
from dash import Input, Output, State, callback
from flask import current_app
from bson import ObjectId
from bson.errors import InvalidId

# Import the analysis function
from backend.app.modules.llm_interface import perform_ethical_analysis 

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
            
        ontology_content = ""
        ontology_path = os.path.join(current_app.root_path, 'ontology.md')
        if not os.path.exists(ontology_path):
             ontology_path_alt = os.path.join(os.path.dirname(__file__), '..', 'ontology.md') # Adjust path relative to analysis.py
             if os.path.exists(ontology_path_alt): ontology_path = ontology_path_alt
             else: logger.error(f"ontology.md not found: {ontology_path} or {ontology_path_alt}"); return "Error: ontology.md not found."
        try:
            with open(ontology_path, 'r', encoding='utf-8') as f: ontology_content = f.read()
        except Exception as e: logger.error(f"Error reading ontology: {e}", exc_info=True); return f"Error reading ontology file."
            
        analysis_api_key = current_app.config.get('ANALYSIS_API_KEY')
        analysis_model_name = current_app.config.get('ANALYSIS_MODEL_NAME', 'gpt-4o')
        analysis_api_endpoint = current_app.config.get('ANALYSIS_API_ENDPOINT')
        
        if not analysis_api_key:
             logger.error("Analysis API Key is missing in Flask config.")
             return "Error: Analysis service API key not configured."

        try:
            # Prepare arguments for the current perform_ethical_analysis signature
            api_config = {
                "provider": None, # Determine provider based on model name if possible, or add config
                "key": analysis_api_key,
                "model": analysis_model_name,
                "endpoint": analysis_api_endpoint
            }
            # Determine provider based on model name (simple heuristic)
            if "gpt-" in analysis_model_name.lower():
                api_config["provider"] = "OpenAI"
            elif "gemini" in analysis_model_name.lower():
                api_config["provider"] = "Gemini"
            elif "claude" in analysis_model_name.lower():
                api_config["provider"] = "Anthropic"
            else:
                 logger.warning(f"Could not determine LLM provider for model: {analysis_model_name}. Add provider config or adjust logic.")
                 # Optionally default to a provider or raise an error

            # Context might include ontology or other relevant info for the LLM call
            context_data = {"ontology": ontology_content}

            analysis_result_dict = perform_ethical_analysis(
                prompt=p1_meme_text,                # Changed from initial_prompt
                initial_response=r1_meme_text,    # Changed from generated_response
                analysis_model=analysis_model_name, # Changed from analysis_model_name
                api_config=api_config,              # Pass the constructed config dict
                context=context_data                # Pass the context dict
            )

            # Process the result dictionary
            if analysis_result_dict:
                logger.info("Ethical analysis successful via Dash callback.")
                # Extract summary and format the output
                summary = analysis_result_dict.get("summary_text", "[Summary not found in analysis result]")
                # We might want to display scores too if needed, extracted from analysis_result_dict["scores_json"]
                return f"### Ethical Analysis Results\n\n**P1 Meme:** {p1_doc.get('name', p1_meme_id)}\n**R1 Meme:** {r1_doc.get('name', r1_meme_id)}\n\n---\n\n{summary}"
            else:
                logger.warning("Ethical analysis returned None via Dash callback.")
                return "Analysis failed. LLM returned no result (check backend logs)."
        except Exception as e:
            logger.error(f"Error calling perform_ethical_analysis via Dash callback: {e}", exc_info=True)
            return f"An unexpected error occurred during analysis: {e}" 