import base64
import io
import json
import requests
import logging
from dash.exceptions import PreventUpdate
from dash.dependencies import Input, Output, State
import os

logger = logging.getLogger(__name__)

# Config
# Fix API URL construction - need to handle both internal Docker networking and local routes
_base_api_url = os.getenv("BACKEND_API_URL", "/api")
# Remove any trailing slash
_base_api_url = _base_api_url.rstrip("/")
# If given as a relative path (starts with '/'), convert to absolute URL pointing to Flask inside container
if not _base_api_url.startswith("http"):
    _base_api_url = f"http://localhost:5000{_base_api_url}"
# Assemble full endpoint URL for memes
BACKEND_API_URL = f"{_base_api_url}/memes"

logger.info(f"Meme management callbacks configured to use API URL: {BACKEND_API_URL}")

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
    
def register_meme_mgmt_callbacks(dash_app):
    """Registers callbacks related to meme management interactions."""
    
    @dash_app.callback(
        Output('mass-upload-output', 'children'),
        Input('mass-upload-component', 'contents'),
        State('mass-upload-component', 'filename'),
        State('mass-upload-component', 'last_modified'),
        State('mass-upload-llm-toggle', 'value'),
        prevent_initial_call=True
    )
    def process_mass_upload(contents, filename, last_modified, llm_toggle):
        """Handles mass upload of memes from a file."""
        if not contents:
            return no_update
        
        content_type, content_string = contents.split(',')
        decoded = dash.no_update

        try:
            use_llm = llm_toggle and 'USE_LLM' in llm_toggle
            logger.info(f"Processing mass upload of file: {filename} (Use LLM: {use_llm})")
            
            if 'json' in filename.lower():
                import base64
                import io
                decoded = base64.b64decode(content_string).decode('utf-8')
                memes_data = json.loads(decoded)
                
                # Simple validation
                if not isinstance(memes_data, list):
                    if isinstance(memes_data, dict):
                        # Try to handle single meme case by wrapping in list
                        memes_data = [memes_data]
                    else:
                        return "Error: JSON data must be an array of meme objects or a single meme object."
                
                # Count memes with the minimum required fields
                valid_memes = [m for m in memes_data if 'name' in m and 'description' in m]
                if not valid_memes:
                    return "Error: No valid meme objects found. Each meme must have at least 'name' and 'description' fields."
                
                # Prepare the payload for backend - wrapping it so the backend knows if LLM processing is requested
                upload_payload = {
                    "memes": memes_data,
                    "use_llm_processing": use_llm
                }
                
                try:
                    # Send to the batch endpoint on the backend
                    url = f"{BACKEND_API_URL}/batch"
                    logger.info(f"Sending batch upload to: {url}")
                    
                    headers = {'Content-Type': 'application/json'}
                    response = requests.post(
                        url,
                        json=upload_payload,  # Will auto-serialize the JSON
                        headers=headers,
                        timeout=30  # Longer timeout for batch/LLM operations
                    )
                    
                    if response.ok:
                        result = response.json()
                        inserted_count = result.get('inserted', 0)
                        updated_count = result.get('updated', 0)
                        errors = result.get('errors', [])
                        
                        status_text = f"Processed {len(memes_data)} meme(s): {inserted_count} inserted, {updated_count} updated."
                        if errors:
                            status_text += f"\n\nErrors ({len(errors)}):"
                            for e in errors[:10]:  # Limit to first 10 errors
                                status_text += f"\n- {e}"
                            if len(errors) > 10:
                                status_text += f"\n- (and {len(errors) - 10} more errors)"
                        
                        return status_text
                    else:
                        error_msg = "API Error"
                        try:
                            error_data = response.json()
                            if 'error' in error_data:
                                error_msg = error_data['error']
                        except:
                            error_msg = f"HTTP {response.status_code}: {response.text}"
                        
                        return f"Error uploading memes: {error_msg}"
                
                except requests.exceptions.RequestException as e:
                    logger.error(f"Network error during batch upload: {e}", exc_info=True)
                    return f"Network error: {str(e)}"
            
            elif 'csv' in filename.lower():
                return "CSV file format is not yet supported. Please use JSON."
            
            else:
                return f"Unsupported file format: {filename}. Only JSON and CSV are supported."
        
        except Exception as e:
            logger.error(f"Error processing upload file {filename}: {e}", exc_info=True)
            return f"Error processing file: {str(e)}"
        
        return no_update
    
    # --- Add other meme management callbacks (save, clear, table selection, etc.) here eventually --- 
    
    # Removed placeholder save_meme_callback as it's implemented in form_callbacks.py
    # @app.callback(
    #     Output('alert-message', 'children'),
    #     Output('alert-message', 'is_open'),
    #     Output('alert-message', 'color'),
    #     # ... more outputs (like meme-update-trigger-store?)
    #     Input('save-meme-button', 'n_clicks'),
    #     # ... states for all form inputs ... 
    #     prevent_initial_call=True
    # )
    # def save_meme_callback(n_clicks):
    #      if n_clicks is None or n_clicks < 1:
    #          raise PreventUpdate
    #      # TODO: Implement save logic (collect data, validate, call API)
    #      # For now, just show a message
    #      return "Save functionality not yet fully implemented.", True, "info" 