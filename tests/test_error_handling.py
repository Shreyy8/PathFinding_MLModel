"""
Property-based tests for error handling in the Backend API.

Tests Properties 14, 16, and 17:
- Property 14: Component Failure Error Handling
- Property 16: Error Logging
- Property 17: Recoverable Error Retry

Validates Requirements: 2.3, 4.3, 7.4, 11.1, 11.2, 11.3, 11.4
"""

import pytest
from hypothesis import given, strategies as st, settings, assume, HealthCheck
from unittest.mock import Mock, patch, MagicMock
import numpy as np
import io
from PIL import Image
import logging

from src.api.app import BackendAPI
from src.api.state_manager import StateManager
from src.api.image_processor import ImageProcessor
from src.api.point_validator import PointValidator
from src.api.pathfinding_coordinator import PathfindingCoordinator
from src.api.exceptions import (
    SegmentationFailedError,
    GraphConstructionFailedError,
    PathfindingFailedError,
    InvalidImageError,
    ImageNotFoundError,
    InvalidCoordinatesError
)


@pytest.fixture
def mock_components():
    """Create mock components for testing."""
    state_manager = StateManager()
    segmentation_model = Mock()
    graph_constructor = Mock()
    pathfinding_engine = Mock()
    image_processor = ImageProcessor()
    point_validator = PointValidator()
    pathfinding_coordinator = PathfindingCoordinator(pathfinding_engine)
    
    return {
        'state_manager': state_manager,
        'segmentation_model': segmentation_model,
        'graph_constructor': graph_constructor,
        'pathfinding_engine': pathfinding_engine,
        'image_processor': image_processor,
        'point_validator': point_validator,
        'pathfinding_coordinator': pathfinding_coordinator
    }


@pytest.fixture
def api_client(mock_components):
    """Create Flask test client with mock components."""
    backend_api = BackendAPI(**mock_components)
    app = backend_api.get_app()
    app.config['TESTING'] = True
    return app.test_client()


# ============================================================================
# Property 14: Component Failure Error Handling
# ============================================================================

def test_property_14_segmentation_failure_returns_500_with_error_code(api_client, mock_components):
    """
    Property 14: Component Failure Error Handling (Segmentation)
    
    For any component failure during backend processing (segmentation),
    the backend should return an appropriate HTTP error status (500) with
    a descriptive error message and error code SEGMENTATION_FAILED.
    
    Validates: Requirements 2.3, 11.1
    """
    # Create a valid test image
    img = Image.new('RGB', (100, 100), color='red')
    img_bytes = io.BytesIO()
    img.save(img_bytes, format='PNG')
    img_bytes.seek(0)
    
    # Mock segmentation to raise an exception
    mock_components['segmentation_model'].predict.side_effect = Exception("Segmentation model crashed")
    
    # Upload image
    response = api_client.post(
        '/api/load-image',
        data={'image': (img_bytes, 'test.png')},
        content_type='multipart/form-data'
    )
    
    # Assert error response
    assert response.status_code == 500
    data = response.get_json()
    assert data['code'] == 'SEGMENTATION_FAILED'
    assert 'error' in data
    assert 'details' in data


def test_property_14_graph_construction_failure_returns_500_with_error_code(api_client, mock_components):
    """
    Property 14: Component Failure Error Handling (Graph Construction)
    
    For any component failure during backend processing (graph construction),
    the backend should return an appropriate HTTP error status (500) with
    a descriptive error message and error code GRAPH_CONSTRUCTION_FAILED.
    
    Validates: Requirements 4.3, 11.1
    """
    # Create a valid test image
    img = Image.new('RGB', (100, 100), color='red')
    img_bytes = io.BytesIO()
    img.save(img_bytes, format='PNG')
    img_bytes.seek(0)
    
    # Mock segmentation to succeed
    mock_components['segmentation_model'].predict.return_value = np.ones((100, 100), dtype=np.uint8) * 255
    
    # Mock graph construction to raise an exception
    mock_components['graph_constructor'].build_graph.side_effect = Exception("Graph construction failed")
    
    # Upload image
    response = api_client.post(
        '/api/load-image',
        data={'image': (img_bytes, 'test.png')},
        content_type='multipart/form-data'
    )
    
    # Assert error response
    assert response.status_code == 500
    data = response.get_json()
    assert data['code'] == 'GRAPH_CONSTRUCTION_FAILED'
    assert 'error' in data
    assert 'details' in data


