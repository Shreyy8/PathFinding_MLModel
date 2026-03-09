"""
Property-based tests for POST /api/clear-selection endpoint.

Tests the following properties:
- Property 13: Point Reselection and Path Clearing
- Property 19: State Consistency

Validates Requirements: 9.1, 9.2
"""

import pytest
import numpy as np
from hypothesis import given, strategies as st, settings, assume, HealthCheck
from unittest.mock import Mock
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


# Property 13: Point Reselection and Path Clearing (via clear_selection)
@given(
    start_x=st.integers(min_value=0, max_value=99),
    start_y=st.integers(min_value=0, max_value=99),
    goal_x=st.integers(min_value=0, max_value=99),
    goal_y=st.integers(min_value=0, max_value=99)
)
@settings(max_examples=50, deadline=None, suppress_health_check=[HealthCheck.function_scoped_fixture])
def test_property_13_clear_selection(api_client, state_manager, start_x, start_y, goal_x, goal_y):
    """
    Property 13: Point Reselection and Path Clearing
    
    For any session with start, goal, and path set, calling clear_selection
    should reset all selections to None while preserving image and graph.
    
    Validates: Requirements 9.1, 9.2
    """
    # Ensure start and goal are different
    assume((start_x, start_y) != (goal_x, goal_y))
    
    image_id = "test-image-clear"
    
    # Create session with both points as road pixels
    create_test_session(state_manager, image_id, width=100, height=100,
                       road_pixels=[(start_x, start_y), (goal_x, goal_y)])
    
    # Set start point, goal point, and path
    state_manager.set_start_point(image_id, start_x, start_y)
    state_manager.set_goal_point(image_id, goal_x, goal_y)
    state_manager.set_path(image_id, [(start_x, start_y), (goal_x, goal_y)])
    
    # Verify selections are set
    session = state_manager.get_session(image_id)
    assert session['start_point'] == (start_x, start_y)
    assert session['goal_point'] == (goal_x, goal_y)
    assert session['path'] is not None
    original_image = session['image']
    original_mask = session['road_mask']
    original_graph = session['graph']
    
    # Send clear_selection request
    response = api_client.post(
        '/api/clear-selection',
        data=json.dumps({'image_id': image_id}),
        content_type='application/json'
    )
    
    # Assert response indicates success
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['message'] == "Selection cleared"
    
    # Assert StateManager cleared selections but preserved image/graph
    session = state_manager.get_session(image_id)
    assert session['start_point'] is None
    assert session['goal_point'] is None
    assert session['path'] is None
    assert session['image'] is original_image
    assert session['road_mask'] is original_mask
    assert session['graph'] is original_graph


# Property 19: State Consistency (for clear_selection)
@given(
    start_x=st.integers(min_value=0, max_value=99),
    start_y=st.integers(min_value=0, max_value=99),
    goal_x=st.integers(min_value=0, max_value=99),
    goal_y=st.integers(min_value=0, max_value=99)
)
@settings(max_examples=50, deadline=None, suppress_health_check=[HealthCheck.function_scoped_fixture])
def test_property_19_state_consistency_clear(api_client, state_manager, start_x, start_y, goal_x, goal_y):
    """
    Property 19: State Consistency
    
    For any image_id, after calling clear_selection, the StateManager should
    maintain consistent state with all selections set to None.
    
    Validates: State Management
    """
    # Ensure start and goal are different
    assume((start_x, start_y) != (goal_x, goal_y))
    
    image_id = "test-image-state-clear"
    
    # Create session with selections
    create_test_session(state_manager, image_id, width=100, height=100,
                       road_pixels=[(start_x, start_y), (goal_x, goal_y)])
    
    state_manager.set_start_point(image_id, start_x, start_y)
    state_manager.set_goal_point(image_id, goal_x, goal_y)
    state_manager.set_path(image_id, [(start_x, start_y), (goal_x, goal_y)])
    
    # Clear selection
    response = api_client.post(
        '/api/clear-selection',
        data=json.dumps({'image_id': image_id}),
        content_type='application/json'
    )
    
    assert response.status_code == 200
    
    # Verify state consistency - all selections should be None
    session = state_manager.get_session(image_id)
    assert session['start_point'] is None
    assert session['goal_point'] is None
    assert session['path'] is None
    
    # Verify session still exists and has image/graph
    assert state_manager.session_exists(image_id)
    assert session['image'] is not None
    assert session['road_mask'] is not None
    assert session['graph'] is not None


