"""Registers callbacks related to form interactions (Add/Edit Meme)."""

import requests
import logging
import datetime
from dash import html, dcc, Input, Output, State, ALL, no_update, ctx
from bson.json_util import dumps
from bson import ObjectId
from bson.errors import InvalidId
import os

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
        attribute_inputs = []
        if dimensions is None: return []
        if 'Deontology' in dimensions: attribute_inputs.extend([html.Label("Deontology Attrs (rules, duties...):"), dcc.Textarea(id={'type': 'dynamic-meme-attr-input', 'index': 'deontology-attrs'}, placeholder="Enter details...")])
        if 'Teleology' in dimensions: attribute_inputs.extend([html.Label("Teleology Attrs (goals, consequences...):"), dcc.Textarea(id={'type': 'dynamic-meme-attr-input', 'index': 'teleology-attrs'}, placeholder="Enter details...")])
        if 'Areteology' in dimensions: attribute_inputs.extend([html.Label("Areteology Attrs (virtues, vices...):"), dcc.Textarea(id={'type': 'dynamic-meme-attr-input', 'index': 'areteology-attrs'}, placeholder="Enter details...")])
        if 'Opt-Out' in dimensions: attribute_inputs.extend([html.Label("Reason for Opt-Out:"), dcc.Textarea(id={'type': 'dynamic-meme-attr-input', 'index': 'opt_out-reason'}, placeholder="Enter details...")])
        return attribute_inputs

    # Save/Clear/Load-for-Edit meme callback
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
        Output('edit-meme-store', 'data'),
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
        alert_msg, alert_open = "", False
        form_reset_values = ["", "", "", [], "", [], [], None]
        dynamic_outputs_reset = [[], [], []]
        trigger_val = no_update

        if triggered_id == 'save-meme-button':
            if not save_clicks:
                return no_update, False, *([no_update]*12), None

            errors = []
            if not name or not isinstance(name, str): errors.append("Name is required.")
            elif len(name) > MAX_NAME_LENGTH: errors.append(f"Name exceeds {MAX_NAME_LENGTH} chars.")
            if not description or not isinstance(description, str): errors.append("Description is required.")
            elif len(description) > MAX_DESC_LENGTH: errors.append(f"Description exceeds {MAX_DESC_LENGTH} chars.")
            if tags and not isinstance(tags, str): errors.append("Tags must be comma-sep string.")
            elif tags:
                tag_list = [t.strip() for t in tags.split(",") if t.strip()]
                if any(len(t) > MAX_TAG_LENGTH for t in tag_list): errors.append(f"Tag exceeds {MAX_TAG_LENGTH} chars.")
            if dimension_values and not isinstance(dimension_values, list): errors.append("Dimensions must be list."); dimension_values = []

            dynamic_inputs = {}
            if dimension_values:
                if isinstance(dynamic_input_values, list) and isinstance(dynamic_input_ids, list) and len(dynamic_input_values) == len(dynamic_input_ids):
                    for i, val in enumerate(dynamic_input_values):
                        input_id_dict = dynamic_input_ids[i]
                        if isinstance(input_id_dict, dict) and 'index' in input_id_dict:
                             input_index = input_id_dict['index']
                             if val is not None:
                                 if not isinstance(val, str): errors.append(f"Attr '{input_index}' must be text.")
                                 elif len(val) > MAX_ATTR_LENGTH: errors.append(f"Attr '{input_index}' exceeds {MAX_ATTR_LENGTH} chars.")
                                 elif val: dynamic_inputs[input_index] = val
                        else: errors.append(f"Internal error: Invalid dyn attr ID index {i}.")
                else: errors.append("Internal error: Mismatched dyn attr values/IDs.")

            validated_morphisms = []
            if isinstance(morphism_types, list) and len(morphism_types) == len(morphism_targets) == len(morphism_descs):
                for i, m_type in enumerate(morphism_types):
                    target_id_str = morphism_targets[i]; desc = morphism_descs[i]
                    if m_type or target_id_str or desc:
                        if not m_type or not isinstance(m_type, str): errors.append(f"Morph {i+1}: Type required.")
                        target_oid=None
                        if not target_id_str or not isinstance(target_id_str, str): errors.append(f"Morph {i+1}: Target required.")
                        else:
                            try: target_oid = ObjectId(target_id_str)
                            except InvalidId: errors.append(f"Morph {i+1}: Invalid Target ID.")
                        if desc and not isinstance(desc, str): errors.append(f"Morph {i+1}: Desc must be text.")
                        elif desc and len(desc) > MAX_MORPH_DESC_LENGTH: errors.append(f"Morph {i+1}: Desc exceeds {MAX_MORPH_DESC_LENGTH} chars.")
                        if m_type and target_oid: validated_morphisms.append({"type": m_type, "target_meme_id": target_oid, "description": desc or ""})
            else: errors.append("Internal error: Mismatched morphism lists.")

            validated_mappings = []
            if isinstance(mapping_concepts, list) and len(mapping_concepts) == len(mapping_categories) == len(mapping_types):
                for i, concept in enumerate(mapping_concepts):
                    category = mapping_categories[i]; map_type = mapping_types[i]
                    if concept or category or map_type:
                        is_valid_map = True
                        if not concept or not isinstance(concept, str): errors.append(f"Map {i+1}: Concept required."); is_valid_map = False
                        elif len(concept) > MAX_MAP_CONCEPT_LENGTH: errors.append(f"Map {i+1}: Concept exceeds {MAX_MAP_CONCEPT_LENGTH} chars."); is_valid_map = False
                        if not category or not isinstance(category, str): errors.append(f"Map {i+1}: Category required."); is_valid_map = False
                        elif len(category) > MAX_MAP_CATEGORY_LENGTH: errors.append(f"Map {i+1}: Category exceeds {MAX_MAP_CATEGORY_LENGTH} chars."); is_valid_map = False
                        if not map_type or not isinstance(map_type, str): errors.append(f"Map {i+1}: Type required."); is_valid_map = False
                        if is_valid_map: validated_mappings.append({"target_concept": concept, "target_category": category, "mapping_type": map_type})
            else: errors.append("Internal error: Mismatched mapping lists.")

            is_merged = True if isinstance(is_merged_value, list) and 'IS_MERGED' in is_merged_value else False
            merged_from_objectids = []
            if is_merged:
                if not merged_from_ids or not isinstance(merged_from_ids, list): errors.append("Merged Tokens: Source IDs required.")
                else:
                    for token_id in merged_from_ids:
                        if not token_id or not isinstance(token_id, str): errors.append("Merged Tokens: Invalid source ID type/empty.")
                        else:
                            try: merged_from_objectids.append(ObjectId(token_id))
                            except InvalidId: errors.append(f"Merged Tokens: Invalid source ID format ('{token_id}').")

            if errors:
                alert_msg = html.Ul([html.Li(e) for e in errors]); alert_open = True
                logger.warning(f"Validation failed saving meme '{name}': {errors}")
                return alert_msg, alert_open, *([no_update]*11), None
            else:
                dimension_specific_attributes = {}
                if dimension_values:
                     if "Deontology" in dimension_values: dimension_specific_attributes["deontology"] = {"details": dynamic_inputs.get('deontology-attrs', '')}
                     if "Teleology" in dimension_values: dimension_specific_attributes["teleology"] = {"details": dynamic_inputs.get('teleology-attrs', '')}
                     if "Areteology" in dimension_values: dimension_specific_attributes["areteology"] = {"details": dynamic_inputs.get('areteology-attrs', '')}
                     if "Opt-Out" in dimension_values: dimension_specific_attributes["opt_out"] = {"reason": dynamic_inputs.get("opt_out-reason", "")}

                tag_list = [t.strip() for t in tags.split(",") if t.strip()] if tags else []

                meme_payload_dict = {
                    "name": name,
                    "description": description,
                    "ethical_dimension": dimension_values or [],
                    "tags": tag_list,
                    "dimension_specific_attributes": dimension_specific_attributes or None,
                    "morphisms": validated_morphisms,
                    "cross_category_mappings": validated_mappings,
                    "is_merged_token": is_merged,
                    "merged_from_tokens": merged_from_objectids
                }
                cleaned_payload = {k: v for k, v in meme_payload_dict.items() if not (v is None or (isinstance(v, (list, dict)) and not v))}
                if 'is_merged_token' in meme_payload_dict: cleaned_payload['is_merged_token'] = meme_payload_dict['is_merged_token']

                try:
                    payload_json_str = dumps(cleaned_payload)
                    headers = {'Content-Type': 'application/json'}
                    action = ""
                    response = None
                    if meme_id:
                        url = f"{BACKEND_API_URL}/{meme_id}"
                        response = requests.put(url, data=payload_json_str, headers=headers, timeout=10)
                        action = "updated"
                    else:
                        url = BACKEND_API_URL + "/"
                        response = requests.post(url, data=payload_json_str, headers=headers, timeout=10)
                        action = "created"

                    if response.ok:
                        alert_msg = f"Meme successfully {action}!"; alert_open = True
                        trigger_val = datetime.datetime.now().timestamp()
                        return alert_msg, alert_open, *form_reset_values, trigger_val, *dynamic_outputs_reset
                    else:
                        error_detail = f"Status {response.status_code}"
                        try: error_data = response.json(); error_detail = error_data.get('error', error_detail)
                        except: pass
                        alert_msg = f"Save failed: {error_detail}"; alert_open = True
                        logger.error(f"API error saving meme '{name}': {response.status_code} - {response.text}")
                        return alert_msg, alert_open, *([no_update]*11), None
                except requests.exceptions.RequestException as e:
                    alert_msg = f"Network error: {e}"; alert_open = True; logger.error(f"Network error: {e}", exc_info=True)
                    return alert_msg, alert_open, *([no_update]*11), None
                except Exception as e:
                    alert_msg = f"Unexpected error: {e}"; alert_open = True; logger.error(f"Unexpected error: {e}", exc_info=True)
                    return alert_msg, alert_open, *([no_update]*11), None

        elif triggered_id == 'clear-form-button':
            if not clear_clicks:
                return no_update, False, *([no_update]*11), None
            logger.info("Clearing form fields.")
            alert_msg = ""; alert_open = False
            return alert_msg, alert_open, *form_reset_values, no_update, *dynamic_outputs_reset

        elif triggered_id == 'meme-database-table':
            if not active_cell or not table_data:
                return no_update, False, *([no_update]*11), None

            selected_row_index = active_cell['row']
            if selected_row_index >= len(table_data):
                logger.warning(f"Selected row index {selected_row_index} out of bounds for table data len {len(table_data)}.")
                return no_update, False, *([no_update]*11), None
                
            meme_id_to_load = table_data[selected_row_index].get('_id')
            if not meme_id_to_load:
                logger.warning("No _id found in selected table row.")
                return no_update, False, *([no_update]*11), None

            logger.info(f"Loading data for editing meme ID: {meme_id_to_load}")
            full_meme_data = None
            try:
                url = f"{BACKEND_API_URL}/{meme_id_to_load}"
                response = requests.get(url, timeout=5)
                response.raise_for_status()
                full_meme_data = response.json()
            except Exception as e:
                logger.error(f"Error fetching full meme {meme_id_to_load}: {e}", exc_info=True)
                alert_msg = f"Error loading data: {e}"; alert_open = True
                return alert_msg, alert_open, *([no_update]*12), None

            if full_meme_data:
                name = full_meme_data.get('name', '')
                description = full_meme_data.get('description', '')
                dimensions = full_meme_data.get('ethical_dimension', [])
                tags = ", ".join(full_meme_data.get('tags', []) or [])
                is_merged = ['IS_MERGED'] if full_meme_data.get('is_merged_token', False) else []
                merged_from_ids = [str(oid) for oid in full_meme_data.get('merged_from_tokens', []) if oid]

                dynamic_attrs_children = []
                dim_attrs_data = full_meme_data.get('dimension_specific_attributes')
                if dimensions and isinstance(dim_attrs_data, dict):
                     if 'Deontology' in dimensions and 'deontology' in dim_attrs_data: dyn_data = dim_attrs_data['deontology'].get('details', ''); dynamic_attrs_children.extend([html.Label("Deontology Attrs:"), dcc.Textarea(id={'type': 'dynamic-meme-attr-input', 'index': 'deontology-attrs'}, value=dyn_data)])
                     if 'Teleology' in dimensions and 'teleology' in dim_attrs_data: dyn_data = dim_attrs_data['teleology'].get('details', ''); dynamic_attrs_children.extend([html.Label("Teleology Attrs:"), dcc.Textarea(id={'type': 'dynamic-meme-attr-input', 'index': 'teleology-attrs'}, value=dyn_data)])
                     if 'Areteology' in dimensions and 'areteology' in dim_attrs_data: dyn_data = dim_attrs_data['areteology'].get('details', ''); dynamic_attrs_children.extend([html.Label("Areteology Attrs:"), dcc.Textarea(id={'type': 'dynamic-meme-attr-input', 'index': 'areteology-attrs'}, value=dyn_data)])
                     if 'Opt-Out' in dimensions and 'opt_out' in dim_attrs_data: dyn_data = dim_attrs_data['opt_out'].get('reason', ''); dynamic_attrs_children.extend([html.Label("Opt-Out Reason:"), dcc.Textarea(id={'type': 'dynamic-meme-attr-input', 'index': 'opt_out-reason'}, value=dyn_data)])

                morphisms_children = []
                mappings_children = []

                alert_msg = f"Loaded '{name}' for editing."; alert_open = True
                return (alert_msg, alert_open, meme_id_to_load, name, description, dimensions, tags,
                        morphisms_children, mappings_children,
                        is_merged, merged_from_ids,
                        no_update,
                        dynamic_attrs_children,
                        full_meme_data
                       )

        # Default return if no relevant trigger
        return no_update, False, *([no_update]*11), None

    # Callback to show/hide the merged_from dropdown
    @dash_app.callback(
        Output('merged-from-row', 'style'),
        Input('meme-is-merged', 'value')
    )
    def toggle_merged_from_visibility(is_merged_value):
        return {'display': 'flex'} if isinstance(is_merged_value, list) and 'IS_MERGED' in is_merged_value else {'display': 'none'}