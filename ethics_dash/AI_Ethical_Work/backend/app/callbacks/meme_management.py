import base64
import io
import json
import requests # Need to add to requirements.txt
import logging # Import logging
from dash import html, dcc, callback, Output, Input, State, ctx
import dash_bootstrap_components as dbc
from dash.exceptions import PreventUpdate
from flask import current_app # Import current_app for logging

# TODO: Get API URL dynamically?
API_BASE_URL = "http://localhost:5000/api/memes" 

MAX_UPLOAD_SIZE_MB = 10
MAX_UPLOAD_SIZE_BYTES = MAX_UPLOAD_SIZE_MB * 1024 * 1024
ALLOWED_EXTENSIONS = {'.json'}

def format_upload_results(results):
    """Formats the JSON response from the upload API into Markdown."""
    if not isinstance(results, dict):
        return "```\nError: Invalid response format received from server.\n```"

    output_lines = []
    
    # Main message
    output_lines.append(f"**{results.get('message', 'No summary message provided.')}**")
    output_lines.append("--- ")
    
    # LLM Feedback
    llm_feedback = results.get('llm_feedback')
    if llm_feedback and llm_feedback != "LLM review was not requested.":
        output_lines.append("**LLM Review Feedback:**")
        output_lines.append(f"```\n{llm_feedback}\n```")
        output_lines.append("--- ")
        
    # Validation Errors
    errors = results.get('validation_errors', [])
    if errors:
        output_lines.append("**Validation Errors (Records Skipped):**")
        for error in errors:
            record_id = f"Record Index {error.get('record_index', '?')} (Name: '{error.get('record_name', 'N/A')}')"
            error_details = json.dumps(error.get('errors', 'Unknown error'), indent=2)
            output_lines.append(f"*   {record_id}:\n    ```json\n    {error_details}\n    ```")
    
    # Combine lines
    return "\n".join(output_lines)
    
def register_meme_management_callbacks(app):
    """Registers callbacks related to meme creation, editing, and upload."""
    
    @app.callback(
        Output('mass-upload-output', 'children'),
        Input('mass-upload-component', 'contents'),
        State('mass-upload-component', 'filename'),
        State('mass-upload-llm-toggle', 'value'), # Get the state of the checklist
        prevent_initial_call=True
    )
    def handle_mass_upload(list_of_contents, list_of_names, llm_toggle_value):
        if list_of_contents is None:
            raise PreventUpdate

        # Assuming single file upload based on layout multiple=False
        content_string = list_of_contents
        filename = list_of_names
        
        # --- Basic File Validation --- 
        if not filename or not isinstance(filename, str):
            current_app.logger.warning("Upload attempt with no filename.")
            return "```\nError: No filename provided.\n```"
            
        file_ext = f".{filename.split('.')[-1].lower()}" if '.' in filename else None
        if file_ext not in ALLOWED_EXTENSIONS:
            current_app.logger.warning(f"Upload attempt with invalid file type: {filename}")
            return f"```\nError: Invalid file type. Only {', '.join(ALLOWED_EXTENSIONS)} files are allowed.\n```"

        # Decode the base64 string and check size
        decoded = None
        try:
            content_type, content_data = content_string.split(',')
            decoded_bytes = base64.b64decode(content_data)
            if len(decoded_bytes) > MAX_UPLOAD_SIZE_BYTES:
                current_app.logger.warning(f"Upload attempt failed: File '{filename}' exceeds size limit of {MAX_UPLOAD_SIZE_MB} MB.")
                return f"```\nError: File size exceeds the limit of {MAX_UPLOAD_SIZE_MB} MB.\n```"
            decoded = decoded_bytes # Store if valid
        except (ValueError, TypeError) as e:
             current_app.logger.error(f"Error decoding base64 content for file '{filename}': {e}", exc_info=True)
             return "```\nError: Could not decode file content. Ensure the file is properly encoded.\n```"
        except Exception as e: # Catch other potential decoding errors
            current_app.logger.error(f"Unexpected error during base64 decoding for file '{filename}': {e}", exc_info=True)
            return f"```\nError: An unexpected error occurred while reading the file content: {e}\n```"

        if decoded is None: # Should not happen if checks above are correct, but safety check
             return "```\nError: Failed to process file content after decoding.\n```"

        use_llm = 'USE_LLM' in llm_toggle_value if isinstance(llm_toggle_value, list) else False
        current_app.logger.info(f"Processing upload for file: '{filename}', Size: {len(decoded)} bytes, Use LLM: {use_llm}")
        
        # Prepare data for POST request
        files = {'file': (filename, io.BytesIO(decoded), content_type)}
        form_data = {'use_llm': str(use_llm).lower()}
        
        try:
            api_url = f"{API_BASE_URL}/upload"
            response = requests.post(api_url, files=files, data=form_data, timeout=300) # Increased timeout for LLM
            response.raise_for_status() # Raise an exception for bad status codes (4xx or 5xx)
            
            results = response.json()
            formatted_output = format_upload_results(results)
            return formatted_output
            
        except requests.exceptions.RequestException as e:
            return f"```\nError connecting to API: {e}\n```"
        except json.JSONDecodeError:
            return f"```\nError: Could not decode JSON response from API. Response text: {response.text}\n```"
        except Exception as e:
            return f"```\nAn unexpected error occurred: {e}\n```"
    
    # --- Add other meme management callbacks (save, clear, table selection, etc.) here eventually --- 
    
    # Example placeholder for save button (needs implementation)
    @app.callback(
        Output('alert-message', 'children'),
        Output('alert-message', 'is_open'),
        Output('alert-message', 'color'),
        # ... more outputs (like meme-update-trigger-store?)
        Input('save-meme-button', 'n_clicks'),
        # ... states for all form inputs ... 
        prevent_initial_call=True
    )
    def save_meme_callback(n_clicks):
         if n_clicks is None or n_clicks < 1:
             raise PreventUpdate
         # TODO: Implement save logic (collect data, validate, call API)
         # For now, just show a message
         return "Save functionality not yet fully implemented.", True, "info" 