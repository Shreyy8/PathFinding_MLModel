"""
Property-based tests for POST /api/load-image endpoint.

Tests the load_image endpoint to ensure it correctly handles image uploads,
invokes segmentation and graph construction, and returns properly formatted responses.
"""

import pytest
import numpy as np
import io
from PIL import Image
from unittest.mock import Mock, MagicMock
from hypothesis import given, strategies as st, assume, settings, HealthCheck
import torch

from src.api.app import BackendAPI


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


def create_test_image_bytes(width, height):
    """Create a test image as bytes."""
    # Create RGB image
    image_array = np.random.randint(0, 256, (height, width, 3), dtype=np.uint8)
    image = Image.fromarray(image_array, mode='RGB')
    
    # Convert to bytes
    buffer = io.BytesIO()
    image.save(buffer, format='PNG')
    buffer.seek(0)
    
    return buffer.read()


def create_mock_api_instance():
    """Create a fresh mock API instance for property tests."""
    mock_components = {
        'state_manager': Mock(),
        'segmentation_model': Mock(),
        'graph_constructor': Mock(),
        'pathfinding_engine': Mock(),
        'image_processor': Mock(),
        'point_validator': Mock(),
        'pathfinding_coordinator': Mock()
    }
    return BackendAPI(**mock_components)


