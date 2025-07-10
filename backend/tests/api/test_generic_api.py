# backend/tests/api/test_generic_api.py
import json
from app.config import ALL_MODELS # Import from your new config

def test_health_check(test_client):
    """Test the /api/health endpoint."""
    response = test_client.get('/api/health')
    assert response.status_code == 200
    data = json.loads(response.data.decode('utf-8'))
    assert data['status'] == 'healthy'
    assert 'database' in data
    assert 'services' in data

def test_get_models(test_client):
    """Test the /api/models endpoint."""
    response = test_client.get('/api/models')
    assert response.status_code == 200
    data = json.loads(response.data.decode('utf-8'))
    assert 'models' in data
    assert isinstance(data['models'], list)
    assert set(data['models']) == set(ALL_MODELS) # Check against config 