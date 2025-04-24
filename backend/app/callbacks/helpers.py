import dash_bootstrap_components as dbc
from dash import dcc, html

# --- Helper Functions for Dynamic Inputs ---
def create_morphism_inputs(index, meme_options=None):
    """Creates a set of input fields for a morphism relationship."""
    if meme_options is None:
        meme_options = []
        
    # Create a card-style container with a border, padding, and margin
    return html.Div(
        id={'type': 'morphism-card', 'index': index},
        children=[
            # Header with Remove button
            html.Div(
                className="d-flex justify-content-between align-items-center",
                children=[
                    html.H6(f"Morphism {index + 1}", className="mb-0"),
                    html.Button(
                        "×", # × character for close
                        id={'type': 'remove-morphism-button', 'index': index},
                        className="btn btn-sm btn-outline-danger",
                        n_clicks=0,
                        # Add client-side JavaScript for immediate click response
                        **{
                            'data-index': index,
                            'onClick': """
                            var el = document.getElementById('remove-morphism-' + this.dataset.index);
                            if(el && el.parentNode) {
                                el.parentNode.removeChild(el);
                            }
                            """
                        }
                    )
                ]
            ),
            # Input fields
            html.Div(
                className="row mt-2",
                children=[
                    # Type Dropdown
                    html.Div(
                        className="col-md-4",
                        children=[
                            html.Label("Morphism Type:", className="form-label"),
                            dcc.Dropdown(
                                id={'type': 'morphism-type', 'index': index},
                                options=[
                                    {'label': 'Specialization', 'value': 'specialization'},
                                    {'label': 'Generalization', 'value': 'generalization'},
                                    {'label': 'Implementation', 'value': 'implementation'},
                                    {'label': 'Opposing', 'value': 'opposing'},
                                    {'label': 'Complementary', 'value': 'complementary'},
                                    {'label': 'Derived', 'value': 'derived'}
                                ],
                                placeholder="Select type..."
                            )
                        ]
                    ),
                    # Target Meme Dropdown
                    html.Div(
                        className="col-md-4",
                        children=[
                            html.Label("Target Meme:", className="form-label"),
                            dcc.Dropdown(
                                id={'type': 'morphism-target', 'index': index},
                                options=meme_options,
                                placeholder="Select target meme..."
                            )
                        ]
                    ),
                    # Description Field
                    html.Div(
                        className="col-md-4",
                        children=[
                            html.Label("Description:", className="form-label"),
                            dcc.Input(
                                id={'type': 'morphism-desc', 'index': index},
                                type="text",
                                placeholder="Describe relationship...",
                                className="form-control"
                            )
                        ]
                    )
                ]
            )
        ],
        className="card p-3 mb-3",
        style={'border': '1px solid #ccc', 'borderRadius': '4px'}
    )

def create_mapping_inputs(index):
    """Creates a set of input fields for a cross-category mapping."""
    return html.Div(
        id={'type': 'mapping-card', 'index': index},
        children=[
            # Header with Remove button
            html.Div(
                className="d-flex justify-content-between align-items-center",
                children=[
                    html.H6(f"Mapping {index + 1}", className="mb-0"),
                    html.Button(
                        "×", # × character for close
                        id={'type': 'remove-mapping-button', 'index': index},
                        className="btn btn-sm btn-outline-danger",
                        n_clicks=0,
                        # Add client-side JavaScript for immediate click response
                        **{
                            'data-index': index,
                            'onClick': """
                            var el = document.getElementById('remove-mapping-' + this.dataset.index);
                            if(el && el.parentNode) {
                                el.parentNode.removeChild(el);
                            }
                            """
                        }
                    )
                ]
            ),
            # Input fields
            html.Div(
                className="row mt-2",
                children=[
                    # Concept Field
                    html.Div(
                        className="col-md-4",
                        children=[
                            html.Label("Target Concept:", className="form-label"),
                            dcc.Input(
                                id={'type': 'mapping-concept', 'index': index},
                                type="text",
                                placeholder="Enter concept...",
                                className="form-control"
                            )
                        ]
                    ),
                    # Category Dropdown
                    html.Div(
                        className="col-md-4",
                        children=[
                            html.Label("Target Category:", className="form-label"),
                            dcc.Dropdown(
                                id={'type': 'mapping-category', 'index': index},
                                options=[
                                    {'label': 'Mathematical', 'value': 'mathematical'},
                                    {'label': 'Biological', 'value': 'biological'},
                                    {'label': 'Physical', 'value': 'physical'},
                                    {'label': 'Psychological', 'value': 'psychological'},
                                    {'label': 'Social', 'value': 'social'},
                                    {'label': 'Religious', 'value': 'religious'},
                                    {'label': 'Political', 'value': 'political'},
                                    {'label': 'Computer Science', 'value': 'computer_science'},
                                    {'label': 'Linguistic', 'value': 'linguistic'},
                                    {'label': 'Other', 'value': 'other'}
                                ],
                                placeholder="Select category..."
                            )
                        ]
                    ),
                    # Mapping Type Dropdown
                    html.Div(
                        className="col-md-4",
                        children=[
                            html.Label("Mapping Type:", className="form-label"),
                            dcc.Dropdown(
                                id={'type': 'mapping-type', 'index': index},
                                options=[
                                    {'label': 'Isomorphic', 'value': 'isomorphic'},
                                    {'label': 'Analogical', 'value': 'analogical'},
                                    {'label': 'Metaphorical', 'value': 'metaphorical'},
                                    {'label': 'Contextual', 'value': 'contextual'}
                                ],
                                placeholder="Select type..."
                            )
                        ]
                    )
                ]
            )
        ],
        className="card p-3 mb-3",
        style={'border': '1px solid #ccc', 'borderRadius': '4px'}
    ) 