"""Registers callbacks related to form interactions (Add/Edit Meme)."""

import requests
import logging
import datetime
from dash import html, dcc, Input, Output, State, ALL, callback, no_update, ctx
import dash_bootstrap_components as dbc
from bson.json_util import dumps, loads
from bson import ObjectId
from bson.errors import InvalidId
from flask import current_app # Use current_app for logger
import os  # <- added import (keep near the other standard imports at top)

# Import helpers 
from .helpers import create_morphism_inputs, create_mapping_inputs 

logger = logging.getLogger(__name__)

# Config
# Determine the base API URL from environment or default to the Docker Compose service
# The `.env` file (and docker‑compose) sets BACKEND_API_URL to something like
#     http://ai-backend:5000/api
# We append the `/memes` segment here so that all subsequent calls can simply add
# a trailing slash or additional path fragments as required.

# Get the base URL for the backend (no trailing slash)
_base_api_url = os.getenv("BACKEND_API_URL", "http://ai-backend:5000/api").rstrip("/")

# Final URL pointing to the memes sub‑resource
BACKEND_API_URL = f"{_base_api_url}/memes"

MAX_NAME_LENGTH = 100
MAX_DESC_LENGTH = 5000
MAX_TAG_LENGTH = 50
MAX_ATTR_LENGTH = 1000
MAX_MORPH_DESC_LENGTH = 500
MAX_MAP_CONCEPT_LENGTH = 100
MAX_MAP_CATEGORY_LENGTH = 100