def test_property_14_pathfinding_failure_returns_500_with_error_code(api_client, mock_components):
    """
    Property 14: Component Failure Error Handling (Pathfinding)
    
    For any component failure during backend processing (pathfinding),
    the backend should return an appropriate HTTP error status (500) with
    a descriptive error message and error code PATHFINDING_FAILED.
    
    Validates: Requirements 7.4, 11.1
    """
    # Setup: Create a session with image and graph
    image_id = "test-image-id"
    road_mask = np.ones((100, 100), dtype=np.uint8) * 255
    graph = Mock()
    graph.number_of_nodes.return_value = 100
    graph.number_of_edges.return_value = 200
    
    mock_components['state_manager'].create_session(
        image_id,
        np.zeros((100, 100, 3), dtype=np.uint8),
        road_mask,
        graph
    )
    
    # Set start point
    mock_components['state_manager'].set_start_point(image_id, 10, 10)
    
    # Mock pathfinding to raise an exception
    mock_components['pathfinding_engine'].find_shortest_path.side_effect = RuntimeError("Pathfinding crashed")
    
    # Select goal point (should trigger pathfinding)
    response = api_client.post(
        '/api/select-goal',
        json={'image_id': image_id, 'x': 50, 'y': 50}
    )
    
    # Assert error response
    assert response.status_code == 500
    data = response.get_json()
    assert data['code'] == 'PATHFINDING_FAILED'
    assert 'error' in data


@given(
    width=st.integers(min_value=10, max_value=200),
    height=st.integers(min_value=10, max_value=200)
)
@settings(max_examples=10, deadline=None, suppress_health_check=[HealthCheck.function_scoped_fixture])
def test_property_14_component_failures_always_return_structured_errors(width, height):
    """
    Property 14: Component Failure Error Handling (Universal)
    
    For any valid image dimensions, when any component fails during processing,
    the backend should always return a structured error response with:
    - error: descriptive message
    - code: error code identifier
    - details: additional information
    
    Validates: Requirements 11.1, 11.2
    """
    # Create fresh mock components for each test
    state_manager = StateManager()
    segmentation_model = Mock()
    graph_constructor = Mock()
    pathfinding_engine = Mock()
    image_processor = ImageProcessor()
    point_validator = PointValidator()
    pathfinding_coordinator = PathfindingCoordinator(pathfinding_engine)
    
    backend_api = BackendAPI(
        state_manager=state_manager,
        segmentation_model=segmentation_model,
        graph_constructor=graph_constructor,
        pathfinding_engine=pathfinding_engine,
        image_processor=image_processor,
        point_validator=point_validator,
        pathfinding_coordinator=pathfinding_coordinator
    )
    app = backend_api.get_app()
    app.config['TESTING'] = True
    client = app.test_client()
    
    # Create a valid test image
    img = Image.new('RGB', (width, height), color='blue')
    img_bytes = io.BytesIO()
    img.save(img_bytes, format='PNG')
    img_bytes.seek(0)
    
    # Mock segmentation to fail
    segmentation_model.predict.side_effect = Exception("Component failure")
    
    # Upload image
    response = client.post(
        '/api/load-image',
        data={'image': (img_bytes, 'test.png')},
        content_type='multipart/form-data'
    )
    
    # Assert structured error response
    assert response.status_code in [400, 500]
    data = response.get_json()
    
    # Property: All error responses must have these fields
    assert 'error' in data, "Error response must include 'error' field"
    assert 'code' in data, "Error response must include 'code' field"
    assert 'details' in data, "Error response must include 'details' field"
    
    # Property: Error fields must be non-empty strings
    assert isinstance(data['error'], str) and len(data['error']) > 0
    assert isinstance(data['code'], str) and len(data['code']) > 0
    assert isinstance(data['details'], str) and len(data['details']) > 0


# ============================================================================
# Property 16: Error Logging
# ============================================================================

