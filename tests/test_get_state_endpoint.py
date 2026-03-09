"""
Property tests for GET /api/state/{image_id} endpoint.

Tests Property 19: State Consistency
Validates that StateManager maintains consistent state across operations.
"""

import pytest
import numpy as np
from hypothesis import given, strategies as st, settings, assume, HealthCheck
from unittest.mock import Mock, MagicMock
import uuid

from src.api.state_manager import StateManager
from src.api.point_validator import PointValidator
from src.api.image_processor import ImageProcessor
from src.api.pathfinding_coordinator import PathfindingCoordinator
from src.api.app import BackendAPI


# Test fixtures
@pytest.fixture
def state_manager():
    """Create StateManager instance."""
    return StateManager()


@pytest.fixture
def mock_segmentation_model():
    """Create mock RoadSegmentationModel."""
    model = Mock()
    # Return a simple road mask
    model.predict = Mock(return_value=np.ones((100, 100), dtype=np.uint8) * 255)
    return model


@pytest.fixture
def mock_graph_constructor():
    """Create mock GraphConstructor."""
    constructor = Mock()
    mock_graph = MagicMock()
    mock_graph.number_of_nodes = Mock(return_value=100)
    mock_graph.number_of_edges = Mock(return_value=200)
    constructor.build_graph = Mock(return_value=mock_graph)
    return constructor


@pytest.fixture
def mock_pathfinding_engine():
    """Create mock PathfindingEngine."""
    engine = Mock()
    # Configure side_effect to return a path from start to goal
    def mock_find_path(graph, start, goal):
        # Return a simple path from start to goal
        return [start, goal]
    engine.find_path = Mock(side_effect=mock_find_path)
    return engine


@pytest.fixture
def point_validator():
    """Create PointValidator instance."""
    return PointValidator()


@pytest.fixture
def image_processor():
    """Create ImageProcessor instance."""
    return ImageProcessor()


@pytest.fixture
def pathfinding_coordinator(mock_pathfinding_engine):
    """Create PathfindingCoordinator instance."""
    return PathfindingCoordinator(mock_pathfinding_engine)


@pytest.fixture
def backend_api(
    state_manager,
    mock_segmentation_model,
    mock_graph_constructor,
    mock_pathfinding_engine,
    image_processor,
    point_validator,
    pathfinding_coordinator
):
    """Create BackendAPI instance with test client."""
    api = BackendAPI(
        state_manager=state_manager,
        segmentation_model=mock_segmentation_model,
        graph_constructor=mock_graph_constructor,
        pathfinding_engine=mock_pathfinding_engine,
        image_processor=image_processor,
        point_validator=point_validator,
        pathfinding_coordinator=pathfinding_coordinator
    )
    api.app.config['TESTING'] = True
    return api.app.test_client()


# Helper function to create a test session
def create_test_session(state_manager, image_id=None):
    """Create a test session with image, mask, and graph."""
    if image_id is None:
        image_id = str(uuid.uuid4())
    
    # Create test image and mask
    image = np.ones((100, 100, 3), dtype=np.uint8) * 128
    road_mask = np.ones((100, 100), dtype=np.uint8) * 255
    
    # Create mock graph
    mock_graph = MagicMock()
    mock_graph.number_of_nodes = Mock(return_value=100)
    mock_graph.number_of_edges = Mock(return_value=200)
    
    # Create session
    state_manager.create_session(image_id, image, road_mask, mock_graph)
    
    return image_id


# Property 19: State Consistency
# For any image_id, the StateManager should maintain consistent state such that
# GET /api/state/{image_id} returns the current start point, goal point, and path
# that match the most recent successful POST requests.

@given(
    start_x=st.integers(min_value=0, max_value=99),
    start_y=st.integers(min_value=0, max_value=99),
    goal_x=st.integers(min_value=0, max_value=99),
    goal_y=st.integers(min_value=0, max_value=99)
)
@settings(max_examples=50, deadline=None, suppress_health_check=[HealthCheck.function_scoped_fixture])
def test_property_19_state_consistency_after_point_selection(
    backend_api,
    state_manager,
    start_x,
    start_y,
    goal_x,
    goal_y
):
    """
    Property 19: State Consistency
    
    Test that GET /api/state/{image_id} returns consistent state after point selections.
    
    Given:
        - A valid session with image_id
        - Start point (start_x, start_y) selected
        - Goal point (goal_x, goal_y) selected
    
    When:
        - GET /api/state/{image_id} is called
    
    Then:
        - Response should contain the same start_point and goal_point
        - State should be consistent with StateManager
    """
    # Create test session
    image_id = create_test_session(state_manager)
    
    # Select start point
    response = backend_api.post(
        '/api/select-start',
        json={'image_id': image_id, 'x': start_x, 'y': start_y}
    )
    assert response.status_code == 200
    
    # Select goal point
    response = backend_api.post(
        '/api/select-goal',
        json={'image_id': image_id, 'x': goal_x, 'y': goal_y}
    )
    assert response.status_code == 200
    
    # Get state
    response = backend_api.get(f'/api/state/{image_id}')
    assert response.status_code == 200
    
    data = response.get_json()
    
    # Verify state consistency
    assert data['image_id'] == image_id
    assert data['has_image'] is True
    assert data['start_point'] == {'x': start_x, 'y': start_y}
    assert data['goal_point'] == {'x': goal_x, 'y': goal_y}
    
    # Verify consistency with StateManager
    session = state_manager.get_session(image_id)
    assert session['start_point'] == (start_x, start_y)
    assert session['goal_point'] == (goal_x, goal_y)


