"""
Backend API for Ethical Review Application
"""
from flask import Flask
from flask_cors import CORS

def create_app():
    """Factory pattern for creating Flask app with config"""
    app = Flask(__name__)
    # Enable CORS for frontend
    CORS(app)
    
    # Import and register blueprints
    from backend.app.api import api_bp
    app.register_blueprint(api_bp)
    
    return app 