# --- Registration Function --- 
def register_form_callbacks(dash_app):

    # Callback to generate dynamic attribute inputs based on dimensions
    @dash_app.callback(
        Output('dynamic-meme-attribute-inputs', 'children'),
        Input('meme-ethical-dimension', 'value')
    )
    def update_dimension_inputs(dimensions):
        """Dynamically generates input fields based on selected ethical dimensions."""
        # ... (Implementation from meme_management.py) ...
        attribute_inputs = []
        if dimensions is None: return []
        if 'Deontology' in dimensions: attribute_inputs.extend([html.Label("Rules (comma-separated):"), dcc.Input(id={'type': 'dynamic-meme-attr-input', 'index': 'deontology-rules'}, type='text'), html.Label("Duties (comma-separated):"), dcc.Input(id={'type': 'dynamic-meme-attr-input', 'index': 'deontology-duties'}, type='text')])
        if 'Teleology' in dimensions: attribute_inputs.extend([html.Label("Goals (comma-separated):"), dcc.Input(id={'type': 'dynamic-meme-attr-input', 'index': 'teleology-goals'}, type='text'), html.Label("Consequences (comma-separated):"), dcc.Input(id={'type': 'dynamic-meme-attr-input', 'index': 'teleology-consequences'}, type='text')])
        if 'Areteology' in dimensions: attribute_inputs.extend([html.Label("Related Virtues (comma-separated):"), dcc.Input(id={'type': 'dynamic-meme-attr-input', 'index': 'areteology-related-virtues'}, type='text'), html.Label("Conflicting Virtues (comma-separated):"), dcc.Input(id={'type': 'dynamic-meme-attr-input', 'index': 'areteology-conflicting-virtues'}, type='text')])
        if 'Opt-Out' in dimensions: attribute_inputs.extend([html.Label("Reason for Opt-Out:"), dcc.Textarea(id={'type': 'dynamic-meme-attr-input', 'index': 'opt_out-reason'})])
        return attribute_inputs

    # Save meme callback (Handles dynamic inputs)
    @dash_app.callback(
        Output('alert-message', 'children'),
        Output('alert-message', 'is_open'),
        Output('meme-id-store', 'value'),
        Output('meme-name', 'value'),
        Output('meme-description', 'value'),
        Output('meme-ethical-dimension', 'value'),
        Output('meme-tags', 'value'),
        Output('morphisms-container', 'children'),
        Output('mappings-container', 'children'),
        Output('meme-is-merged', 'value'),
        Output('meme-merged-from', 'value'),
        Output('meme-update-trigger-store', 'data'),
        Output('dynamic-meme-attribute-inputs', 'children'),
        Input('save-meme-button', 'n_clicks'),
        Input('clear-form-button', 'n_clicks'),
        Input('meme-database-table', 'active_cell'),
        State('meme-id-store', 'value'),
        State('meme-name', 'value'),
        State('meme-description', 'value'),
        State('meme-ethical-dimension', 'value'),
        State({'type': 'dynamic-meme-attr-input', 'index': ALL}, 'value'),
        State({'type': 'dynamic-meme-attr-input', 'index': ALL}, 'id'),
        State('meme-tags', 'value'),
        State({'type': 'morphism-type', 'index': ALL}, 'value'),
        State({'type': 'morphism-target', 'index': ALL}, 'value'),
        State({'type': 'morphism-desc', 'index': ALL}, 'value'),
        State({'type': 'mapping-concept', 'index': ALL}, 'value'),
        State({'type': 'mapping-category', 'index': ALL}, 'value'),
        State({'type': 'mapping-type', 'index': ALL}, 'value'),
        State('meme-is-merged', 'value'),
        State('meme-merged-from', 'value'),
        State('meme-database-table', 'data'),
        prevent_initial_call=True
    )
    def handle_form_actions(save_clicks, clear_clicks, active_cell, meme_id, name, description, dimension_values, dynamic_input_values, dynamic_input_ids, tags, morphism_types, morphism_targets, morphism_descs, mapping_concepts, mapping_categories, mapping_types, is_merged_value, merged_from_ids, table_data):
        """Handles form saving, clearing, and edit selections based on the trigger."""
        triggered_id = ctx.triggered_id
        if triggered_id == 'save-meme-button':
            if not save_clicks:
                return no_update, False, *([no_update]*11)
            # --- Input Validation --- 
            errors = []
            if not name or not isinstance(name, str):
                errors.append("Name is required.")
            elif len(name) > MAX_NAME_LENGTH:
                 errors.append(f"Name exceeds maximum length of {MAX_NAME_LENGTH} characters.")

            if not description or not isinstance(description, str):
                errors.append("Description is required.")
            elif len(description) > MAX_DESC_LENGTH:
                 errors.append(f"Description exceeds maximum length of {MAX_DESC_LENGTH} characters.")

            if tags and not isinstance(tags, str):
                 errors.append("Tags must be a comma-separated string.")
            elif tags:
                 tag_list = [t.strip() for t in tags.split(",") if t.strip()]
                 if any(len(t) > MAX_TAG_LENGTH for t in tag_list):
                     errors.append(f"One or more tags exceed maximum length of {MAX_TAG_LENGTH} characters.")

            if dimension_values and not isinstance(dimension_values, list):
                errors.append("Ethical Dimensions must be a list.")
                # Stop further dimension processing if type is wrong
                dimension_values = [] 

            # Validate dynamic attributes
            dynamic_inputs = {}
            if dimension_values:
                valid_dynamic_inputs = True
                if not isinstance(dynamic_input_values, list) or not isinstance(dynamic_input_ids, list) or len(dynamic_input_values) != len(dynamic_input_ids):
                    errors.append("Internal error: Mismatched dynamic attribute values and IDs.")
                    valid_dynamic_inputs = False
                else:
                    for i, val in enumerate(dynamic_input_values):
                        input_id_dict = dynamic_input_ids[i]
                        if not isinstance(input_id_dict, dict) or 'index' not in input_id_dict:
                            errors.append(f"Internal error: Invalid dynamic attribute ID structure at index {i}.")
                            valid_dynamic_inputs = False
                            break 
                        input_index = input_id_dict['index']
                        if val is not None and not isinstance(val, str):
                            errors.append(f"Dynamic attribute '{input_index}' must be text.")
                            valid_dynamic_inputs = False
                        elif val and len(val) > MAX_ATTR_LENGTH:
                            errors.append(f"Dynamic attribute '{input_index}' exceeds maximum length of {MAX_ATTR_LENGTH} characters.")
                            valid_dynamic_inputs = False
                        elif val:
                            dynamic_inputs[input_index] = val # Store valid, non-empty values
                
                if not valid_dynamic_inputs:
                     # Avoid processing dynamic attrs further if structure is wrong
                     dynamic_inputs = {}

            # Validate Morphisms
            morphisms_list = []
            if not isinstance(morphism_types, list) or not isinstance(morphism_targets, list) or not isinstance(morphism_descs, list) or \
               not (len(morphism_types) == len(morphism_targets) == len(morphism_descs)):
                errors.append("Internal error: Mismatched morphism input lists.")
            else:
                for i, m_type in enumerate(morphism_types):
                    target_id_str = morphism_targets[i]
                    desc = morphism_descs[i]
                    if m_type or target_id_str or desc: # Only validate if any field is filled
                        if not m_type or not isinstance(m_type, str):
                            errors.append(f"Morphism {i+1}: Type is required.")
                        if not target_id_str or not isinstance(target_id_str, str):
                            errors.append(f"Morphism {i+1}: Target Meme ID is required.")
                        else:
                            try: target_oid = ObjectId(target_id_str)
                            except InvalidId: errors.append(f"Morphism {i+1}: Invalid Target Meme ID format ('{target_id_str}').")
                        if desc is not None and not isinstance(desc, str):
                            errors.append(f"Morphism {i+1}: Description must be text.")
                        elif desc and len(desc) > MAX_MORPH_DESC_LENGTH:
                             errors.append(f"Morphism {i+1}: Description exceeds maximum length of {MAX_MORPH_DESC_LENGTH} characters.")

            # Validate Mappings
            mappings_list = []
            if not isinstance(mapping_concepts, list) or not isinstance(mapping_categories, list) or not isinstance(mapping_types, list) or \
               not (len(mapping_concepts) == len(mapping_categories) == len(mapping_types)):
                 errors.append("Internal error: Mismatched mapping input lists.")
            else:
                for i, concept in enumerate(mapping_concepts):
                     category = mapping_categories[i]
                     map_type = mapping_types[i]
                     if concept or category or map_type: # Only validate if any field is filled
                        if not concept or not isinstance(concept, str):
                            errors.append(f"Mapping {i+1}: Target Concept is required.")
                        elif len(concept) > MAX_MAP_CONCEPT_LENGTH:
                             errors.append(f"Mapping {i+1}: Target Concept exceeds maximum length of {MAX_MAP_CONCEPT_LENGTH} characters.")
                        if not category or not isinstance(category, str):
                            errors.append(f"Mapping {i+1}: Target Category is required.")
                        elif len(category) > MAX_MAP_CATEGORY_LENGTH:
                             errors.append(f"Mapping {i+1}: Target Category exceeds maximum length of {MAX_MAP_CATEGORY_LENGTH} characters.")
                        if not map_type or not isinstance(map_type, str):
                            errors.append(f"Mapping {i+1}: Mapping Type is required.")
            
            # Validate Merged Tokens
            is_merged = True if isinstance(is_merged_value, list) and 'IS_MERGED' in is_merged_value else False
            merged_from_objectids = []
            if is_merged:
                 if not merged_from_ids or not isinstance(merged_from_ids, list):
                     errors.append("Merged Tokens: At least one source token ID is required when 'Is Merged' is checked.")
                 elif any(not isinstance(token_id, str) for token_id in merged_from_ids):
                     errors.append("Internal error: Merged source token IDs must be strings.")
                 else:
                     for token_id in merged_from_ids:
                         if not token_id:
                             errors.append("Merged Tokens: Source token IDs cannot be empty.")
                             continue
                         try: ObjectId(token_id) # Validate format only
                         except InvalidId: errors.append(f"Merged Tokens: Invalid source token ID format ('{token_id}').")

            # --- Handle Validation Results --- 
            if errors:
                error_message = html.Ul([html.Li(e) for e in errors])
                current_app.logger.warning(f"Validation failed for saving meme '{name}': {errors}")
                return error_message, True, *([no_update]*11) # Show errors, keep form state

            # --- Construct Payload (if validation passed) --- 
            dimension_specific_attributes = {}
            if dimension_values:
                # Use the validated dynamic_inputs dictionary
                if "Deontology" in dimension_values: dimension_specific_attributes["deontology"] = {k: [i.strip() for i in v.split(',') if i.strip()] for k, v in [('rules', dynamic_inputs.get('deontology-rules','')), ('duties', dynamic_inputs.get('deontology-duties',''))] if v}
                if "Teleology" in dimension_values: dimension_specific_attributes["teleology"] = {k: [i.strip() for i in v.split(',') if i.strip()] for k, v in [('goals', dynamic_inputs.get('teleology-goals','')), ('consequences', dynamic_inputs.get('teleology-consequences',''))] if v}
                if "Areteology" in dimension_values: dimension_specific_attributes["areteology"] = {k: [i.strip() for i in v.split(',') if i.strip()] for k, v in [('related_virtues', dynamic_inputs.get('areteology-related-virtues','')), ('conflicting_virtues', dynamic_inputs.get('areteology-conflicting-virtues',''))] if v}
                if "Opt-Out" in dimension_values: dimension_specific_attributes["opt_out"] = {"reason": dynamic_inputs.get("opt_out-reason", "")}

            morphisms_list = []
            for i, m_type in enumerate(morphism_types):
                target_id_str = morphism_targets[i]
                desc = morphism_descs[i]
                if m_type and target_id_str: # Re-check required fields post-validation
                    try: 
                        morphisms_list.append({
                            "type": m_type,
                            "target_meme_id": ObjectId(target_id_str),
                            "description": desc or ""
                        })
                    except InvalidId: pass # Should have been caught by validation 
            
            mappings_list = []
            for i, concept in enumerate(mapping_concepts):
                category = mapping_categories[i]
                map_type = mapping_types[i]
                if concept and category and map_type: # Re-check required fields post-validation
                    mappings_list.append({
                        "target_concept": concept,
                        "target_category": category,
                        "mapping_type": map_type
                    })
            
            # Re-validate and convert merged_from_ids (already validated format)
            merged_from_objectids = []
            if is_merged and merged_from_ids:
                for token_id in merged_from_ids:
                    try: merged_from_objectids.append(ObjectId(token_id))
                    except InvalidId: pass # Should have been caught by validation

            tag_list = [t.strip() for t in tags.split(",") if t.strip()] if tags else []
            
            meme_payload_dict = {
                "name": name,
                "description": description,
                "ethical_dimension": dimension_values or [],
                "tags": tag_list,
                "dimension_specific_attributes": dimension_specific_attributes or None,
                "morphisms": morphisms_list,
                "cross_category_mappings": mappings_list,
                "is_merged_token": is_merged,
                "merged_from_tokens": merged_from_objectids
            }

            # --- API Call --- 
            cleaned_payload = {k: v for k, v in meme_payload_dict.items() if not (v is None or (isinstance(v, (list, dict)) and not v))}
            if 'is_merged_token' in meme_payload_dict: cleaned_payload['is_merged_token'] = meme_payload_dict['is_merged_token']
            try: payload_json_str = dumps(cleaned_payload)
            except Exception as e: logger.error(f"Error serializing payload: {e}", exc_info=True); return f"Internal error.", True, *([no_update]*11)
            try:
                headers = {'Content-Type': 'application/json'}; action = ""; response=None
                if meme_id: url = f"{BACKEND_API_URL}/{meme_id}"; response = requests.put(url, data=payload_json_str, headers=headers); action = "updated"
                else: url = BACKEND_API_URL + "/"; response = requests.post(url, data=payload_json_str, headers=headers); action = "created"
                if response.ok: clear_values = ["", "", "", [], "", [], [], [], []]; trigger_data = datetime.datetime.now().timestamp(); return f"Meme {action}!", True, *clear_values, trigger_data, []
                else: error_data = response.json(); details = error_data.get('detail', f'Status {response.status_code}'); return f"Save failed: {details}", True, *([no_update]*11)
            except requests.exceptions.RequestException as e: return f"Network error: {e}", True, *([no_update]*11)
            except Exception as e: return f"Unexpected error: {e}", True, *([no_update]*11)
        elif triggered_id == 'clear-form-button':
            if not clear_clicks:
                return no_update, False, *([no_update]*11)
            logger.info("Clearing form fields.")
            clear_values = ["", "", "", [], "", [], [], [], []]
            return "", False, *clear_values, None, []
        elif triggered_id == 'meme-database-table':
            if not active_cell or not table_data:
                return no_update, False, *([no_update]*11)
            meme_id = table_data[active_cell['row']].get('_id')
            logger.info(f"Storing data for editing meme ID: {meme_id}")
            full_meme_data = {}
            if meme_id:
                try:
                    url = f"{BACKEND_API_URL}/{meme_id}"
                    response = requests.get(url, timeout=5)
                    response.raise_for_status()
                    full_meme_data = loads(response.text)
                except Exception as e:
                    logger.error(f"Error fetching/decoding full meme {meme_id}: {e}")
                    return f"Error loading data: {e}", True, *([no_update]*11)
            else:
                return "No meme ID selected.", True, *([no_update]*11)
            name = full_meme_data.get('name', '')
            description = full_meme_data.get('description', '')
            dimensions = full_meme_data.get('ethical_dimension', [])
            tags = ", ".join(full_meme_data.get('tags', []) or [])
            is_merged = ['IS_MERGED'] if full_meme_data.get('is_merged_token', False) else []
            merged_from_ids = [str(oid) for oid in full_meme_data.get('merged_from_tokens', []) if oid]
            return "", False, meme_id, name, description, dimensions, tags, is_merged, merged_from_ids, full_meme_data, [], []
        return no_update, False, *([no_update]*11)

    # Callback to show/hide the merged_from dropdown
    @dash_app.callback(
        Output('merged-from-row', 'style'),
        Input('meme-is-merged', 'value')
    )
    def toggle_merged_from_visibility(is_merged_value):
        # ... (Implementation from meme_management.py) ...
        return {'display': 'flex'} if is_merged_value and 'IS_MERGED' in is_merged_value else {'display': 'none'}

    # Callback to populate form when a row is selected (Handles dynamic inputs via store)
    @dash_app.callback(
        Output('meme-id-store', 'value'),
        Output('meme-name', 'value'),
        Output('meme-description', 'value'),
        Output('meme-ethical-dimension', 'value'),
        Output('meme-tags', 'value'),
        Output('meme-is-merged', 'value'),
        Output('meme-merged-from', 'value'),
        Output('edit-meme-store', 'data'),
        Output('dynamic-meme-attribute-inputs', 'children'),
        Output('morphisms-container', 'children'),
        Output('mappings-container', 'children'),
        Input('clear-form-button', 'n_clicks'),
        Input('meme-database-table', 'active_cell'),
        State('meme-database-table', 'data'),
        prevent_initial_call=True
    )
    def handle_form_actions(clear_clicks, active_cell, table_data):
        """Handles form clearing and edit selections based on the trigger."""
        triggered_id = ctx.triggered_id
        if triggered_id == 'clear-form-button':
            if not clear_clicks:
                return no_update
            logger.info("Clearing form fields.")
            clear_values = ["", "", "", [], "", [], [], [], []]
            return *clear_values, None, []
        elif triggered_id == 'meme-database-table':
            if not active_cell or not table_data:
                return no_update, *([no_update]*7), None, [], [], []
            meme_id = table_data[active_cell['row']].get('_id')
            logger.info(f"Storing data for editing meme ID: {meme_id}")
            full_meme_data = {}
            if meme_id:
                try:
                    url = f"{BACKEND_API_URL}/{meme_id}"
                    response = requests.get(url, timeout=5)
                    response.raise_for_status()
                    full_meme_data = loads(response.text)
                except Exception as e:
                    logger.error(f"Error fetching/decoding full meme {meme_id}: {e}")
                    return no_update, *([no_update]*7), None, [], [], []
            else:
                return no_update, *([no_update]*7), None, [], [], []
            name = full_meme_data.get('name', '')
            description = full_meme_data.get('description', '')
            dimensions = full_meme_data.get('ethical_dimension', [])
            tags = ", ".join(full_meme_data.get('tags', []) or [])
            is_merged = ['IS_MERGED'] if full_meme_data.get('is_merged_token', False) else []
            merged_from_ids = [str(oid) for oid in full_meme_data.get('merged_from_tokens', []) if oid]
            return (meme_id, name, description, dimensions, tags, is_merged, merged_from_ids, full_meme_data, [], [], [])
        return no_update

    # Callback to generate dynamic attribute inputs when editing
    @dash_app.callback(
        Output('dynamic-meme-attribute-inputs', 'children'),
        Input('edit-meme-store', 'data'),
        prevent_initial_call=True
    )
    def populate_dynamic_attributes_on_edit(edit_data):
        """Generates pre-filled dynamic attribute inputs based on stored edit data."""
        # ... (Implementation from meme_management.py) ...
        if not edit_data or not isinstance(edit_data, dict): return []
        attribute_inputs_children = []
        dimensions = edit_data.get('ethical_dimension', []); dim_attrs = edit_data.get('dimension_specific_attributes', None)
        if dimensions and isinstance(dim_attrs, dict):
            if 'Deontology' in dimensions and 'deontology' in dim_attrs: deon = dim_attrs['deontology']; attribute_inputs_children.extend([html.Label("Rules:"), dcc.Input(id={'type':'dynamic-meme-attr-input', 'index':'deontology-rules'}, value=",".join(deon.get('rules',[]))), html.Label("Duties:"), dcc.Input(id={'type':'dynamic-meme-attr-input', 'index':'deontology-duties'}, value=",".join(deon.get('duties',[])))])
            if 'Teleology' in dimensions and 'teleology' in dim_attrs: teleo = dim_attrs['teleology']; attribute_inputs_children.extend([html.Label("Goals:"), dcc.Input(id={'type':'dynamic-meme-attr-input', 'index':'teleology-goals'}, value=",".join(teleo.get('goals',[]))), html.Label("Cons:"), dcc.Input(id={'type':'dynamic-meme-attr-input', 'index':'teleology-consequences'}, value=",".join(teleo.get('consequences',[])))])
            if 'Areteology' in dimensions and 'areteology' in dim_attrs: arete = dim_attrs['areteology']; attribute_inputs_children.extend([html.Label("Rel Virtues:"), dcc.Input(id={'type':'dynamic-meme-attr-input', 'index':'areteology-related-virtues'}, value=",".join(arete.get('related_virtues',[]))), html.Label("Conf Virtues:"), dcc.Input(id={'type':'dynamic-meme-attr-input', 'index':'areteology-conflicting-virtues'}, value=",".join(arete.get('conflicting_virtues',[])))])
            if 'Opt-Out' in dimensions and 'opt_out' in dim_attrs: optout = dim_attrs['opt_out']; attribute_inputs_children.extend([html.Label("Opt-Out Reason:"), dcc.Textarea(id={'type':'dynamic-meme-attr-input', 'index':'opt_out-reason'}, value=optout.get('reason',''))])
        else: logger.debug("No dimensions or attributes in edit_data.")
        return attribute_inputs_children 