def test_property_16_errors_are_logged_with_timestamp_and_details(api_client, mock_components, caplog):
    """
    Property 16: Error Logging
    
    For any error that occurs during backend operation, the backend should
    log the error with sufficient detail (timestamp, error type, stack trace)
    for debugging purposes.
    
    Validates: Requirement 11.3
    """
    with caplog.at_level(logging.ERROR):
        # Create a valid test image
        img = Image.new('RGB', (100, 100), color='red')
        img_bytes = io.BytesIO()
        img.save(img_bytes, format='PNG')
        img_bytes.seek(0)
        
        # Mock segmentation to raise an exception
        mock_components['segmentation_model'].predict.side_effect = Exception("Test error for logging")
        
        # Upload image (should trigger error)
        response = api_client.post(
            '/api/load-image',
            data={'image': (img_bytes, 'test.png')},
            content_type='multipart/form-data'
        )
        
        # Assert error was logged
        assert response.status_code == 500
        
        # Property: Error must be logged
        assert len(caplog.records) > 0, "Error should be logged"
        
        # Property: Log should contain error information
        error_logs = [record for record in caplog.records if record.levelno >= logging.ERROR]
        assert len(error_logs) > 0, "At least one ERROR level log should exist"
        
        # Property: Log record should have timestamp (automatically added by logging)
        for record in error_logs:
            assert hasattr(record, 'created'), "Log record should have timestamp"
            assert record.created > 0, "Timestamp should be valid"


@given(
    error_message=st.text(min_size=1, max_size=100)
)
@settings(max_examples=10, deadline=None, suppress_health_check=[HealthCheck.function_scoped_fixture])
def test_property_16_all_errors_are_logged_regardless_of_message(error_message, caplog):
    """
    Property 16: Error Logging (Universal)
    
    For any error message, when an error occurs, it should be logged
    with appropriate log level and details.
    
    Validates: Requirement 11.3
    """
    # Filter out problematic characters that might cause issues
    assume(len(error_message.strip()) > 0)
    
    # Create fresh mock components for each test
    state_manager = StateManager()
    segmentation_model = Mock()
    graph_constructor = Mock()
    pathfinding_engine = Mock()
    image_processor = ImageProcessor()
    point_validator = PointValidator()
    pathfinding_coordinator = PathfindingCoordinator(pathfinding_engine)
    
    backend_api = BackendAPI(
        state_manager=state_manager,
        segmentation_model=segmentation_model,
        graph_constructor=graph_constructor,
        pathfinding_engine=pathfinding_engine,
        image_processor=image_processor,
        point_validator=point_validator,
        pathfinding_coordinator=pathfinding_coordinator
    )
    app = backend_api.get_app()
    app.config['TESTING'] = True
    client = app.test_client()
    
    with caplog.at_level(logging.ERROR):
        # Create a valid test image
        img = Image.new('RGB', (50, 50), color='green')
        img_bytes = io.BytesIO()
        img.save(img_bytes, format='PNG')
        img_bytes.seek(0)
        
        # Mock segmentation to raise an exception with the given message
        segmentation_model.predict.side_effect = Exception(error_message)
        
        # Upload image (should trigger error)
        response = client.post(
            '/api/load-image',
            data={'image': (img_bytes, 'test.png')},
            content_type='multipart/form-data'
        )
        
        # Property: Error response should be returned
        assert response.status_code == 500
        
        # Property: Error should be logged
        error_logs = [record for record in caplog.records if record.levelno >= logging.ERROR]
        assert len(error_logs) > 0, "Error should be logged regardless of message content"


def test_property_16_request_and_response_logging(api_client, mock_components, caplog):
    """
    Property 16: Error Logging (Request/Response)
    
    The backend should log API requests and responses for debugging purposes.
    
    Validates: Requirement 11.3
    """
    with caplog.at_level(logging.INFO):
        # Make a simple request
        response = api_client.get('/api/health')
        
        # Property: Request should be logged
        request_logs = [record for record in caplog.records 
                       if 'Request:' in record.message and 'GET' in record.message]
        assert len(request_logs) > 0, "Request should be logged"
        
        # Property: Response should be logged
        response_logs = [record for record in caplog.records 
                        if 'Response:' in record.message and '200' in record.message]
        assert len(response_logs) > 0, "Response should be logged"


# ============================================================================
# Property 17: Recoverable Error Retry
# ============================================================================