def test_property_19_state_consistency_after_clear_selection(backend_api, state_manager):
    """
    Property 19: State Consistency
    
    Test that GET /api/state/{image_id} returns consistent state after clearing selection.
    
    Given:
        - A valid session with start and goal points selected
    
    When:
        - POST /api/clear-selection is called
        - GET /api/state/{image_id} is called
    
    Then:
        - Response should show start_point and goal_point as null
        - State should be consistent with StateManager
    """
    # Create test session
    image_id = create_test_session(state_manager)
    
    # Select start and goal points
    backend_api.post('/api/select-start', json={'image_id': image_id, 'x': 50, 'y': 50})
    backend_api.post('/api/select-goal', json={'image_id': image_id, 'x': 60, 'y': 60})
    
    # Clear selection
    response = backend_api.post('/api/clear-selection', json={'image_id': image_id})
    assert response.status_code == 200
    
    # Get state
    response = backend_api.get(f'/api/state/{image_id}')
    assert response.status_code == 200
    
    data = response.get_json()
    
    # Verify state consistency after clearing
    assert data['image_id'] == image_id
    assert data['has_image'] is True
    assert data['start_point'] is None
    assert data['goal_point'] is None
    assert data['path'] is None
    
    # Verify consistency with StateManager
    session = state_manager.get_session(image_id)
    assert session['start_point'] is None
    assert session['goal_point'] is None
    assert session['path'] is None


def test_property_19_state_consistency_with_path(backend_api, state_manager, pathfinding_coordinator):
    """
    Property 19: State Consistency
    
    Test that GET /api/state/{image_id} returns consistent state including computed path.
    
    Given:
        - A valid session with start and goal points
        - A path computed between the points
    
    When:
        - GET /api/state/{image_id} is called
    
    Then:
        - Response should include the computed path
        - State should be consistent with StateManager
    """
    # Create test session
    image_id = create_test_session(state_manager)
    
    # Mock pathfinding to return a simple path
    test_path = [[50, 50], [55, 55], [60, 60]]
    pathfinding_coordinator.compute_path = Mock(return_value=test_path)
    
    # Select start and goal points (this will trigger pathfinding)
    backend_api.post('/api/select-start', json={'image_id': image_id, 'x': 50, 'y': 50})
    backend_api.post('/api/select-goal', json={'image_id': image_id, 'x': 60, 'y': 60})
    
    # Get state
    response = backend_api.get(f'/api/state/{image_id}')
    assert response.status_code == 200
    
    data = response.get_json()
    
    # Verify state consistency with path
    assert data['image_id'] == image_id
    assert data['has_image'] is True
    assert data['start_point'] == {'x': 50, 'y': 50}
    assert data['goal_point'] == {'x': 60, 'y': 60}
    assert data['path'] == test_path
    
    # Verify consistency with StateManager
    session = state_manager.get_session(image_id)
    assert session['path'] == test_path


def test_get_state_invalid_image_id(backend_api):
    """
    Test that GET /api/state/{image_id} returns 404 for invalid image_id.
    
    Given:
        - An invalid image_id that doesn't exist
    
    When:
        - GET /api/state/{image_id} is called
    
    Then:
        - Response should return 404 status code
        - Response should contain appropriate error message
    """
    invalid_image_id = str(uuid.uuid4())
    
    response = backend_api.get(f'/api/state/{invalid_image_id}')
    
    assert response.status_code == 404
    data = response.get_json()
    assert 'error' in data
    assert data['code'] == 'IMAGE_NOT_FOUND'


def test_get_state_initial_state(backend_api, state_manager):
    """
    Test that GET /api/state/{image_id} returns correct initial state.
    
    Given:
        - A newly created session with no points selected
    
    When:
        - GET /api/state/{image_id} is called
    
    Then:
        - Response should show has_image=True
        - start_point, goal_point, and path should be null
    """
    # Create test session
    image_id = create_test_session(state_manager)
    
    # Get state immediately after creation
    response = backend_api.get(f'/api/state/{image_id}')
    assert response.status_code == 200
    
    data = response.get_json()
    
    # Verify initial state
    assert data['image_id'] == image_id
    assert data['has_image'] is True
    assert data['start_point'] is None
    assert data['goal_point'] is None
    assert data['path'] is None


def test_get_state_only_start_point(backend_api, state_manager):
    """
    Test that GET /api/state/{image_id} returns correct state with only start point.
    
    Given:
        - A session with only start point selected
    
    When:
        - GET /api/state/{image_id} is called
    
    Then:
        - Response should show start_point set
        - goal_point and path should be null
    """
    # Create test session
    image_id = create_test_session(state_manager)
    
    # Select only start point
    backend_api.post('/api/select-start', json={'image_id': image_id, 'x': 50, 'y': 50})
    
    # Get state
    response = backend_api.get(f'/api/state/{image_id}')
    assert response.status_code == 200
    
    data = response.get_json()
    
    # Verify state with only start point
    assert data['image_id'] == image_id
    assert data['has_image'] is True
    assert data['start_point'] == {'x': 50, 'y': 50}
    assert data['goal_point'] is None
    assert data['path'] is None
