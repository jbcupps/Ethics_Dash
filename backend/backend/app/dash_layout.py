"""
Defines the layout for the Dash application.
"""
from dash import html, dcc, dash_table
import dash_bootstrap_components as dbc
import dash_cytoscape as cyto # Import cytoscape

def create_layout():
    """Creates the Dash application layout."""
    return dbc.Container([
        dcc.Store(id='meme-update-trigger-store'), # Triggers dropdown/table updates
        dcc.Interval(id='meme-initial-load', interval=1000, n_intervals=0, max_intervals=1), # Load memes once on startup
        dcc.Store(id='edit-meme-store', storage_type='memory'), # Holds data for meme being edited
        html.H1("Ethical Memes Dashboard"),
        dbc.Alert(id='alert-message', color='warning', is_open=False), # For notifications
        dbc.Tabs([
            dbc.Tab(label="Meme Management", children=[
                dbc.Accordion([
                    dbc.AccordionItem(title="Add/Edit Ethical Meme", children=[
                        dbc.Input(id='meme-id-store', type='hidden'), # To store ID when editing
                        dbc.Row([
                            dbc.Col(dbc.Label("Meme Name:"), width=2),
                            dbc.Col(dcc.Input(id='meme-name', type='text', placeholder="Enter meme name", required=True), width=10)
                        ]),
                        dbc.Row([
                            dbc.Col(dbc.Label("Description:"), width=2),
                            dbc.Col(dcc.Textarea(id='meme-description', placeholder="Enter meme description", style={'width': '100%'}), width=10)
                        ]),
                        dbc.Row([
                             dbc.Col(dbc.Label("Ethical Dimensions:"), width=2),
                             dbc.Col(
                                 # Incorporating the checklist from the old app.py
                                 dcc.Checklist(
                                     id='meme-ethical-dimension',
                                     options=[
                                         {'label': 'Deontology', 'value': 'Deontology'},
                                         {'label': 'Teleology', 'value': 'Teleology'},
                                         {'label': 'Areteology', 'value': 'Areteology'},
                                         {'label': 'Opt-Out', 'value': 'Opt-Out'}
                                     ],
                                     value=[],
                                     labelStyle={'display': 'block'}
                                 ), width=10)
                        ]),
                        # Placeholder for dynamically generated dimension attributes
                        dbc.Row([
                            dbc.Col(width=2),
                            dbc.Col(html.Div(id='dynamic-meme-attribute-inputs'), width=10)
                        ]),
                        dbc.Row([
                            dbc.Col(dbc.Label("Tags (comma-sep):"), width=2),
                            dbc.Col(dcc.Input(id='meme-tags', type='text', placeholder="e.g., fairness, privacy"), width=10)
                        ]),
                        # Add Merged Token Section
                        html.Hr(),
                        html.H5("Merged Token Status"),
                        dbc.Row([
                            dbc.Col(width=2),
                            dbc.Col(
                                dcc.Checklist(
                                    id='meme-is-merged',
                                    options=[{'label': 'This meme is a merged token', 'value': 'IS_MERGED'}],
                                    value=[] # Default to not checked
                                ), width=10)
                        ]),
                        dbc.Row([
                            dbc.Col(dbc.Label("Merged From Tokens:"), width=2),
                            # This dropdown needs dynamic options and multi-select enabled
                            dbc.Col(dcc.Dropdown(id='meme-merged-from', multi=True, placeholder="Select source tokens..."), width=10)
                        ], id='merged-from-row', style={'display': 'none'}), # Initially hidden
                        # End Merged Token Section

                        # Dynamic Morphisms Section
                        html.Hr(),
                        html.H5("Define Relationships (Morphisms)"),
                        html.Div(id='morphisms-container', children=[]), # Container for dynamic inputs
                        dbc.Button("Add Morphism", id="add-morphism-button", color="secondary", size="sm", className="mt-2", n_clicks=0),
                        
                        # Dynamic Mappings Section
                        html.Hr(),
                        html.H5("Define Cross-Category Mappings"),
                        html.Div(id='mappings-container', children=[]), # Container for dynamic inputs
                        dbc.Button("Add Mapping", id="add-mapping-button", color="secondary", size="sm", className="mt-2", n_clicks=0),
                        
                        html.Hr(),
                        # Add Clear button next to Save button
                        dbc.Row([
                            dbc.Col(dbc.Button("Save Meme", id="save-meme-button", color="primary", n_clicks=0), width="auto"),
                            dbc.Col(dbc.Button("Clear Form / New Meme", id="clear-form-button", color="warning", outline=True, n_clicks=0), width="auto")
                        ], className="mt-3")
                    ]), # End AccordionItem: Add/Edit
                    # --- NEW: Accordion Item for Mass Upload ---
                    dbc.AccordionItem(title="Mass Import Memes via File Upload", children=[
                        dcc.Upload(
                            id='mass-upload-component',
                            children=html.Div([
                                'Drag and Drop or ',
                                html.A('Select Files')
                            ]),
                            style={
                                'width': '100%',
                                'height': '60px',
                                'lineHeight': '60px',
                                'borderWidth': '1px',
                                'borderStyle': 'dashed',
                                'borderRadius': '5px',
                                'textAlign': 'center',
                                'margin': '10px'
                            },
                            # Allow multiple files to be uploaded
                            multiple=False, # Set to True if you want to allow multiple files at once
                            accept='.csv,.json' # Specify accepted file types
                        ),
                        dbc.Checklist(
                            options=[
                                {"label": "Use LLM to review and format uploaded data (experimental)", "value": "USE_LLM"},
                            ],
                            value=[], # Default to not using LLM
                            id="mass-upload-llm-toggle",
                            inline=True,
                            switch=True,
                        ),
                        dbc.Spinner(dcc.Markdown(id='mass-upload-output', children="Upload status will appear here."))
                    ]) # End AccordionItem: Mass Upload
                ]), # End Accordion
                html.Hr(),
                html.H4("Existing Memes"),
                dbc.Spinner(
                    dash_table.DataTable(
                        id='meme-database-table',
                        columns=[
                            # Define columns - adjust based on desired display
                            {"name": "Name", "id": "name"},
                            {"name": "Description", "id": "description", "type": "text", "presentation": "markdown"},
                            {"name": "Dimensions", "id": "ethical_dimension_str"}, # We'll create this string in the callback
                            {"name": "Tags", "id": "tags_str"}, # We'll create this string in the callback
                            {"name": "Merged", "id": "is_merged_token"},
                            {"name": "ID", "id": "_id", "hidden": True} # Hide ID but keep for selection
                        ],
                        data=[], # Initially empty, populated by callback
                        row_selectable='single', # Allow selecting one row for editing
                        selected_rows=[],
                        page_size=10,
                        style_cell={'textAlign': 'left', 'padding': '5px', 'whiteSpace': 'normal', 'height': 'auto'},
                        style_header={'fontWeight': 'bold'},
                        style_data={'border': '1px solid grey'},
                        style_table={'overflowX': 'auto'},
                        markdown_options={"html": True} # Allow HTML in markdown for descriptions if needed
                    )
                ) # End Spinner
            ]),
            dbc.Tab(label="Ethical Analysis (R2)", children=[
                 html.H4("Perform Analysis"),
                 # Add components for selecting P1, R1, and triggering analysis
                 dbc.Row([
                     dbc.Col(dbc.Label("Primary Meme (P1):"), width=2),
                     dbc.Col(dcc.Dropdown(id='analysis-p1-dropdown'), width=10), # Needs dynamic options
                 ]),
                 dbc.Row([
                     dbc.Col(dbc.Label("Response Meme (R1):"), width=2),
                     dbc.Col(dcc.Dropdown(id='analysis-r1-dropdown'), width=10), # Needs dynamic options
                 ]),
                 dbc.Button("Run Analysis", id="run-analysis-button", color="success", n_clicks=0),
                 html.Hr(),
                 dbc.Spinner(dcc.Markdown(id='analysis-results-output', children="Analysis results will appear here."))
            ]),
             dbc.Tab(label="Ontology", children=[
                 html.H4("Ethical Ontology"),
                 dbc.Spinner(dcc.Markdown(id='ontology-display')) # Load ontology.md here
             ]),
             # New Tab for Visualization
             dbc.Tab(label="Meme Network", children=[
                 html.H4("Ethical Meme Relationship Graph"),
                 dbc.Alert("Click nodes/edges for details (Not Implemented Yet)", color="info"),
                 cyto.Cytoscape(
                    id='meme-cytoscape-graph',
                    layout={'name': 'cose', 'animate': True}, # cose layout is good for networks
                    style={'width': '100%', 'height': '600px'},
                    elements=[], # Nodes and edges populated by callback
                    # Define basic styling
                    stylesheet=[
                        {
                            'selector': 'node',
                            'style': {
                                'label': 'data(label)', # Use the 'label' data property
                                'background-color': '#007bff', # Default blue
                                'color': 'white',
                                'text-outline-color': '#007bff',
                                'text-outline-width': 2
                            }
                        },
                         {
                            'selector': 'edge',
                            'style': {
                                'line-color': '#6c757d',
                                'target-arrow-color': '#6c757d',
                                'target-arrow-shape': 'triangle',
                                'curve-style': 'bezier',
                                'label': 'data(label)', # Show edge type
                                'font-size': '10px',
                                'color': '#6c757d'
                            }
                        }
                    ]
                )
             ])
        ])
    ], fluid=True) # Use fluid container for full width 