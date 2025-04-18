import dash
import dash_bootstrap_components as dbc
from dash import html, dcc, Input, Output, State, callback
import requests # To call backend API
import json     # To handle JSON data
import os       # To read backend URL from env
from flask import Flask, send_from_directory # Import Flask and send_from_directory
from dash import dash_table  # for rendering existing memes table

# Initialize Flask server explicitly for route handling
server = Flask(__name__, static_folder='static') # Define static folder explicitly

# Initialize the Dash app, linking it to the Flask server
# Set assets_folder to the 'assets' directory relative to app.py
# Set requests_pathname_prefix to avoid conflicts with Flask routes if needed
# Use the Flask server instance
app = dash.Dash(
    __name__,
    server=server, # Use the explicit Flask server
    external_stylesheets=[dbc.themes.BOOTSTRAP],
    suppress_callback_exceptions=True,
    assets_folder='assets',
    requests_pathname_prefix='/dash/',
)

# Path for the React build artifacts
REACT_BUILD_DIR = os.path.join(server.static_folder, 'react')

# Serve React App
@server.route('/react_app')
@server.route('/react_app/<path:path>')
def serve_react(path=None):
    if path is None or path == "":
        # Serve index.html for the root route of the React app
        return send_from_directory(REACT_BUILD_DIR, 'index.html')
    elif os.path.exists(os.path.join(REACT_BUILD_DIR, path)):
        # Serve static files like JS, CSS, images
        return send_from_directory(REACT_BUILD_DIR, path)
    else:
        # Handle client-side routing: serve index.html for unknown paths
        return send_from_directory(REACT_BUILD_DIR, 'index.html')

# Serve React static assets (ensure paths match those in index.html)
@server.route('/static/<path:path>')
def serve_react_static(path):
    return send_from_directory(os.path.join(REACT_BUILD_DIR, 'static'), path)

# --- Configuration --- 
# Get backend API URL from environment variable or use a default
# Important: This URL needs to be accessible *from the machine running the Dash app*.
# If running Dash locally (not in Docker) and backend is in Docker, use localhost mapping.
# If both are in Docker on same network, use service name.
# Ensure this matches the service name in your docker-compose.yml if applicable
BACKEND_API_URL = os.getenv("BACKEND_API_URL", "http://ai-backend:5000/api") 

# --- Helper Function for API Calls ---
def make_api_request(method, endpoint, data=None):
    url = f"{BACKEND_API_URL}{endpoint}"
    try:
        if method.upper() == 'POST':
            response = requests.post(url, json=data, timeout=10)
        elif method.upper() == 'GET':
            response = requests.get(url, timeout=10)
        else:
            return {"error": f"Unsupported method: {method}"}, 500
        
        response.raise_for_status() # Raise exception for bad status codes (4xx or 5xx)
        
        if response.status_code == 204: # No Content (e.g., successful DELETE)
             return {}, response.status_code
        
        # Try to decode JSON, return raw text if it fails
        try:
            return response.json(), response.status_code
        except json.JSONDecodeError:
            return {"raw_response": response.text}, response.status_code
            
    except requests.exceptions.RequestException as e:
        return {"error": f"API request failed: {e}"}, 503 # Service Unavailable or connection error
    except Exception as e:
        return {"error": f"An unexpected error occurred: {e}"}, 500

# --- Reusable Form Group Component ---
def form_group(label_text, component):
    return dbc.Row(
        [
            dbc.Label(label_text, html_for=component.id, width=2),
            dbc.Col(component, width=10),
        ],
        className="mb-3",
    )