# Unit test: Clear selection with no selections set
def test_clear_selection_empty_session(api_client, state_manager):
    """
    Test that clearing selection on a session with no selections works correctly.
    """
    image_id = "test-image-empty"
    
    # Create session with no selections
    create_test_session(state_manager, image_id)
    
    # Verify no selections
    session = state_manager.get_session(image_id)
    assert session['start_point'] is None
    assert session['goal_point'] is None
    assert session['path'] is None
    
    # Clear selection (should succeed even with nothing to clear)
    response = api_client.post(
        '/api/clear-selection',
        data=json.dumps({'image_id': image_id}),
        content_type='application/json'
    )
    
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['message'] == "Selection cleared"
    
    # Verify state remains None
    session = state_manager.get_session(image_id)
    assert session['start_point'] is None
    assert session['goal_point'] is None
    assert session['path'] is None


# Unit test: Clear selection with only start point
def test_clear_selection_only_start(api_client, state_manager):
    """
    Test that clearing selection works when only start point is set.
    """
    image_id = "test-image-only-start"
    
    # Create session with only start point
    create_test_session(state_manager, image_id, road_pixels=[(10, 10)])
    state_manager.set_start_point(image_id, 10, 10)
    
    # Verify start point is set
    session = state_manager.get_session(image_id)
    assert session['start_point'] == (10, 10)
    assert session['goal_point'] is None
    assert session['path'] is None
    
    # Clear selection
    response = api_client.post(
        '/api/clear-selection',
        data=json.dumps({'image_id': image_id}),
        content_type='application/json'
    )
    
    assert response.status_code == 200
    
    # Verify start point was cleared
    session = state_manager.get_session(image_id)
    assert session['start_point'] is None


# Unit test: Clear selection with only goal point
def test_clear_selection_only_goal(api_client, state_manager):
    """
    Test that clearing selection works when only goal point is set.
    """
    image_id = "test-image-only-goal"
    
    # Create session with only goal point
    create_test_session(state_manager, image_id, road_pixels=[(20, 20)])
    state_manager.set_goal_point(image_id, 20, 20)
    
    # Verify goal point is set
    session = state_manager.get_session(image_id)
    assert session['start_point'] is None
    assert session['goal_point'] == (20, 20)
    assert session['path'] is None
    
    # Clear selection
    response = api_client.post(
        '/api/clear-selection',
        data=json.dumps({'image_id': image_id}),
        content_type='application/json'
    )
    
    assert response.status_code == 200
    
    # Verify goal point was cleared
    session = state_manager.get_session(image_id)
    assert session['goal_point'] is None


# Unit test: Missing image_id
def test_clear_selection_missing_image_id(api_client):
    """Test clear_selection with missing image_id."""
    response = api_client.post(
        '/api/clear-selection',
        data=json.dumps({}),
        content_type='application/json'
    )
    
    assert response.status_code == 400
    data = json.loads(response.data)
    assert data['code'] == 'INVALID_REQUEST'
    assert 'image_id' in data['details']


# Unit test: Invalid image_id (session doesn't exist)
def test_clear_selection_invalid_image_id(api_client):
    """Test clear_selection with non-existent image_id."""
    response = api_client.post(
        '/api/clear-selection',
        data=json.dumps({'image_id': 'non-existent'}),
        content_type='application/json'
    )
    
    assert response.status_code == 404
    data = json.loads(response.data)
    assert data['code'] == 'IMAGE_NOT_FOUND'


# Unit test: No JSON body
def test_clear_selection_no_json_body(api_client):
    """Test clear_selection with no JSON body."""
    response = api_client.post('/api/clear-selection', content_type='application/json')
    
    assert response.status_code == 400
    data = json.loads(response.data)
    assert data['code'] == 'INVALID_REQUEST'


# Unit test: Invalid JSON
def test_clear_selection_invalid_json(api_client):
    """Test clear_selection with invalid JSON."""
    response = api_client.post(
        '/api/clear-selection',
        data='invalid json',
        content_type='application/json'
    )
    
    assert response.status_code == 400
    data = json.loads(response.data)
    assert data['code'] == 'INVALID_REQUEST'