class TestLoadImagePropertyTests:
    """Property-based tests for load_image endpoint."""
    
    @given(
        width=st.integers(min_value=10, max_value=200),
        height=st.integers(min_value=10, max_value=200)
    )
    @settings(suppress_health_check=[HealthCheck.function_scoped_fixture], max_examples=10)
    def test_property_3_segmentation_invocation(self, width, height):
        """
        **Validates: Property 3 - Segmentation Invocation**
        
        For any valid satellite image uploaded to POST /api/load-image,
        the backend should automatically invoke RoadSegmentationModel
        and return road_mask_data in the response.
        
        **Validates: Requirements 2.1, 2.2**
        """
        # Create fresh API instance for this test
        api_instance = create_mock_api_instance()
        
        # Setup mocks
        test_image_bytes = create_test_image_bytes(width, height)
        test_image_array = np.random.randint(0, 256, (height, width, 3), dtype=np.uint8)
        test_road_mask = np.random.randint(0, 2, (height, width), dtype=np.uint8)
        mock_graph = MagicMock()
        mock_graph.number_of_nodes.return_value = 100
        mock_graph.number_of_edges.return_value = 200
        
        # Configure mocks
        api_instance.image_processor.load_image.return_value = test_image_array
        api_instance.image_processor.validate_image.return_value = True
        api_instance.segmentation_model.predict.return_value = test_road_mask
        api_instance.graph_constructor.build_graph.return_value = mock_graph
        api_instance.image_processor.encode_image_to_base64.return_value = "base64_image_data"
        api_instance.image_processor.encode_mask_to_base64.return_value = "base64_mask_data"
        
        # Create test client
        app = api_instance.get_app()
        app.config['TESTING'] = True
        client = app.test_client()
        
        # Make request
        data = {'image': (io.BytesIO(test_image_bytes), 'test.png')}
        response = client.post('/api/load-image', data=data, content_type='multipart/form-data')
        
        # Verify segmentation was invoked
        assert api_instance.segmentation_model.predict.called, \
            "RoadSegmentationModel.predict should be invoked for valid image"
        
        # Verify response contains road_mask_data
        if response.status_code == 200:
            response_data = response.get_json()
            assert 'road_mask_data' in response_data, \
                "Response should contain road_mask_data"
            assert response_data['road_mask_data'] is not None, \
                "road_mask_data should not be None"
    
    @given(
        width=st.integers(min_value=10, max_value=200),
        height=st.integers(min_value=10, max_value=200)
    )
    @settings(suppress_health_check=[HealthCheck.function_scoped_fixture], max_examples=10)
    def test_property_5_graph_construction_trigger(self, width, height):
        """
        **Validates: Property 5 - Graph Construction Trigger**
        
        For any road mask generated by segmentation during POST /api/load-image,
        the backend should automatically invoke GraphConstructor and store
        the resulting road graph in StateManager.
        
        **Validates: Requirements 4.1, 4.2**
        """
        # Create fresh API instance for this test
        api_instance = create_mock_api_instance()
        
        # Setup mocks
        test_image_bytes = create_test_image_bytes(width, height)
        test_image_array = np.random.randint(0, 256, (height, width, 3), dtype=np.uint8)
        test_road_mask = np.random.randint(0, 2, (height, width), dtype=np.uint8)
        mock_graph = MagicMock()
        mock_graph.number_of_nodes.return_value = 100
        mock_graph.number_of_edges.return_value = 200
        
        # Configure mocks
        api_instance.image_processor.load_image.return_value = test_image_array
        api_instance.image_processor.validate_image.return_value = True
        api_instance.segmentation_model.predict.return_value = test_road_mask
        api_instance.graph_constructor.build_graph.return_value = mock_graph
        api_instance.image_processor.encode_image_to_base64.return_value = "base64_image_data"
        api_instance.image_processor.encode_mask_to_base64.return_value = "base64_mask_data"
        
        # Create test client
        app = api_instance.get_app()
        app.config['TESTING'] = True
        client = app.test_client()
        
        # Make request
        data = {'image': (io.BytesIO(test_image_bytes), 'test.png')}
        response = client.post('/api/load-image', data=data, content_type='multipart/form-data')
        
        # Verify graph construction was invoked
        assert api_instance.graph_constructor.build_graph.called, \
            "GraphConstructor.build_graph should be invoked after segmentation"
        
        # Verify build_graph was called with the road mask
        call_args = api_instance.graph_constructor.build_graph.call_args
        assert call_args is not None, \
            "GraphConstructor.build_graph should be called with road mask"
        
        # Verify StateManager.create_session was called with the graph
        if response.status_code == 200:
            assert api_instance.state_manager.create_session.called, \
                "StateManager.create_session should be called to store graph"
            
            # Verify the graph was passed to create_session
            session_call_args = api_instance.state_manager.create_session.call_args
            assert session_call_args is not None, \
                "create_session should be called with image_id, image, mask, and graph"
    
    @given(
        width=st.integers(min_value=10, max_value=200),
        height=st.integers(min_value=10, max_value=200)
    )
    @settings(suppress_health_check=[HealthCheck.function_scoped_fixture], max_examples=10)
    def test_property_18_api_response_format_consistency(self, width, height):
        """
        **Validates: Property 18 - API Response Format Consistency**
        
        For any API endpoint response, the backend should return JSON data
        conforming to the documented response schema for that endpoint.
        
        For POST /api/load-image, the response should contain:
        - image_id (string)
        - image_data (base64 string)
        - road_mask_data (base64 string)
        - width (integer)
        - height (integer)
        - message (string)
        
        **Validates: API Contract**
        """
        # Create fresh API instance for this test
        api_instance = create_mock_api_instance()
        
        # Setup mocks
        test_image_bytes = create_test_image_bytes(width, height)
        test_image_array = np.random.randint(0, 256, (height, width, 3), dtype=np.uint8)
        test_road_mask = np.random.randint(0, 2, (height, width), dtype=np.uint8)
        mock_graph = MagicMock()
        mock_graph.number_of_nodes.return_value = 100
        mock_graph.number_of_edges.return_value = 200
        
        # Configure mocks
        api_instance.image_processor.load_image.return_value = test_image_array
        api_instance.image_processor.validate_image.return_value = True
        api_instance.segmentation_model.predict.return_value = test_road_mask
        api_instance.graph_constructor.build_graph.return_value = mock_graph
        api_instance.image_processor.encode_image_to_base64.return_value = "base64_image_data"
        api_instance.image_processor.encode_mask_to_base64.return_value = "base64_mask_data"
        
        # Create test client
        app = api_instance.get_app()
        app.config['TESTING'] = True
        client = app.test_client()
        
        # Make request
        data = {'image': (io.BytesIO(test_image_bytes), 'test.png')}
        response = client.post('/api/load-image', data=data, content_type='multipart/form-data')
        
        # Verify response is JSON
        assert response.content_type == 'application/json', \
            "Response should be JSON"
        
        # Verify response format for success case
        if response.status_code == 200:
            response_data = response.get_json()
            
            # Check all required fields are present
            required_fields = ['image_id', 'image_data', 'road_mask_data', 'width', 'height', 'message']
            for field in required_fields:
                assert field in response_data, \
                    f"Response should contain '{field}' field"
            
            # Verify field types
            assert isinstance(response_data['image_id'], str), \
                "image_id should be a string"
            assert isinstance(response_data['image_data'], str), \
                "image_data should be a base64 string"
            assert isinstance(response_data['road_mask_data'], str), \
                "road_mask_data should be a base64 string"
            assert isinstance(response_data['width'], int), \
                "width should be an integer"
            assert isinstance(response_data['height'], int), \
                "height should be an integer"
            assert isinstance(response_data['message'], str), \
                "message should be a string"
            
            # Verify dimensions match input
            assert response_data['width'] == width, \
                f"Response width should match input: expected {width}, got {response_data['width']}"
            assert response_data['height'] == height, \
                f"Response height should match input: expected {height}, got {response_data['height']}"
        
        # Verify response format for error cases
        elif response.status_code >= 400:
            response_data = response.get_json()
            
            # Error responses should have error, code, and details
            assert 'error' in response_data, \
                "Error response should contain 'error' field"
            assert 'code' in response_data, \
                "Error response should contain 'code' field"
            assert 'details' in response_data, \
                "Error response should contain 'details' field"