# --- Layout Definition ---
app.layout = dbc.Container([
    dcc.Location(id='url', refresh=False),
    # Auto-load memes once at startup
    dcc.Interval(id='init-load-memes', interval=1, n_intervals=0, max_intervals=1),
    html.H1("Ethics Dash - Integrated"), # Updated Title
    html.Hr(),
    
    dbc.Tabs([
        dbc.Tab(label="Analysis Tool", tab_id="tab-analysis", children=[
            # Use an Iframe to embed the React app served from /react_app
            html.Iframe(
                src="/react_app",
                style={"width": "100%", "height": "80vh", "border": "none"}
            )
        ]),
        dbc.Tab(label="Database Management", tab_id="tab-db-mgmt", children=[
            html.H3("Ethical Meme Management"),
            html.Hr(),
            
            # --- Section 1: Populate Database ---
            dbc.Card([
                dbc.CardHeader("Populate with Predefined Memes"),
                dbc.CardBody([
                    html.P("Click the button to clear the existing collection and insert the predefined set of foundational ethical memes.", className="card-text"),
                    html.P("WARNING: This will delete all current memes in the database!", className="text-danger fw-bold"),
                    dbc.Button("Populate Database", id="btn-populate-db", color="danger", className="me-2"),
                    dbc.Spinner(html.Div(id="populate-status")) # Show status/spinner here
                ])
            ], className="mb-4"),
            
            # --- Section 2: Add New Meme Wizard ---
            dbc.Card([
                dbc.CardHeader("Add New Ethical Meme"),
                dbc.CardBody([
                    dbc.Accordion([
                        dbc.AccordionItem([
                             form_group("Name:", dcc.Input(id="meme-name", type="text", placeholder="Enter meme name", required=True)),
                             form_group("Description:", dcc.Textarea(id="meme-description", placeholder="Enter concise definition...", style={'height': 100}, required=True)),
                             form_group("Source Concept:", dcc.Input(id="meme-source-concept", type="text", placeholder="e.g., Duty, Virtue, Net Benefit")),     
                             form_group("Ethical Dimension(s):", dcc.Checklist(
                                 options=[
                                     {'label': 'Deontology', 'value': 'Deontology'},
                                     {'label': 'Teleology', 'value': 'Teleology'},
                                     {'label': 'Areteology', 'value': 'Areteology'},
                                     {'label': 'Memetics', 'value': 'Memetics'}
                                 ],
                                 value=[],
                                 id="meme-ethical-dimension",
                                 inline=True,
                                 inputStyle={"margin-right": "5px"},
                                 labelStyle={"margin-right": "20px"}
                             )),
                             form_group("Keywords:", dcc.Input(id="meme-keywords", type="text", placeholder="Comma-separated keywords (e.g., kant, duty, rule)")),
                             form_group("Variations:", dcc.Textarea(id="meme-variations", placeholder="Common phrasings or related sayings (one per line)...", style={'height': 80})),
                             form_group("Examples:", dcc.Textarea(id="meme-examples", placeholder="Brief scenarios illustrating the meme (one per line)...", style={'height': 80})),
                             form_group("Related Memes:", dcc.Input(id="meme-related-memes", type="text", placeholder="Comma-separated names of related memes")),
                        ], title="Core Information"),
                        
                        dbc.AccordionItem([
                            html.Div(id="dimension-specific-inputs") # Content generated by callback
                        ], title="Dimension-Specific Attributes"),
                        
                        dbc.AccordionItem([
                             form_group("Est. Transmissibility:", dcc.Dropdown(id="meme-memetic-transmissibility", options=['High', 'Medium', 'Low'], placeholder="Select...")),
                             form_group("Est. Persistence:", dcc.Dropdown(id="meme-memetic-persistence", options=['High', 'Medium', 'Low'], placeholder="Select...")),
                             form_group("Est. Adaptability:", dcc.Dropdown(id="meme-memetic-adaptability", options=['High', 'Medium', 'Low'], placeholder="Select...")),
                             form_group("Fidelity Level:", dcc.Dropdown(id="meme-memetic-fidelity", options=['High', 'Medium', 'Low'], placeholder="Select...")),
                             form_group("Transmission Pathways:", dcc.Input(id="meme-memetic-pathways", type="text", placeholder="Comma-separated (e.g., Law, Parenting)")),
                             form_group("Selection Pressures:", dcc.Input(id="meme-memetic-pressures", type="text", placeholder="Comma-separated (e.g., Social Order, Trust)")),
                        ], title="Memetic Attributes"),
                    ], start_collapsed=True, always_open=True, className="mb-3"),
                    
                    dbc.Button("Save New Meme", id="btn-save-meme", color="primary", className="me-2"),
                    dbc.Spinner(html.Div(id="save-meme-status"))
                ])
            ]),
            # Section 3: Display existing memes
            dbc.Card([
                dbc.CardHeader("Existing Memes"),
                dbc.CardBody([
                    dbc.Button("Refresh List", id="btn-refresh-memes", color="secondary", className="me-2"),
                    html.Div(id="existing-memes-container")
                ])
            ], className="mt-4")
        ])
    ])
], fluid=True)

