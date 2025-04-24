"""Registers callbacks related to adding/managing dynamic inputs."""

# import requests # Unused
import logging
import json
from dash import Input, Output, State, callback, ALL, callback_context, dcc, html
from dash.exceptions import PreventUpdate
import dash_bootstrap_components as dbc

# Import helpers 
from .helpers import create_morphism_inputs, create_mapping_inputs 

logger = logging.getLogger(__name__)

# --- Registration Function --- 
def register_dynamic_input_callbacks(dash_app):
    """Register callbacks related to dynamic inputs."""
    
    # Add client-side callback for immediate visual feedback when buttons are clicked
    dash_app.clientside_callback(
        """
        function(n_clicks) {
            // This callback is triggered when buttons are clicked
            // It prevents the default delay in Dash before the server responds
            if (n_clicks) {
                return true;
            }
            return false;
        }
        """,
        Output('client-side-callback-container', 'children'),
        [Input('add-morphism-button', 'n_clicks'),
         Input('add-mapping-button', 'n_clicks')]
    )

    # --- Adding Morphism Inputs ---
    @dash_app.callback(
        Output('morphism-container', 'children'),
        [Input('add-morphism-button', 'n_clicks'),
         Input('morphism-data-store', 'data')],
        [State('morphism-container', 'children'),
         State('meme-options-store', 'data')]
    )
    def add_morphism_input(n_clicks, morphism_data, children, meme_options):
        """Add new morphism input group when button is clicked."""
        try:
            logger.debug(f"Add morphism callback triggered. n_clicks: {n_clicks}, context: {callback_context.triggered}")
            
            # Initialize empty lists if None
            if children is None:
                children = []
            
            # Parse meme options from store
            if meme_options:
                try:
                    meme_options = json.loads(meme_options) if isinstance(meme_options, str) else meme_options
                except Exception as e:
                    logger.error(f"Error parsing meme options: {e}")
                    meme_options = []
            else:
                meme_options = []
                
            # Get the triggered input
            triggered_id = callback_context.triggered[0]['prop_id'].split('.')[0] if callback_context.triggered else None
            
            # Add new morphism input if the button was clicked
            if triggered_id == 'add-morphism-button' and n_clicks:
                next_index = len(children)
                logger.debug(f"Adding new morphism input with index {next_index}")
                new_input = create_morphism_inputs(next_index, meme_options)
                children.append(new_input)
            
            # Initialize from stored data if exists 
            elif triggered_id == 'morphism-data-store' and morphism_data:
                try:
                    if isinstance(morphism_data, str):
                        morphism_data = json.loads(morphism_data)
                    
                    # Clear existing children to rebuild from stored data
                    children = []
                    for i, morphism in enumerate(morphism_data):
                        children.append(create_morphism_inputs(i, meme_options))
                except Exception as e:
                    logger.error(f"Error loading morphism data from store: {e}")
            
            return children
        except Exception as e:
            logger.error(f"Error in add_morphism_input callback: {e}")
            return children if children else []
    
    # --- Adding Mapping Inputs ---
    @dash_app.callback(
        Output('mapping-container', 'children'),
        [Input('add-mapping-button', 'n_clicks'),
         Input('mapping-data-store', 'data')],
        [State('mapping-container', 'children')]
    )
    def add_mapping_input(n_clicks, mapping_data, children):
        """Add new mapping input group when button is clicked."""
        try:
            logger.debug(f"Add mapping callback triggered. n_clicks: {n_clicks}, context: {callback_context.triggered}")
            
            # Initialize empty lists if None
            if children is None:
                children = []
            
            # Get the triggered input
            triggered_id = callback_context.triggered[0]['prop_id'].split('.')[0] if callback_context.triggered else None
            
            # Add new mapping input if the button was clicked
            if triggered_id == 'add-mapping-button' and n_clicks:
                next_index = len(children)
                logger.debug(f"Adding new mapping input with index {next_index}")
                new_input = create_mapping_inputs(next_index)
                children.append(new_input)
            
            # Initialize from stored data if exists 
            elif triggered_id == 'mapping-data-store' and mapping_data:
                try:
                    if isinstance(mapping_data, str):
                        mapping_data = json.loads(mapping_data)
                    
                    # Clear existing children to rebuild from stored data
                    children = []
                    for i, mapping in enumerate(mapping_data):
                        children.append(create_mapping_inputs(i))
                except Exception as e:
                    logger.error(f"Error loading mapping data from store: {e}")
            
            return children
        except Exception as e:
            logger.error(f"Error in add_mapping_input callback: {e}")
            return children if children else []
    
    # --- Removing Morphism Inputs ---
    @dash_app.callback(
        Output({'type': 'morphism-card', 'index': ALL}, 'style'),
        [Input({'type': 'remove-morphism-button', 'index': ALL}, 'n_clicks')],
        [State({'type': 'morphism-card', 'index': ALL}, 'style'),
         State({'type': 'morphism-card', 'index': ALL}, 'id')]
    )
    def remove_morphism_input(n_clicks, styles, ids):
        """Remove morphism input group when button is clicked."""
        try:
            logger.debug(f"Remove morphism callback triggered. context: {callback_context.triggered}")
            
            # If nothing has been clicked, prevent update
            if not callback_context.triggered or callback_context.triggered[0]['value'] is None:
                raise PreventUpdate
            
            # Handle missing styles
            if styles is None or len(styles) == 0:
                raise PreventUpdate
                
            # Create new styles list if needed
            new_styles = []
            for i, style in enumerate(styles):
                if style is None:
                    style = {'border': '1px solid #ccc', 'borderRadius': '4px'}
                new_styles.append(style)
            
            # Identify which button was clicked and hide that card
            for i, n_click in enumerate(n_clicks):
                if n_click and n_click > 0:
                    triggered_id = callback_context.triggered[0]['prop_id'].split('.')[0]
                    triggered_index = json.loads(triggered_id)['index'] if isinstance(triggered_id, str) and '{' in triggered_id else None
                    
                    # Only hide the card corresponding to the clicked button
                    if triggered_index is not None and i < len(new_styles):
                        for j, card_id in enumerate(ids):
                            if card_id['index'] == triggered_index:
                                logger.debug(f"Hiding morphism card with index {triggered_index}")
                                new_styles[j] = {'display': 'none'}
            
            return new_styles
        except PreventUpdate:
            raise
        except Exception as e:
            logger.error(f"Error in remove_morphism_input callback: {e}")
            raise PreventUpdate
    
    # --- Removing Mapping Inputs ---
    @dash_app.callback(
        Output({'type': 'mapping-card', 'index': ALL}, 'style'),
        [Input({'type': 'remove-mapping-button', 'index': ALL}, 'n_clicks')],
        [State({'type': 'mapping-card', 'index': ALL}, 'style'),
         State({'type': 'mapping-card', 'index': ALL}, 'id')]
    )
    def remove_mapping_input(n_clicks, styles, ids):
        """Remove mapping input group when button is clicked."""
        try:
            logger.debug(f"Remove mapping callback triggered. context: {callback_context.triggered}")
            
            # If nothing has been clicked, prevent update
            if not callback_context.triggered or callback_context.triggered[0]['value'] is None:
                raise PreventUpdate
            
            # Handle missing styles
            if styles is None or len(styles) == 0:
                raise PreventUpdate
                
            # Create new styles list if needed
            new_styles = []
            for i, style in enumerate(styles):
                if style is None:
                    style = {'border': '1px solid #ccc', 'borderRadius': '4px'}
                new_styles.append(style)
            
            # Identify which button was clicked and hide that card
            for i, n_click in enumerate(n_clicks):
                if n_click and n_click > 0:
                    triggered_id = callback_context.triggered[0]['prop_id'].split('.')[0]
                    triggered_index = json.loads(triggered_id)['index'] if isinstance(triggered_id, str) and '{' in triggered_id else None
                    
                    # Only hide the card corresponding to the clicked button
                    if triggered_index is not None and i < len(new_styles):
                        for j, card_id in enumerate(ids):
                            if card_id['index'] == triggered_index:
                                logger.debug(f"Hiding mapping card with index {triggered_index}")
                                new_styles[j] = {'display': 'none'}
            
            return new_styles
        except PreventUpdate:
            raise
        except Exception as e:
            logger.error(f"Error in remove_mapping_input callback: {e}")
            raise PreventUpdate

    # Callback to populate morphism inputs when editing
    @dash_app.callback(
        Output('morphisms-container', 'children', allow_duplicate=True),
        Input('edit-meme-store', 'data'),
        State('meme-merged-from', 'options'), # Need options for target dropdown
        prevent_initial_call=True
    )
    def populate_morphisms_on_edit(edit_data, meme_options):
        """Generates pre-filled morphism input groups based on stored edit data."""
        if not edit_data or not isinstance(edit_data, dict):
            return []
        
        morphisms_children = []
        morphisms_data = edit_data.get('morphisms', [])
        if not isinstance(morphisms_data, list):
             logger.warning("Morphisms data in store is not a list.")
             return []
             
        logger.info(f"Populating {len(morphisms_data)} morphisms from edit store.")
        for i, morph in enumerate(morphisms_data):
            if not isinstance(morph, dict): continue # Skip invalid entries
            input_group = create_morphism_inputs(i, meme_options or []) # Pass options
            
            # Pre-fill values by modifying the generated component structure
            # This relies on the structure defined in create_morphism_inputs
            try:
                # Access Dropdown for type
                type_dropdown = input_group.children[1].children[0].children[1].children
                type_dropdown.value = morph.get('type')
                
                # Access Dropdown for target
                target_dropdown = input_group.children[1].children[1].children[1].children
                target_id = morph.get('target_meme_id')
                # Target ID needs to be string for dropdown value
                target_dropdown.value = str(target_id) if target_id else None 

                # Access Input for description
                desc_input = input_group.children[1].children[2].children[1].children
                desc_input.value = morph.get('description', '')
                
                morphisms_children.append(input_group)
            except (AttributeError, IndexError, TypeError) as e:
                logger.error(f"Error accessing components to pre-fill morphism {i}: {e}")
                # Optionally append the non-filled group or skip
                # morphisms_children.append(input_group) 
                
        return morphisms_children

    # Callback to populate mapping inputs when editing
    @dash_app.callback(
        Output('mappings-container', 'children', allow_duplicate=True),
        Input('edit-meme-store', 'data'),
        prevent_initial_call=True
    )
    def populate_mappings_on_edit(edit_data):
        """Generates pre-filled mapping input groups based on stored edit data."""
        if not edit_data or not isinstance(edit_data, dict):
            return []

        mappings_children = []
        mappings_data = edit_data.get('cross_category_mappings', [])
        if not isinstance(mappings_data, list):
             logger.warning("Mappings data in store is not a list.")
             return []
             
        logger.info(f"Populating {len(mappings_data)} mappings from edit store.")
        for i, mapping in enumerate(mappings_data):
            if not isinstance(mapping, dict): continue
            input_group = create_mapping_inputs(i)
            
            try:
                # Access Input for concept
                concept_input = input_group.children[1].children[0].children[1].children
                concept_input.value = mapping.get('target_concept', '')
                
                # Access Dropdown for category
                cat_dropdown = input_group.children[1].children[1].children[1].children
                cat_dropdown.value = mapping.get('target_category')
                
                # Access Dropdown for type
                type_dropdown = input_group.children[1].children[2].children[1].children
                type_dropdown.value = mapping.get('mapping_type')
                
                mappings_children.append(input_group)
            except (AttributeError, IndexError, TypeError) as e:
                logger.error(f"Error accessing components to pre-fill mapping {i}: {e}")

        return mappings_children 