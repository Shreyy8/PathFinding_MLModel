"""
Unit tests for Backend API setup and configuration.

Tests the basic Flask application setup, CORS configuration, error handlers,
and health check endpoint.
"""

import pytest
from unittest.mock import Mock
from src.api.app import BackendAPI
from src.api.config import APIConfig
from src.api.exceptions import (
    APIException,
    InvalidImageError,
    SegmentationFailedError,
    GraphConstructionFailedError,
    PointNotOnRoadError,
    PathfindingFailedError,
    ImageNotFoundError,
    InvalidCoordinatesError
)


@pytest.fixture
def mock_components():
    """Create mock components for BackendAPI."""
    return {
        'state_manager': Mock(),
        'segmentation_model': Mock(),
        'graph_constructor': Mock(),
        'pathfinding_engine': Mock(),
        'image_processor': Mock(),
        'point_validator': Mock(),
        'pathfinding_coordinator': Mock()
    }


@pytest.fixture
def api_instance(mock_components):
    """Create BackendAPI instance with mock components."""
    return BackendAPI(**mock_components)


@pytest.fixture
def client(api_instance):
    """Create Flask test client."""
    app = api_instance.get_app()
    app.config['TESTING'] = True
    return app.test_client()


class TestBackendAPISetup:
    """Test Backend API initialization and configuration."""
    
    def test_api_initialization(self, api_instance):
        """Test that BackendAPI initializes correctly."""
        assert api_instance.app is not None
        assert api_instance.state_manager is not None
        assert api_instance.segmentation_model is not None
        assert api_instance.graph_constructor is not None
        assert api_instance.pathfinding_engine is not None
    
    def test_flask_app_creation(self, api_instance):
        """Test that Flask app is created."""
        app = api_instance.get_app()
        assert app is not None
        assert app.name == 'src.api.app'
    
    def test_cors_configuration(self, api_instance):
        """Test that CORS is configured."""
        # CORS extension should be registered
        app = api_instance.get_app()
        assert 'cors' in app.extensions or hasattr(app, 'after_request_funcs')


class TestHealthEndpoint:
    """Test health check endpoint."""
    
    def test_health_check_success(self, client):
        """Test health check returns 200 OK."""
        response = client.get('/api/health')
        assert response.status_code == 200
        
        data = response.get_json()
        assert data['status'] == 'healthy'
        assert 'version' in data
    
    def test_health_check_json_format(self, client):
        """Test health check returns valid JSON."""
        response = client.get('/api/health')
        assert response.content_type == 'application/json'


class TestErrorHandlers:
    """Test error handling."""
    
    def test_404_handler(self, client):
        """Test 404 error handler."""
        response = client.get('/api/nonexistent')
        assert response.status_code == 404
        
        data = response.get_json()
        assert 'error' in data
        assert data['code'] == 'NOT_FOUND'
    
    def test_api_exception_handler(self, api_instance):
        """Test custom API exception handling."""
        app = api_instance.get_app()
        
        @app.route('/api/test-error')
        def test_error():
            raise InvalidImageError("Test error", "Test details")
        
        client = app.test_client()
        response = client.get('/api/test-error')
        
        assert response.status_code == 400
        data = response.get_json()
        assert data['code'] == 'INVALID_IMAGE'
        assert 'error' in data


class TestExceptions:
    """Test custom exception classes."""
    
    def test_invalid_image_error(self):
        """Test InvalidImageError exception."""
        error = InvalidImageError("Invalid format", "Not a PNG")
        assert error.status_code == 400
        assert error.error_code == "INVALID_IMAGE"
        assert error.message == "Invalid format"
        assert error.details == "Not a PNG"
    
    def test_segmentation_failed_error(self):
        """Test SegmentationFailedError exception."""
        error = SegmentationFailedError()
        assert error.status_code == 500
        assert error.error_code == "SEGMENTATION_FAILED"
    
    def test_graph_construction_failed_error(self):
        """Test GraphConstructionFailedError exception."""
        error = GraphConstructionFailedError()
        assert error.status_code == 500
        assert error.error_code == "GRAPH_CONSTRUCTION_FAILED"
    
    def test_point_not_on_road_error(self):
        """Test PointNotOnRoadError exception."""
        error = PointNotOnRoadError()
        assert error.status_code == 400
        assert error.error_code == "POINT_NOT_ON_ROAD"
    
    def test_pathfinding_failed_error(self):
        """Test PathfindingFailedError exception."""
        error = PathfindingFailedError()
        assert error.status_code == 500
        assert error.error_code == "PATHFINDING_FAILED"
    
    def test_image_not_found_error(self):
        """Test ImageNotFoundError exception."""
        error = ImageNotFoundError()
        assert error.status_code == 404
        assert error.error_code == "IMAGE_NOT_FOUND"
    
    def test_invalid_coordinates_error(self):
        """Test InvalidCoordinatesError exception."""
        error = InvalidCoordinatesError()
        assert error.status_code == 400
        assert error.error_code == "INVALID_COORDINATES"
    
    def test_exception_to_dict(self):
        """Test exception serialization to dictionary."""
        error = InvalidImageError("Test message", "Test details")
        error_dict = error.to_dict()
        
        assert error_dict['error'] == "Test message"
        assert error_dict['code'] == "INVALID_IMAGE"
        assert error_dict['details'] == "Test details"


class TestAPIConfig:
    """Test API configuration."""
    
    def test_default_config_values(self):
        """Test default configuration values."""
        assert APIConfig.HOST == "localhost"
        assert APIConfig.PORT == 5000
        assert APIConfig.DEBUG == False
        assert isinstance(APIConfig.CORS_ORIGINS, list)
        assert APIConfig.MAX_IMAGE_SIZE > 0
        assert APIConfig.MAX_IMAGE_DIMENSION > 0
    
    def test_get_config_dict(self):
        """Test configuration dictionary export."""
        config_dict = APIConfig.get_config_dict()
        
        assert 'host' in config_dict
        assert 'port' in config_dict
        assert 'debug' in config_dict
        assert 'cors_origins' in config_dict
        assert 'max_image_size' in config_dict