def test_property_17_invalid_image_error_allows_retry(api_client, mock_components):
    """
    Property 17: Recoverable Error Retry
    
    For any recoverable error condition (e.g., invalid image),
    the frontend should be able to retry the operation by sending
    a new request. The backend should handle the retry without issues.
    
    Validates: Requirements 11.4
    """
    # First attempt: Upload invalid image (empty file)
    img_bytes_invalid = io.BytesIO(b'')
    
    response1 = api_client.post(
        '/api/load-image',
        data={'image': (img_bytes_invalid, 'test.png')},
        content_type='multipart/form-data'
    )
    
    # Assert first attempt fails
    assert response1.status_code == 400
    data1 = response1.get_json()
    assert data1['code'] == 'INVALID_IMAGE'
    
    # Second attempt: Upload valid image (retry)
    img = Image.new('RGB', (100, 100), color='red')
    img_bytes_valid = io.BytesIO()
    img.save(img_bytes_valid, format='PNG')
    img_bytes_valid.seek(0)
    
    # Mock successful processing
    mock_components['segmentation_model'].predict.return_value = np.ones((100, 100), dtype=np.uint8) * 255
    mock_graph = Mock()
    mock_graph.number_of_nodes.return_value = 100
    mock_graph.number_of_edges.return_value = 200
    mock_components['graph_constructor'].build_graph.return_value = mock_graph
    
    response2 = api_client.post(
        '/api/load-image',
        data={'image': (img_bytes_valid, 'test.png')},
        content_type='multipart/form-data'
    )
    
    # Property: Retry should succeed after fixing the error
    assert response2.status_code == 200
    data2 = response2.get_json()
    assert 'image_id' in data2
    assert 'image_data' in data2


def test_property_17_segmentation_failure_allows_retry(api_client, mock_components):
    """
    Property 17: Recoverable Error Retry (Segmentation)
    
    For any recoverable error condition (e.g., segmentation failure),
    the system should allow retry with a different image or after
    fixing the issue.
    
    Validates: Requirements 2.3, 11.4
    """
    # Create a valid test image
    img = Image.new('RGB', (100, 100), color='blue')
    img_bytes = io.BytesIO()
    img.save(img_bytes, format='PNG')
    img_bytes.seek(0)
    
    # First attempt: Mock segmentation to fail
    mock_components['segmentation_model'].predict.side_effect = Exception("Segmentation failed")
    
    response1 = api_client.post(
        '/api/load-image',
        data={'image': (img_bytes, 'test.png')},
        content_type='multipart/form-data'
    )
    
    # Assert first attempt fails
    assert response1.status_code == 500
    data1 = response1.get_json()
    assert data1['code'] == 'SEGMENTATION_FAILED'
    
    # Second attempt: Create a new image for retry
    img2 = Image.new('RGB', (100, 100), color='blue')
    img_bytes2 = io.BytesIO()
    img2.save(img_bytes2, format='PNG')
    img_bytes2.seek(0)
    
    # Fix the segmentation (simulate retry after fixing issue)
    mock_components['segmentation_model'].predict.side_effect = None
    mock_components['segmentation_model'].predict.return_value = np.ones((100, 100), dtype=np.uint8) * 255
    
    mock_graph = Mock()
    mock_graph.number_of_nodes.return_value = 100
    mock_graph.number_of_edges.return_value = 200
    mock_components['graph_constructor'].build_graph.return_value = mock_graph
    
    response2 = api_client.post(
        '/api/load-image',
        data={'image': (img_bytes2, 'test.png')},
        content_type='multipart/form-data'
    )
    
    # Property: Retry should succeed after fixing the error
    assert response2.status_code == 200
    data2 = response2.get_json()
    assert 'image_id' in data2


