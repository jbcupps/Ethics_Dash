"""Registers all callbacks for the application."""

# Import individual registration functions
# from .meme_management import register_meme_management_callbacks # Replaced by below
from .form_callbacks import register_form_callbacks
from .data_loading_callbacks import register_data_loading_callbacks
from .dynamic_inputs import register_dynamic_input_callbacks
# from .analysis import register_analysis_callbacks # Removed analysis callbacks
from .ontology import register_ontology_callbacks
from .visualization import register_visualization_callbacks
from .meme_management import register_meme_mgmt_callbacks

def register_all_callbacks(dash_app):
    """Calls all individual callback registration functions."""
    # register_meme_management_callbacks(dash_app) # Replaced by below
    register_form_callbacks(dash_app)
    register_data_loading_callbacks(dash_app)
    register_dynamic_input_callbacks(dash_app)
    # register_analysis_callbacks(dash_app) # Removed analysis callbacks
    register_ontology_callbacks(dash_app)
    register_visualization_callbacks(dash_app)
    register_meme_mgmt_callbacks(dash_app) 