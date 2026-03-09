"""
Property-based tests for POST /api/select-start endpoint.

Tests the following properties:
- Property 7: Valid Point Acceptance
- Property 8: Invalid Point Rejection
- Property 19: State Consistency

Validates Requirements: 5.2, 5.3, 5.4
"""

import pytest
import numpy as np
from hypothesis import given, strategies as st, settings, assume, HealthCheck
from unittest.mock import Mock, MagicMock
import json

from src.api.app import BackendAPI
from src.api.state_manager import StateManager
from src.api.point_validator import PointValidator
from src.api.image_processor import ImageProcessor


# Test fixtures
@pytest.fixture
def state_manager():
    """Create StateManager instance for testing."""
    return StateManager()


@pytest.fixture
def point_validator():
    """Create PointValidator instance for testing."""
    return PointValidator()


@pytest.fixture
def image_processor():
    """Create ImageProcessor instance for testing."""
    return ImageProcessor()


@pytest.fixture
def mock_components():
    """Create mock components for BackendAPI."""
    return {
        'segmentation_model': Mock(),
        'graph_constructor': Mock(),
        'pathfinding_engine': Mock(),
        'pathfinding_coordinator': Mock()
    }


@pytest.fixture
def api_client(state_manager, point_validator, image_processor, mock_components):
    """Create Flask test client with BackendAPI."""
    backend_api = BackendAPI(
        state_manager=state_manager,
        segmentation_model=mock_components['segmentation_model'],
        graph_constructor=mock_components['graph_constructor'],
        pathfinding_engine=mock_components['pathfinding_engine'],
        image_processor=image_processor,
        point_validator=point_validator,
        pathfinding_coordinator=mock_components['pathfinding_coordinator']
    )
    
    app = backend_api.get_app()
    app.config['TESTING'] = True
    return app.test_client()


def create_test_session(state_manager, image_id, width=100, height=100, road_pixels=None):
    """
    Helper to create a test session with a road mask.
    
    Args:
        state_manager: StateManager instance
        image_id: Session ID
        width: Image width
        height: Image height
        road_pixels: List of (x, y) tuples representing road pixels
    """
    # Create test image
    image = np.zeros((height, width, 3), dtype=np.uint8)
    
    # Create road mask
    road_mask = np.zeros((height, width), dtype=np.uint8)
    
    if road_pixels:
        for x, y in road_pixels:
            if 0 <= x < width and 0 <= y < height:
                road_mask[y, x] = 255
    
    # Create mock graph
    mock_graph = Mock()
    
    # Create session
    state_manager.create_session(image_id, image, road_mask, mock_graph)


# Property 7: Valid Point Acceptance
@given(
    x=st.integers(min_value=0, max_value=99),
    y=st.integers(min_value=0, max_value=99)
)
@settings(max_examples=50, deadline=None, suppress_health_check=[HealthCheck.function_scoped_fixture])
def test_property_7_valid_point_acceptance(api_client, state_manager, x, y):
    """
    Property 7: Valid Point Acceptance
    
    For any coordinates that lie on a road pixel, the backend should return
    {valid: true} and update the StateManager with the selected point.
    
    Validates: Requirements 5.3
    """
    image_id = "test-image-valid-point"
    
    # Create session with the specific point as a road pixel
    create_test_session(state_manager, image_id, width=100, height=100, road_pixels=[(x, y)])
    
    # Send select_start request
    response = api_client.post(
        '/api/select-start',
        data=json.dumps({'image_id': image_id, 'x': x, 'y': y}),
        content_type='application/json'
    )
    
    # Assert response indicates valid point
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['valid'] is True
    assert data['coordinates']['x'] == x
    assert data['coordinates']['y'] == y
    assert 'message' in data
    
    # Assert StateManager was updated with start point
    session = state_manager.get_session(image_id)
    assert session['start_point'] == (x, y)


# Property 8: Invalid Point Rejection
@given(
    x=st.integers(min_value=0, max_value=99),
    y=st.integers(min_value=0, max_value=99),
    road_x=st.integers(min_value=0, max_value=99),
    road_y=st.integers(min_value=0, max_value=99)
)
@settings(max_examples=50, deadline=None, suppress_health_check=[HealthCheck.function_scoped_fixture])
def test_property_8_invalid_point_rejection(api_client, state_manager, x, y, road_x, road_y):
    """
    Property 8: Invalid Point Rejection
    
    For any coordinates that do not lie on a road pixel, the backend should return
    {valid: false, error: "Point is not on a road"} with HTTP status 400.
    
    Validates: Requirements 5.4
    """
    # Ensure selected point is different from road pixel
    assume((x, y) != (road_x, road_y))
    
    image_id = "test-image-invalid-point"
    
    # Create session with only one road pixel at (road_x, road_y)
    create_test_session(state_manager, image_id, width=100, height=100, road_pixels=[(road_x, road_y)])
    
    # Send select_start request for non-road point
    response = api_client.post(
        '/api/select-start',
        data=json.dumps({'image_id': image_id, 'x': x, 'y': y}),
        content_type='application/json'
    )
    
    # Assert response indicates invalid point
    assert response.status_code == 400
    data = json.loads(response.data)
    assert data['valid'] is False
    assert data['error'] == "Point is not on a road"
    assert data['coordinates']['x'] == x
    assert data['coordinates']['y'] == y
    
    # Assert StateManager was NOT updated with start point
    session = state_manager.get_session(image_id)
    assert session['start_point'] is None


