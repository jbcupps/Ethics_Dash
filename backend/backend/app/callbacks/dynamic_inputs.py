"""Registers callbacks related to adding/managing dynamic inputs."""

# import requests # Unused
import logging
# Removed ctx, MATCH from import
from dash import Input, Output, State, callback, ALL

# Import helpers 
from .helpers import create_morphism_inputs, create_mapping_inputs 

logger = logging.getLogger(__name__)

# --- Registration Function --- 
def register_dynamic_input_callbacks(dash_app):

    # Callback to add new morphism input group
    # (Moved from original dash_callbacks.py)
    @dash_app.callback(
        Output('morphisms-container', 'children', allow_duplicate=True),
        Input('add-morphism-button', 'n_clicks'),
        State('morphisms-container', 'children'),
        State('meme-merged-from', 'options'), # Use merged-from dropdown options
        prevent_initial_call=True
    )
    def add_morphism(n_clicks, existing_children, meme_options):
        """Adds a new set of morphism inputs to the container."""
        if not existing_children: existing_children = []
        new_index = len(existing_children)
        new_input_group = create_morphism_inputs(new_index, meme_options)
        existing_children.append(new_input_group)
        return existing_children

    # Callback to add new mapping input group
    # (Moved from original dash_callbacks.py)
    @dash_app.callback(
        Output('mappings-container', 'children'),
        Input('add-mapping-button', 'n_clicks'),
        State('mappings-container', 'children'),
        prevent_initial_call=True
    )
    def add_mapping(n_clicks, existing_children):
        """Adds a new set of mapping inputs to the container."""
        if not existing_children: existing_children = []
        new_index = len(existing_children)
        new_input_group = create_mapping_inputs(new_index)
        existing_children.append(new_input_group)
        return existing_children

    # Callback to REMOVE a morphism input group
    @dash_app.callback(
        Output('morphisms-container', 'children', allow_duplicate=True),
        # Use ALL instead of MATCH for pattern matching
        Input({'type': 'remove-morphism-button', 'index': ALL}, 'n_clicks'),
        State('morphisms-container', 'children'),
        prevent_initial_call=True
    )
    def remove_morphism(n_clicks_list, existing_children):
        if not n_clicks_list or not existing_children or not any(n for n in n_clicks_list if n):
            return existing_children # No clicks or nothing to remove

        # Find which button was clicked by looking for a change in n_clicks
        clicked_index = None
        for i, n_clicks in enumerate(n_clicks_list):
            if n_clicks:
                clicked_index = i
                break
                
        if clicked_index is None:
            return existing_children

        # Get the index of the button that was clicked
        remove_index = clicked_index
        logger.info(f"Removing morphism at index {remove_index}")

        # Filter out the child whose card ID matches the removed index
        updated_children = [
            child for child in existing_children 
            if not (isinstance(child, dict) 
                    and child.get('props', {}).get('id', {}).get('type') == 'morphism-card' 
                    and child.get('props', {}).get('id', {}).get('index') == remove_index)
        ]
        
        # It might be necessary to re-index subsequent components if IDs rely on order,
        # but since we use pattern matching for saving, simply removing should be okay.
        # If re-indexing is needed, it adds complexity.

        return updated_children

    # Callback to REMOVE a mapping input group
    @dash_app.callback(
        Output('mappings-container', 'children'),
        # Use ALL instead of MATCH for pattern matching
        Input({'type': 'remove-mapping-button', 'index': ALL}, 'n_clicks'),
        State('mappings-container', 'children'),
        prevent_initial_call=True
    )
    def remove_mapping(n_clicks_list, existing_children):
        if not n_clicks_list or not existing_children or not any(n for n in n_clicks_list if n):
            return existing_children

        # Find which button was clicked by looking for a change in n_clicks
        clicked_index = None
        for i, n_clicks in enumerate(n_clicks_list):
            if n_clicks:
                clicked_index = i
                break
                
        if clicked_index is None:
            return existing_children
          
        remove_index = clicked_index
        logger.info(f"Removing mapping at index {remove_index}")

        updated_children = [
            child for child in existing_children
            if not (isinstance(child, dict)
                    and child.get('props', {}).get('id', {}).get('type') == 'mapping-card'
                    and child.get('props', {}).get('id', {}).get('index') == remove_index)
        ]
        
        return updated_children

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
        Output('mappings-container', 'children'),
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