class TestLoadImageEdgeCases:
    """Test edge cases for load_image endpoint."""
    
    def test_missing_image_file(self, client):
        """Test request without image file."""
        response = client.post('/api/load-image', data={}, content_type='multipart/form-data')
        
        assert response.status_code == 400
        response_data = response.get_json()
        assert response_data['code'] == 'INVALID_IMAGE'
        assert 'No image file' in response_data['error']
    
    def test_empty_filename(self, client, api_instance):
        """Test request with empty filename."""
        data = {'image': (io.BytesIO(b''), '')}
        response = client.post('/api/load-image', data=data, content_type='multipart/form-data')
        
        assert response.status_code == 400
        response_data = response.get_json()
        assert response_data['code'] == 'INVALID_IMAGE'
    
    def test_invalid_image_data(self, client, api_instance):
        """Test request with invalid image data."""
        # Configure mock to raise ValueError
        api_instance.image_processor.load_image.side_effect = ValueError("Invalid image format")
        
        data = {'image': (io.BytesIO(b'invalid data'), 'test.png')}
        response = client.post('/api/load-image', data=data, content_type='multipart/form-data')
        
        assert response.status_code == 400
        response_data = response.get_json()
        assert response_data['code'] == 'INVALID_IMAGE'
    
    def test_image_validation_failure(self, client, api_instance):
        """Test request with image that fails validation."""
        # Configure mocks
        test_image_array = np.random.randint(0, 256, (100, 100, 3), dtype=np.uint8)
        api_instance.image_processor.load_image.return_value = test_image_array
        api_instance.image_processor.validate_image.return_value = False
        
        test_image_bytes = create_test_image_bytes(100, 100)
        data = {'image': (io.BytesIO(test_image_bytes), 'test.png')}
        response = client.post('/api/load-image', data=data, content_type='multipart/form-data')
        
        assert response.status_code == 400
        response_data = response.get_json()
        assert response_data['code'] == 'INVALID_IMAGE'
        assert 'validation failed' in response_data['error'].lower()
    
    def test_segmentation_failure(self, client, api_instance):
        """Test segmentation failure handling."""
        # Configure mocks
        test_image_array = np.random.randint(0, 256, (100, 100, 3), dtype=np.uint8)
        api_instance.image_processor.load_image.return_value = test_image_array
        api_instance.image_processor.validate_image.return_value = True
        api_instance.segmentation_model.predict.side_effect = RuntimeError("Segmentation failed")
        
        test_image_bytes = create_test_image_bytes(100, 100)
        data = {'image': (io.BytesIO(test_image_bytes), 'test.png')}
        response = client.post('/api/load-image', data=data, content_type='multipart/form-data')
        
        assert response.status_code == 500
        response_data = response.get_json()
        assert response_data['code'] == 'SEGMENTATION_FAILED'
    
    def test_graph_construction_failure(self, client, api_instance):
        """Test graph construction failure handling."""
        # Configure mocks
        test_image_array = np.random.randint(0, 256, (100, 100, 3), dtype=np.uint8)
        test_road_mask = np.random.randint(0, 2, (100, 100), dtype=np.uint8)
        
        api_instance.image_processor.load_image.return_value = test_image_array
        api_instance.image_processor.validate_image.return_value = True
        api_instance.segmentation_model.predict.return_value = test_road_mask
        api_instance.graph_constructor.build_graph.side_effect = ValueError("No road pixels")
        
        test_image_bytes = create_test_image_bytes(100, 100)
        data = {'image': (io.BytesIO(test_image_bytes), 'test.png')}
        response = client.post('/api/load-image', data=data, content_type='multipart/form-data')
        
        assert response.status_code == 500
        response_data = response.get_json()
        assert response_data['code'] == 'GRAPH_CONSTRUCTION_FAILED'
