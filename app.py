import dash
import dash_bootstrap_components as dbc
from dash import html

# Initialize the Dash app
# Use Bootstrap for styling
# suppress_callback_exceptions=True is used to allow callbacks to be defined in separate files or later in the code
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP], suppress_callback_exceptions=True)

# Make the Flask server instance accessible for Gunicorn
# This is the variable Gunicorn looks for by default (app:server)
server = app.server

# Define a simple layout
app.layout = dbc.Container([
    html.H1("Ethics Dash - Landing Page"),
    html.Hr(),
    dbc.Row([
        dbc.Col([
            html.P("This is the main application container."),
            html.P("Replace this content with your actual landing page layout and components.")
            # Add components for your landing page and other pages here
        ])
    ])
], fluid=True)

# Add callbacks for interactivity here
# Example:
# @app.callback(
#     Output('some-output', 'children'),
#     Input('some-input', 'value')
# )
# def update_output(value):
#     return f'You have entered: {value}'

# Run the app server if this script is executed directly
# This is useful for local development without Docker/Gunicorn
if __name__ == '__main__':
    # Set debug=True for local development to enable hot-reloading and view error messages in the browser
    # IMPORTANT: Gunicorn will run the app with debug=False in the container unless configured otherwise
    app.run_server(debug=True, host='0.0.0.0', port=8050) 