# Property 19: State Consistency (for select_start)
@given(
    x1=st.integers(min_value=0, max_value=99),
    y1=st.integers(min_value=0, max_value=99),
    x2=st.integers(min_value=0, max_value=99),
    y2=st.integers(min_value=0, max_value=99)
)
@settings(max_examples=50, deadline=None, suppress_health_check=[HealthCheck.function_scoped_fixture])
def test_property_19_state_consistency_select_start(api_client, state_manager, x1, y1, x2, y2):
    """
    Property 19: State Consistency
    
    For any image_id, the StateManager should maintain consistent state such that
    the start point matches the most recent successful POST /api/select-start request.
    
    Validates: State Management
    """
    # Ensure points are different
    assume((x1, y1) != (x2, y2))
    
    image_id = "test-image-state-consistency"
    
    # Create session with both points as road pixels
    create_test_session(state_manager, image_id, width=100, height=100, road_pixels=[(x1, y1), (x2, y2)])
    
    # Select first start point
    response1 = api_client.post(
        '/api/select-start',
        data=json.dumps({'image_id': image_id, 'x': x1, 'y': y1}),
        content_type='application/json'
    )
    assert response1.status_code == 200
    
    # Verify state after first selection
    session = state_manager.get_session(image_id)
    assert session['start_point'] == (x1, y1)
    
    # Select second start point (reselection)
    response2 = api_client.post(
        '/api/select-start',
        data=json.dumps({'image_id': image_id, 'x': x2, 'y': y2}),
        content_type='application/json'
    )
    assert response2.status_code == 200
    
    # Verify state was updated to second point
    session = state_manager.get_session(image_id)
    assert session['start_point'] == (x2, y2)


# Additional unit tests for edge cases
def test_select_start_missing_image_id(api_client):
    """Test select_start with missing image_id."""
    response = api_client.post(
        '/api/select-start',
        data=json.dumps({'x': 10, 'y': 20}),
        content_type='application/json'
    )
    
    assert response.status_code == 400
    data = json.loads(response.data)
    assert 'error' in data


def test_select_start_missing_coordinates(api_client):
    """Test select_start with missing coordinates."""
    response = api_client.post(
        '/api/select-start',
        data=json.dumps({'image_id': 'test-id'}),
        content_type='application/json'
    )
    
    assert response.status_code == 400
    data = json.loads(response.data)
    assert 'error' in data


def test_select_start_invalid_image_id(api_client):
    """Test select_start with non-existent image_id."""
    response = api_client.post(
        '/api/select-start',
        data=json.dumps({'image_id': 'non-existent', 'x': 10, 'y': 20}),
        content_type='application/json'
    )
    
    assert response.status_code == 404
    data = json.loads(response.data)
    assert data['code'] == 'IMAGE_NOT_FOUND'


def test_select_start_invalid_coordinate_types(api_client, state_manager):
    """Test select_start with invalid coordinate types."""
    image_id = "test-image-invalid-types"
    create_test_session(state_manager, image_id)
    
    response = api_client.post(
        '/api/select-start',
        data=json.dumps({'image_id': image_id, 'x': 'invalid', 'y': 20}),
        content_type='application/json'
    )
    
    assert response.status_code == 400
    data = json.loads(response.data)
    assert data['code'] == 'INVALID_COORDINATES'


def test_select_start_no_json_body(api_client):
    """Test select_start with no JSON body."""
    response = api_client.post('/api/select-start', content_type='application/json')
    
    assert response.status_code == 400
    data = json.loads(response.data)
    assert 'error' in data


def test_select_start_clears_existing_path(api_client, state_manager):
    """Test that selecting a new start point clears any existing path."""
    image_id = "test-image-clear-path"
    
    # Create session with road pixels
    create_test_session(state_manager, image_id, width=100, height=100, road_pixels=[(10, 10), (20, 20)])
    
    # Set initial start, goal, and path
    state_manager.set_start_point(image_id, 10, 10)
    state_manager.set_goal_point(image_id, 20, 20)
    state_manager.set_path(image_id, [(10, 10), (15, 15), (20, 20)])
    
    # Verify path exists
    session = state_manager.get_session(image_id)
    assert session['path'] is not None
    
    # Select new start point
    response = api_client.post(
        '/api/select-start',
        data=json.dumps({'image_id': image_id, 'x': 20, 'y': 20}),
        content_type='application/json'
    )
    
    assert response.status_code == 200
    
    # Verify path was cleared
    session = state_manager.get_session(image_id)
    assert session['path'] is None
