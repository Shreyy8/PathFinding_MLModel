"""
Property-based tests for POST /api/select-goal endpoint.

Tests the following properties:
- Property 11: Pathfinding Invocation
- Property 13: Point Reselection and Path Clearing

Validates Requirements: 6.2, 6.3, 7.1, 7.2, 9.1, 9.2, 9.3
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
from src.api.pathfinding_coordinator import PathfindingCoordinator


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
def mock_pathfinding_coordinator():
    """Create mock PathfindingCoordinator for testing."""
    def _create_coordinator():
        coordinator = Mock(spec=PathfindingCoordinator)
        # Default behavior: return a simple path
        coordinator.compute_path.return_value = [(0, 0), (50, 50), (100, 100)]
        return coordinator
    return _create_coordinator


@pytest.fixture
def mock_components(mock_pathfinding_coordinator):
    """Create mock components for BackendAPI."""
    return {
        'segmentation_model': Mock(),
        'graph_constructor': Mock(),
        'pathfinding_engine': Mock(),
        'pathfinding_coordinator': mock_pathfinding_coordinator()
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


# Property 11: Pathfinding Invocation
@given(
    start_x=st.integers(min_value=0, max_value=99),
    start_y=st.integers(min_value=0, max_value=99),
    goal_x=st.integers(min_value=0, max_value=99),
    goal_y=st.integers(min_value=0, max_value=99)
)
@settings(max_examples=50, deadline=None, suppress_health_check=[HealthCheck.function_scoped_fixture])
def test_property_11_pathfinding_invocation(api_client, state_manager, mock_components, start_x, start_y, goal_x, goal_y):
    """
    Property 11: Pathfinding Invocation
    
    For any POST /api/select-goal request where both start and goal points are valid and set,
    the backend should automatically invoke PathfindingEngine and return the computed path
    in the response.
    
    Validates: Requirements 7.1, 7.2
    """
    # Reset mock for this test run
    mock_components['pathfinding_coordinator'].reset_mock()
    
    # Ensure start and goal are different
    assume((start_x, start_y) != (goal_x, goal_y))
    
    image_id = "test-image-pathfinding"
    
    # Create session with both points as road pixels
    create_test_session(state_manager, image_id, width=100, height=100, 
                       road_pixels=[(start_x, start_y), (goal_x, goal_y)])
    
    # Set start point
    state_manager.set_start_point(image_id, start_x, start_y)
    
    # Configure mock to return a path
    expected_path = [(start_x, start_y), (goal_x, goal_y)]
    mock_components['pathfinding_coordinator'].compute_path.return_value = expected_path
    
    # Send select_goal request
    response = api_client.post(
        '/api/select-goal',
        data=json.dumps({'image_id': image_id, 'x': goal_x, 'y': goal_y}),
        content_type='application/json'
    )
    
    # Assert response indicates valid point with path
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['valid'] is True
    assert data['coordinates']['x'] == goal_x
    assert data['coordinates']['y'] == goal_y
    assert data['path'] is not None
    assert len(data['path']) > 0
    
    # Assert PathfindingCoordinator was invoked (check it was called, not exact count)
    assert mock_components['pathfinding_coordinator'].compute_path.called
    
    # Assert StateManager was updated with goal point and path
    session = state_manager.get_session(image_id)
    assert session['goal_point'] == (goal_x, goal_y)
    assert session['path'] == expected_path


# Test valid goal point without start point
@given(
    x=st.integers(min_value=0, max_value=99),
    y=st.integers(min_value=0, max_value=99)
)
@settings(max_examples=50, deadline=None, suppress_health_check=[HealthCheck.function_scoped_fixture])
def test_valid_goal_without_start(api_client, state_manager, mock_components, x, y):
    """
    Test that selecting a valid goal point without a start point returns success
    but no path.
    
    Validates: Requirement 6.3
    """
    # Reset mock for this test run
    mock_components['pathfinding_coordinator'].reset_mock()
    
    image_id = "test-image-goal-no-start"
    
    # Create session with the point as a road pixel
    create_test_session(state_manager, image_id, width=100, height=100, road_pixels=[(x, y)])
    
    # Send select_goal request (no start point set)
    response = api_client.post(
        '/api/select-goal',
        data=json.dumps({'image_id': image_id, 'x': x, 'y': y}),
        content_type='application/json'
    )
    
    # Assert response indicates valid point without path
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['valid'] is True
    assert data['coordinates']['x'] == x
    assert data['coordinates']['y'] == y
    assert data['path'] is None
    assert 'no start point' in data['message'].lower()
    
    # Assert PathfindingCoordinator was NOT invoked
    assert not mock_components['pathfinding_coordinator'].compute_path.called
    
    # Assert StateManager was updated with goal point but no path
    session = state_manager.get_session(image_id)
    assert session['goal_point'] == (x, y)
    assert session['path'] is None


# Test invalid goal point rejection
@given(
    x=st.integers(min_value=0, max_value=99),
    y=st.integers(min_value=0, max_value=99),
    road_x=st.integers(min_value=0, max_value=99),
    road_y=st.integers(min_value=0, max_value=99)
)
@settings(max_examples=50, deadline=None, suppress_health_check=[HealthCheck.function_scoped_fixture])
def test_invalid_goal_point_rejection(api_client, state_manager, x, y, road_x, road_y):
    """
    Test that selecting an invalid goal point (not on road) returns error.
    
    Validates: Requirement 6.4
    """
    # Ensure selected point is different from road pixel
    assume((x, y) != (road_x, road_y))
    
    image_id = "test-image-invalid-goal"
    
    # Create session with only one road pixel at (road_x, road_y)
    create_test_session(state_manager, image_id, width=100, height=100, road_pixels=[(road_x, road_y)])
    
    # Send select_goal request for non-road point
    response = api_client.post(
        '/api/select-goal',
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
    
    # Assert StateManager was NOT updated with goal point
    session = state_manager.get_session(image_id)
    assert session['goal_point'] is None


# Property 13: Point Reselection and Path Clearing
@given(
    start_x=st.integers(min_value=0, max_value=99),
    start_y=st.integers(min_value=0, max_value=99),
    goal1_x=st.integers(min_value=0, max_value=99),
    goal1_y=st.integers(min_value=0, max_value=99),
    goal2_x=st.integers(min_value=0, max_value=99),
    goal2_y=st.integers(min_value=0, max_value=99)
)
@settings(max_examples=50, deadline=None, suppress_health_check=[HealthCheck.function_scoped_fixture])
def test_property_13_goal_reselection(api_client, state_manager, mock_components, 
                                      start_x, start_y, goal1_x, goal1_y, goal2_x, goal2_y):
    """
    Property 13: Point Reselection and Path Clearing
    
    For any reselection of goal point after both start and goal have been set,
    the backend should recompute a new path.
    
    Validates: Requirements 9.1, 9.2, 9.3
    """
    # Reset mock for this test run
    mock_components['pathfinding_coordinator'].reset_mock()
    
    # Ensure all points are different
    assume((start_x, start_y) != (goal1_x, goal1_y))
    assume((start_x, start_y) != (goal2_x, goal2_y))
    assume((goal1_x, goal1_y) != (goal2_x, goal2_y))
    
    image_id = "test-image-reselection"
    
    # Create session with all points as road pixels
    create_test_session(state_manager, image_id, width=100, height=100,
                       road_pixels=[(start_x, start_y), (goal1_x, goal1_y), (goal2_x, goal2_y)])
    
    # Set start point
    state_manager.set_start_point(image_id, start_x, start_y)
    
    # Configure mock for first path
    path1 = [(start_x, start_y), (goal1_x, goal1_y)]
    mock_components['pathfinding_coordinator'].compute_path.return_value = path1
    
    # Select first goal point
    response1 = api_client.post(
        '/api/select-goal',
        data=json.dumps({'image_id': image_id, 'x': goal1_x, 'y': goal1_y}),
        content_type='application/json'
    )
    
    assert response1.status_code == 200
    data1 = json.loads(response1.data)
    assert data1['path'] is not None
    
    # Verify first path was stored
    session = state_manager.get_session(image_id)
    assert session['goal_point'] == (goal1_x, goal1_y)
    assert session['path'] == path1
    
    # Configure mock for second path
    path2 = [(start_x, start_y), (goal2_x, goal2_y)]
    mock_components['pathfinding_coordinator'].compute_path.return_value = path2
    
    # Select second goal point (reselection)
    response2 = api_client.post(
        '/api/select-goal',
        data=json.dumps({'image_id': image_id, 'x': goal2_x, 'y': goal2_y}),
        content_type='application/json'
    )
    
    assert response2.status_code == 200
    data2 = json.loads(response2.data)
    assert data2['path'] is not None
    
    # Verify path was recomputed and updated
    session = state_manager.get_session(image_id)
    assert session['goal_point'] == (goal2_x, goal2_y)
    assert session['path'] == path2
    
    # Verify PathfindingCoordinator was called twice (once for each goal selection)
    assert mock_components['pathfinding_coordinator'].compute_path.call_count == 2


# Test pathfinding failure (no path exists)
def test_pathfinding_no_path_exists(api_client, state_manager, mock_components):
    """
    Test that pathfinding failure (no path) returns appropriate error.
    
    Validates: Requirement 7.3
    """
    image_id = "test-image-no-path"
    
    # Create session with start and goal as road pixels
    create_test_session(state_manager, image_id, width=100, height=100,
                       road_pixels=[(10, 10), (90, 90)])
    
    # Set start point
    state_manager.set_start_point(image_id, 10, 10)
    
    # Configure mock to raise ValueError (no path exists)
    mock_components['pathfinding_coordinator'].compute_path.side_effect = ValueError("No path found")
    
    # Send select_goal request
    response = api_client.post(
        '/api/select-goal',
        data=json.dumps({'image_id': image_id, 'x': 90, 'y': 90}),
        content_type='application/json'
    )
    
    # Assert response indicates pathfinding failure
    assert response.status_code == 400
    data = json.loads(response.data)
    assert data['valid'] is True  # Point is valid, but no path
    assert data['path'] is None
    assert 'no path' in data['error'].lower()
    assert data['code'] == 'PATHFINDING_FAILED'


# Test pathfinding exception
def test_pathfinding_exception(api_client, state_manager, mock_components):
    """
    Test that pathfinding exception returns 500 error.
    
    Validates: Requirement 7.4, 11.1
    """
    image_id = "test-image-pathfinding-error"
    
    # Create session with start and goal as road pixels
    create_test_session(state_manager, image_id, width=100, height=100,
                       road_pixels=[(10, 10), (90, 90)])
    
    # Set start point
    state_manager.set_start_point(image_id, 10, 10)
    
    # Configure mock to raise unexpected exception
    mock_components['pathfinding_coordinator'].compute_path.side_effect = RuntimeError("Unexpected error")
    
    # Send select_goal request
    response = api_client.post(
        '/api/select-goal',
        data=json.dumps({'image_id': image_id, 'x': 90, 'y': 90}),
        content_type='application/json'
    )
    
    # Assert response indicates internal error
    assert response.status_code == 500
    data = json.loads(response.data)
    assert data['code'] == 'PATHFINDING_FAILED'
    assert 'error' in data


# Additional unit tests for edge cases
def test_select_goal_missing_image_id(api_client):
    """Test select_goal with missing image_id."""
    response = api_client.post(
        '/api/select-goal',
        data=json.dumps({'x': 10, 'y': 20}),
        content_type='application/json'
    )
    
    assert response.status_code == 400
    data = json.loads(response.data)
    assert 'error' in data


def test_select_goal_missing_coordinates(api_client):
    """Test select_goal with missing coordinates."""
    response = api_client.post(
        '/api/select-goal',
        data=json.dumps({'image_id': 'test-id'}),
        content_type='application/json'
    )
    
    assert response.status_code == 400
    data = json.loads(response.data)
    assert 'error' in data


def test_select_goal_invalid_image_id(api_client):
    """Test select_goal with non-existent image_id."""
    response = api_client.post(
        '/api/select-goal',
        data=json.dumps({'image_id': 'non-existent', 'x': 10, 'y': 20}),
        content_type='application/json'
    )
    
    assert response.status_code == 404
    data = json.loads(response.data)
    assert data['code'] == 'IMAGE_NOT_FOUND'


def test_select_goal_invalid_coordinate_types(api_client, state_manager):
    """Test select_goal with invalid coordinate types."""
    image_id = "test-image-invalid-types"
    create_test_session(state_manager, image_id)
    
    response = api_client.post(
        '/api/select-goal',
        data=json.dumps({'image_id': image_id, 'x': 'invalid', 'y': 20}),
        content_type='application/json'
    )
    
    assert response.status_code == 400
    data = json.loads(response.data)
    assert data['code'] == 'INVALID_COORDINATES'


def test_select_goal_no_json_body(api_client):
    """Test select_goal with no JSON body."""
    response = api_client.post('/api/select-goal', content_type='application/json')
    
    assert response.status_code == 400
    data = json.loads(response.data)
    assert 'error' in data
