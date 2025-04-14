# --- Helper Functions for Dynamic Inputs ---
def create_morphism_inputs(index, meme_options):
    return dbc.Card([
        dbc.CardHeader(dbc.Row([
            dbc.Col(f"Morphism {index + 1}"),
            dbc.Col(dbc.Button(
                "Remove", 
                id={'type': 'remove-morphism-button', 'index': index}, 
                color="danger", 
                size="sm",
                n_clicks=0
            ), width="auto")
        ], justify="between")), 
        dbc.CardBody([
             dbc.Row([
                 dbc.Col(dbc.Label("Morphism Type:"), width=3),
                 dbc.Col(dcc.Dropdown(
                     id={'type': 'morphism-type', 'index': index},
                     options=[
                         {'label': 'Universalizes', 'value': 'Universalizes'},
                         {'label': 'Concretizes', 'value': 'Concretizes'},
                         {'label': 'Generates Consequence', 'value': 'Generates Consequence'},
                     ]), width=9),
             ], className="mb-2"),
             dbc.Row([
                dbc.Col(dbc.Label("Target Meme:"), width=3),
                dbc.Col(dcc.Dropdown(
                    id={'type': 'morphism-target', 'index': index},
                    options=meme_options, 
                    placeholder="Select target meme..."
                ), width=9),
             ], className="mb-2"),
             dbc.Row([
                dbc.Col(dbc.Label("Description:"), width=3),
                dbc.Col(dcc.Input(
                    id={'type': 'morphism-desc', 'index': index},
                    type='text', placeholder="Optional description", style={'width': '100%'}
                ), width=9)
             ])
        ])
    ], className="mb-2", id={'type': 'morphism-card', 'index': index})

def create_mapping_inputs(index):
    return dbc.Card([
        dbc.CardHeader(dbc.Row([
            dbc.Col(f"Mapping {index + 1}"),
            dbc.Col(dbc.Button(
                "Remove", 
                id={'type': 'remove-mapping-button', 'index': index},
                color="danger", 
                size="sm",
                n_clicks=0
            ), width="auto")
        ], justify="between")), 
        dbc.CardBody([
             dbc.Row([
                 dbc.Col(dbc.Label("Target Concept:"), width=3),
                 dbc.Col(dcc.Input(
                     id={'type': 'mapping-concept', 'index': index},
                     type='text', placeholder="e.g., Net Benefit"
                 ), width=9),
             ], className="mb-2"),
             dbc.Row([
                 dbc.Col(dbc.Label("Target Category:"), width=3),
                 dbc.Col(dcc.Dropdown(
                     id={'type': 'mapping-category', 'index': index},
                     options=[
                         {'label': 'Deontology', 'value': 'Deontology'},
                         {'label': 'Teleology', 'value': 'Teleology'},
                         {'label': 'Areteology', 'value': 'Areteology'},
                     ]), width=9),
             ], className="mb-2"),
             dbc.Row([
                 dbc.Col(dbc.Label("Mapping Type:"), width=3),
                 dbc.Col(dcc.Dropdown(
                     id={'type': 'mapping-type', 'index': index},
                     options=[
                         {'label': 'Functorial Analogy', 'value': 'Functorial Analogy'},
                         {'label': 'Conceptual Bridge', 'value': 'Conceptual Bridge'},
                     ]), width=9),
             ])
        ])
    ], className="mb-2", id={'type': 'mapping-card', 'index': index}) 