# --- Callbacks ---

# Callback to handle Populate Database button
@callback(
    Output("populate-status", "children"),
    Input("btn-populate-db", "n_clicks"),
    prevent_initial_call=True
)
def handle_populate_db(n_clicks):
    if n_clicks is None or n_clicks < 1:
        return ""
    
    result, status_code = make_api_request('POST', '/memes/populate')
    
    if status_code == 200:
        msg = result.get("message", "Population successful.")
        deleted = result.get("deleted_count", "N/A")
        inserted = result.get("inserted_count", "N/A")
        alert_color = "success"
        alert_text = f"{msg} (Deleted: {deleted}, Inserted: {inserted})"
    else:
        alert_color = "danger"
        alert_text = f"Error ({status_code}): {result.get('error', 'Unknown error during population')}"
        
    return dbc.Alert(alert_text, color=alert_color, dismissable=True, duration=5000)

# Callback to dynamically generate dimension-specific inputs
@callback(
    Output("dimension-specific-inputs", "children"),
    Input("meme-ethical-dimension", "value") 
)
def update_dimension_inputs(selected_dimensions):
    children = []
    if not selected_dimensions:
        return html.P("Select an Ethical Dimension above to see specific attributes.", className="text-muted")
        
    if "Deontology" in selected_dimensions:
        children.append(html.H5("Deontology Attributes"))
        children.append(form_group("Rule-Based?", dcc.Dropdown(id='deon-is-rule-based', options=[{'label': 'Yes', 'value': True}, {'label': 'No', 'value': False}], value=True)))
        children.append(form_group("Universalizability Test:", dcc.Dropdown(id='deon-universalizability', options=['Applicable', 'Not Applicable', 'Contradictory', 'Contextual'], placeholder="Select...")))
        children.append(form_group("Respects Rational Agents?", dcc.Dropdown(id='deon-respects-agents', options=[{'label': 'Yes', 'value': True}, {'label': 'No', 'value': False}, {'label': 'Contextual', 'value': 'Contextual'}], placeholder="Select...")))
        children.append(form_group("Focus on Intent?", dcc.Dropdown(id='deon-focus-intent', options=[{'label': 'Yes', 'value': True}, {'label': 'No', 'value': False}, {'label': 'Contextual', 'value': 'Contextual'}], placeholder="Select...")))
        children.append(html.Hr())
        
    if "Teleology" in selected_dimensions:
        children.append(html.H5("Teleology Attributes"))
        children.append(form_group("Focus:", dcc.Dropdown(id='teleo-focus', options=['Outcomes', 'Rules (Rule Util.)'], value='Outcomes')))
        children.append(form_group("Utility Metric:", dcc.Input(id='teleo-utility-metric', type="text", placeholder="e.g., Happiness, Welfare, Preference Satisfaction")))
        children.append(form_group("Scope:", dcc.Input(id='teleo-scope', type="text", placeholder="e.g., All Affected Beings, Group, Individual")))
        children.append(form_group("Time Horizon:", dcc.Input(id='teleo-time-horizon', type="text", placeholder="e.g., Long-term, Short-term, Contextual")))
        children.append(html.Hr())
        
    if "Areteology" in selected_dimensions:
        children.append(html.H5("Areteology Attributes"))
        children.append(form_group("Related Virtues:", dcc.Input(id='areteology-related-virtues', type="text", placeholder="Comma-separated virtue names")))
        children.append(form_group("Related Vices:", dcc.Input(id='areteology-related-vices', type="text", placeholder="Comma-separated vice names")))
        children.append(form_group("Role of Phronesis:", dcc.Dropdown(id='areteology-role-phronesis', options=['Essential', 'Important', 'Relevant', 'Not Applicable'], placeholder="Select...")))
        children.append(form_group("Contributes to Eudaimonia?", dcc.Dropdown(id='areteology-contributes-eudaimonia', options=[{'label': 'Yes', 'value': True}, {'label': 'No', 'value': False}, {'label': 'Indirectly', 'value': 'Indirectly'}], placeholder="Select...")))
        children.append(html.Hr())
        
    return children

