# backend/tests/conftest.py
import pytest
import sys
import os

# Add the backend directory to the Python path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from app import create_app # Import from backend/app
from app.config import ALL_MODELS # Import from your new config

@pytest.fixture(scope='module')
def test_client():
    """Create a test client for the Flask app."""
    flask_app = create_app() # You might need to pass a test config here
    flask_app.config['TESTING'] = True

    # Create a test client using the Flask application configured for testing
    with flask_app.test_client() as testing_client:
        # Establish an application context
        with flask_app.app_context():
            yield testing_client 

@pytest.fixture(scope='module')
def mock_mongo_db(mocker):
    """Mocks the MongoDB client and database."""
    mock_db_instance = mocker.MagicMock()
    # Mock specific collections and their methods as needed for tests
    mock_db_instance.ethical_memes = mocker.MagicMock()

    # Mock current_app.db to return this mock_db_instance
    mocker.patch('flask.current_app.db', mock_db_instance)
    return mock_db_instance 