@given(
    num_retries=st.integers(min_value=1, max_value=5)
)
@settings(max_examples=5, deadline=None, suppress_health_check=[HealthCheck.function_scoped_fixture])
def test_property_17_multiple_retries_are_supported(num_retries):
    """
    Property 17: Recoverable Error Retry (Multiple Retries)
    
    For any number of retry attempts, the backend should handle each
    request independently and allow multiple retries without state corruption.
    
    Validates: Requirement 11.4
    """
    # Create fresh mock components for each test
    state_manager = StateManager()
    segmentation_model = Mock()
    graph_constructor = Mock()
    pathfinding_engine = Mock()
    image_processor = ImageProcessor()
    point_validator = PointValidator()
    pathfinding_coordinator = PathfindingCoordinator(pathfinding_engine)
    
    backend_api = BackendAPI(
        state_manager=state_manager,
        segmentation_model=segmentation_model,
        graph_constructor=graph_constructor,
        pathfinding_engine=pathfinding_engine,
        image_processor=image_processor,
        point_validator=point_validator,
        pathfinding_coordinator=pathfinding_coordinator
    )
    app = backend_api.get_app()
    app.config['TESTING'] = True
    client = app.test_client()
    
    # Perform multiple failed attempts
    for i in range(num_retries):
        img_bytes = io.BytesIO(b'')  # Invalid image
        
        response = client.post(
            '/api/load-image',
            data={'image': (img_bytes, f'test{i}.png')},
            content_type='multipart/form-data'
        )
        
        # Property: Each retry should fail consistently
        assert response.status_code == 400
        data = response.get_json()
        assert data['code'] == 'INVALID_IMAGE'
    
    # Final attempt with valid image
    img = Image.new('RGB', (50, 50), color='yellow')
    img_bytes_valid = io.BytesIO()
    img.save(img_bytes_valid, format='PNG')
    img_bytes_valid.seek(0)
    
    segmentation_model.predict.return_value = np.ones((50, 50), dtype=np.uint8) * 255
    mock_graph = Mock()
    mock_graph.number_of_nodes.return_value = 50
    mock_graph.number_of_edges.return_value = 100
    graph_constructor.build_graph.return_value = mock_graph
    
    response_final = client.post(
        '/api/load-image',
        data={'image': (img_bytes_valid, 'test_final.png')},
        content_type='multipart/form-data'
    )
    
    # Property: After multiple retries, valid request should succeed
    assert response_final.status_code == 200
    data_final = response_final.get_json()
    assert 'image_id' in data_final


# ============================================================================
# Additional Error Handling Tests
# ============================================================================

def test_invalid_coordinates_error_code(api_client, mock_components):
    """
    Test that invalid coordinates return appropriate error code.
    
    Validates: Requirement 11.1
    """
    # Setup: Create a session
    image_id = "test-image-id"
    road_mask = np.ones((100, 100), dtype=np.uint8) * 255
    graph = Mock()
    
    mock_components['state_manager'].create_session(
        image_id,
        np.zeros((100, 100, 3), dtype=np.uint8),
        road_mask,
        graph
    )
    
    # Send request with invalid coordinate types
    response = api_client.post(
        '/api/select-start',
        json={'image_id': image_id, 'x': 'invalid', 'y': 'invalid'}
    )
    
    # Assert error response
    assert response.status_code == 400
    data = response.get_json()
    assert data['code'] == 'INVALID_COORDINATES'


def test_image_not_found_error_code(api_client):
    """
    Test that non-existent image_id returns appropriate error code.
    
    Validates: Requirement 11.1
    """
    # Send request with non-existent image_id
    response = api_client.post(
        '/api/select-start',
        json={'image_id': 'non-existent-id', 'x': 10, 'y': 10}
    )
    
    # Assert error response
    assert response.status_code == 404
    data = response.get_json()
    assert data['code'] == 'IMAGE_NOT_FOUND'


def test_point_not_on_road_error_code(api_client, mock_components):
    """
    Test that off-road point selection returns appropriate error code.
    
    Validates: Requirement 11.1
    """
    # Setup: Create a session with partial road mask
    image_id = "test-image-id"
    road_mask = np.zeros((100, 100), dtype=np.uint8)
    road_mask[10:20, 10:20] = 255  # Only small area is road
    graph = Mock()
    
    mock_components['state_manager'].create_session(
        image_id,
        np.zeros((100, 100, 3), dtype=np.uint8),
        road_mask,
        graph
    )
    
    # Select point off the road
    response = api_client.post(
        '/api/select-start',
        json={'image_id': image_id, 'x': 50, 'y': 50}
    )
    
    # Assert error response
    assert response.status_code == 400
    data = response.get_json()
    assert data['valid'] is False
    assert 'Point is not on a road' in data['error']