# Callback to handle Save New Meme button
@callback(
    Output("save-meme-status", "children"),
    Input("btn-save-meme", "n_clicks"),
    State("meme-name", "value"),
    State("meme-description", "value"),
    State("meme-source-concept", "value"),
    State("meme-ethical-dimension", "value"),
    State("meme-keywords", "value"),
    State("meme-variations", "value"),
    State("meme-examples", "value"),
    State("meme-related-memes", "value"),
    # Memetics States
    State("meme-memetic-transmissibility", "value"),
    State("meme-memetic-persistence", "value"),
    State("meme-memetic-adaptability", "value"),
    State("meme-memetic-fidelity", "value"),
    State("meme-memetic-pathways", "value"),
    State("meme-memetic-pressures", "value"),
    # Deontology States (check if they exist in layout before accessing)
    State("deon-is-rule-based", "value"),
    State("deon-universalizability", "value"),
    State("deon-respects-agents", "value"),
    State("deon-focus-intent", "value"),
    # Teleology States
    State("teleo-focus", "value"),
    State("teleo-utility-metric", "value"),
    State("teleo-scope", "value"),
    State("teleo-time-horizon", "value"),
    # Areteology States
    State("areteology-related-virtues", "value"),
    State("areteology-related-vices", "value"),
    State("areteology-role-phronesis", "value"),
    State("areteology-contributes-eudaimonia", "value"),
    prevent_initial_call=True
)
def handle_save_meme(
    n_clicks,
    name, description, source_concept, ethical_dimension,
    keywords_str, variations_str, examples_str, related_memes_str,
    mem_trans, mem_persist, mem_adapt, mem_fidelity, mem_paths_str, mem_press_str,
    deon_rule, deon_univ, deon_respect, deon_intent,
    teleo_focus, teleo_metric, teleo_scope, teleo_horizon,
    areteology_virtues, areteology_vices, areteology_phronesis, areteology_eudaimonia
):
    if n_clicks is None or n_clicks < 1:
        return ""
        
    # Basic validation (more robust validation should happen in backend via Pydantic)
    if not name or not description or not ethical_dimension:
        return dbc.Alert("Name, Description, and Ethical Dimension are required.", color="warning", dismissable=True)

    # Helper to split comma-separated strings or newline strings into lists
    def split_str(s, separator=','):
        if not s: return []
        return [item.strip() for item in s.split(separator) if item.strip()]
    def split_textarea(s):
        if not s: return []
        return [item.strip() for item in s.splitlines() if item.strip()]

    # Construct the payload dictionary matching EthicalMemeCreate model structure
    payload = {
        "name": name,
        "description": description,
        "ethical_dimension": ethical_dimension,
        "source_concept": source_concept,
        "keywords": split_str(keywords_str),
        "variations": split_textarea(variations_str),
        "examples": split_textarea(examples_str),
        "related_memes": split_str(related_memes_str),
        "dimension_specific_attributes": {},
    }
    
    # Add memetics attributes if provided
    memetics_attrs = {}
    if mem_trans: memetics_attrs["estimated_transmissibility"] = mem_trans
    if mem_persist: memetics_attrs["estimated_persistence"] = mem_persist
    if mem_adapt: memetics_attrs["estimated_adaptability"] = mem_adapt
    if mem_fidelity: memetics_attrs["fidelity_level"] = mem_fidelity
    if mem_paths_str: memetics_attrs["common_transmission_pathways"] = split_str(mem_paths_str)
    if mem_press_str: memetics_attrs["relevant_selection_pressures"] = split_str(mem_press_str)
    if memetics_attrs: # Only add if there's at least one attribute
         payload["dimension_specific_attributes"]["memetics"] = memetics_attrs
         
    # Add dimension-specific attributes based on selected dimensions
    if "Deontology" in ethical_dimension:
        deon_attrs = {}
        if deon_rule is not None: deon_attrs["is_rule_based"] = deon_rule
        if deon_univ: deon_attrs["universalizability_test"] = deon_univ
        if deon_respect is not None: deon_attrs["respects_rational_agents"] = deon_respect
        if deon_intent is not None: deon_attrs["focus_on_intent"] = deon_intent
        if deon_attrs: payload["dimension_specific_attributes"]["deontology"] = deon_attrs
            
    if "Teleology" in ethical_dimension:
        teleo_attrs = {}
        if teleo_focus: teleo_attrs["focus"] = teleo_focus
        if teleo_metric: teleo_attrs["utility_metric"] = teleo_metric
        if teleo_scope: teleo_attrs["scope"] = teleo_scope
        if teleo_horizon: teleo_attrs["time_horizon"] = teleo_horizon
        if teleo_attrs: payload["dimension_specific_attributes"]["teleology"] = teleo_attrs
        
    if "Areteology" in ethical_dimension:
        areteology_attrs = {}
        if areteology_virtues: areteology_attrs["related_virtues"] = split_str(areteology_virtues)
        if areteology_vices: areteology_attrs["related_vices"] = split_str(areteology_vices)
        if areteology_phronesis: areteology_attrs["role_of_phronesis"] = areteology_phronesis
        if areteology_eudaimonia is not None: areteology_attrs["contributes_to_eudaimonia"] = areteology_eudaimonia
        if areteology_attrs: payload["dimension_specific_attributes"]["areteology"] = areteology_attrs

    # Make the API call
    result, status_code = make_api_request('POST', '/memes/', data=payload)
    
    if status_code == 201:
        alert_color = "success"
        meme_name = result.get("name", "New meme")
        alert_text = f"Successfully created meme: '{meme_name}' (ID: {result.get('_id')})"
        # Potentially clear the form here
    elif status_code == 422:
        alert_color = "warning"
        error_details = result.get("details", "Unknown validation error")
        alert_text = f"Validation Error: {result.get('error')}. Details: {json.dumps(error_details)}"
    else:
        alert_color = "danger"
        alert_text = f"Error ({status_code}): {result.get('error', 'Unknown error saving meme')}"
        
    return dbc.Alert(alert_text, color=alert_color, dismissable=True, duration=8000)

# --- Callback to refresh existing memes table ---
@callback(
    Output("existing-memes-container", "children"),
    Input("btn-refresh-memes", "n_clicks"),
    Input("init-load-memes", "n_intervals")  # auto trigger once
)
def refresh_existing_memes(n_clicks, n_intervals):
    result, status_code = make_api_request("GET", "/memes/")
    if status_code != 200:
        return dbc.Alert(f"API error {status_code}: {result}",
                         color="danger")
    if not result:           # empty list
        return dbc.Alert("No memes returned (check DB or BACKEND_API_URL)",
                         color="warning")
    else:
        columns = [
            {"name": "Name", "id": "name"},
            {"name": "Description", "id": "description"},
            {"name": "Dimensions", "id": "ethical_dimension"},
            {"name": "Tags", "id": "keywords"},
            {"name": "Merged", "id": "is_merged_token"},
            {"name": "ID", "id": "_id"},
        ]
        data = [
            {
                "name": m.get("name", ""),
                "description": m.get("description", ""),
                "ethical_dimension": ", ".join(m.get("ethical_dimension", [])),
                "keywords": ", ".join(m.get("keywords", [])),
                "is_merged_token": m.get("is_merged_token", False),
                "_id": m.get("_id", ""),
            }
            for m in result
        ]
        table = dash_table.DataTable(
            columns=columns,
            data=data,
            page_size=10,
            style_table={"overflowX": "auto"},
            style_cell={"textAlign": "left", "whiteSpace": "normal"}
        )
        return table

# --- Run the App ---
if __name__ == '__main__':
    # Use the Flask server's run method for development
    # Use debug=True only for development, remove for production
    # Use host='0.0.0.0' to be accessible externally (within Docker)
    server.run(host='0.0.0.0', port=8050, debug=False)
