"""
Unit tests for StateManager component.

Tests session creation, state management, point selection, and clearing operations.
"""

import pytest
import numpy as np
from unittest.mock import Mock
from src.api.state_manager import StateManager


@pytest.fixture
def state_manager():
    """Create StateManager instance."""
    return StateManager()


@pytest.fixture
def sample_image():
    """Create sample satellite image."""
    return np.random.randint(0, 255, (100, 100, 3), dtype=np.uint8)


@pytest.fixture
def sample_road_mask():
    """Create sample road mask."""
    mask = np.zeros((100, 100), dtype=np.uint8)
    mask[40:60, 40:60] = 255  # Road region
    return mask


@pytest.fixture
def sample_graph():
    """Create mock graph object."""
    return Mock()


class TestSessionCreation:
    """Test session creation and storage."""
    
    def test_create_session(self, state_manager, sample_image, sample_road_mask, sample_graph):
        """Test creating a new session."""
        image_id = "test-image-123"
        
        state_manager.create_session(image_id, sample_image, sample_road_mask, sample_graph)
        
        assert state_manager.session_exists(image_id)
        session = state_manager.get_session(image_id)
        assert session is not None
        assert np.array_equal(session['image'], sample_image)
        assert np.array_equal(session['road_mask'], sample_road_mask)
        assert session['graph'] == sample_graph
        assert session['start_point'] is None
        assert session['goal_point'] is None
        assert session['path'] is None
    
    def test_create_multiple_sessions(self, state_manager, sample_image, sample_road_mask, sample_graph):
        """Test creating multiple sessions with different image_ids."""
        image_id_1 = "image-1"
        image_id_2 = "image-2"
        
        state_manager.create_session(image_id_1, sample_image, sample_road_mask, sample_graph)
        state_manager.create_session(image_id_2, sample_image, sample_road_mask, sample_graph)
        
        assert state_manager.session_exists(image_id_1)
        assert state_manager.session_exists(image_id_2)
        assert state_manager.get_session(image_id_1) is not None
        assert state_manager.get_session(image_id_2) is not None


class TestSessionRetrieval:
    """Test session retrieval operations."""
    
    def test_get_existing_session(self, state_manager, sample_image, sample_road_mask, sample_graph):
        """Test retrieving an existing session."""
        image_id = "test-image"
        state_manager.create_session(image_id, sample_image, sample_road_mask, sample_graph)
        
        session = state_manager.get_session(image_id)
        
        assert session is not None
        assert 'image' in session
        assert 'road_mask' in session
        assert 'graph' in session
        assert 'start_point' in session
        assert 'goal_point' in session
        assert 'path' in session
    
    def test_get_nonexistent_session(self, state_manager):
        """Test retrieving a non-existent session returns None."""
        session = state_manager.get_session("nonexistent-id")
        assert session is None
    
    def test_session_exists_true(self, state_manager, sample_image, sample_road_mask, sample_graph):
        """Test session_exists returns True for existing session."""
        image_id = "test-image"
        state_manager.create_session(image_id, sample_image, sample_road_mask, sample_graph)
        
        assert state_manager.session_exists(image_id) is True
    
    def test_session_exists_false(self, state_manager):
        """Test session_exists returns False for non-existent session."""
        assert state_manager.session_exists("nonexistent-id") is False


class TestStartPointManagement:
    """Test start point selection and management."""
    
    def test_set_start_point(self, state_manager, sample_image, sample_road_mask, sample_graph):
        """Test setting start point for a session."""
        image_id = "test-image"
        state_manager.create_session(image_id, sample_image, sample_road_mask, sample_graph)
        
        state_manager.set_start_point(image_id, 50, 50)
        
        session = state_manager.get_session(image_id)
        assert session['start_point'] == (50, 50)
    
    def test_set_start_point_clears_path(self, state_manager, sample_image, sample_road_mask, sample_graph):
        """Test that setting start point clears existing path."""
        image_id = "test-image"
        state_manager.create_session(image_id, sample_image, sample_road_mask, sample_graph)
        state_manager.set_start_point(image_id, 40, 40)
        state_manager.set_goal_point(image_id, 60, 60)
        state_manager.set_path(image_id, [(40, 40), (50, 50), (60, 60)])
        
        # Change start point
        state_manager.set_start_point(image_id, 45, 45)
        
        session = state_manager.get_session(image_id)
        assert session['start_point'] == (45, 45)
        assert session['path'] is None
    
    def test_set_start_point_nonexistent_session(self, state_manager):
        """Test setting start point for non-existent session raises KeyError."""
        with pytest.raises(KeyError):
            state_manager.set_start_point("nonexistent-id", 50, 50)


class TestGoalPointManagement:
    """Test goal point selection and management."""
    
    def test_set_goal_point(self, state_manager, sample_image, sample_road_mask, sample_graph):
        """Test setting goal point for a session."""
        image_id = "test-image"
        state_manager.create_session(image_id, sample_image, sample_road_mask, sample_graph)
        
        state_manager.set_goal_point(image_id, 60, 60)
        
        session = state_manager.get_session(image_id)
        assert session['goal_point'] == (60, 60)
    
    def test_set_goal_point_clears_path(self, state_manager, sample_image, sample_road_mask, sample_graph):
        """Test that setting goal point clears existing path."""
        image_id = "test-image"
        state_manager.create_session(image_id, sample_image, sample_road_mask, sample_graph)
        state_manager.set_start_point(image_id, 40, 40)
        state_manager.set_goal_point(image_id, 60, 60)
        state_manager.set_path(image_id, [(40, 40), (50, 50), (60, 60)])
        
        # Change goal point
        state_manager.set_goal_point(image_id, 65, 65)
        
        session = state_manager.get_session(image_id)
        assert session['goal_point'] == (65, 65)
        assert session['path'] is None
    
    def test_set_goal_point_nonexistent_session(self, state_manager):
        """Test setting goal point for non-existent session raises KeyError."""
        with pytest.raises(KeyError):
            state_manager.set_goal_point("nonexistent-id", 60, 60)


class TestPathManagement:
    """Test path storage and management."""
    
    def test_set_path(self, state_manager, sample_image, sample_road_mask, sample_graph):
        """Test setting path for a session."""
        image_id = "test-image"
        state_manager.create_session(image_id, sample_image, sample_road_mask, sample_graph)
        path = [(40, 40), (45, 45), (50, 50), (55, 55), (60, 60)]
        
        state_manager.set_path(image_id, path)
        
        session = state_manager.get_session(image_id)
        assert session['path'] == path
    
    def test_set_empty_path(self, state_manager, sample_image, sample_road_mask, sample_graph):
        """Test setting empty path."""
        image_id = "test-image"
        state_manager.create_session(image_id, sample_image, sample_road_mask, sample_graph)
        
        state_manager.set_path(image_id, [])
        
        session = state_manager.get_session(image_id)
        assert session['path'] == []
    
    def test_set_path_nonexistent_session(self, state_manager):
        """Test setting path for non-existent session raises KeyError."""
        with pytest.raises(KeyError):
            state_manager.set_path("nonexistent-id", [(40, 40), (60, 60)])


class TestClearSelection:
    """Test clearing selections."""
    
    def test_clear_selection(self, state_manager, sample_image, sample_road_mask, sample_graph):
        """Test clearing start point, goal point, and path."""
        image_id = "test-image"
        state_manager.create_session(image_id, sample_image, sample_road_mask, sample_graph)
        state_manager.set_start_point(image_id, 40, 40)
        state_manager.set_goal_point(image_id, 60, 60)
        state_manager.set_path(image_id, [(40, 40), (50, 50), (60, 60)])
        
        state_manager.clear_selection(image_id)
        
        session = state_manager.get_session(image_id)
        assert session['start_point'] is None
        assert session['goal_point'] is None
        assert session['path'] is None
        # Image, mask, and graph should remain
        assert session['image'] is not None
        assert session['road_mask'] is not None
        assert session['graph'] is not None
    
    def test_clear_selection_preserves_image_data(self, state_manager, sample_image, sample_road_mask, sample_graph):
        """Test that clear_selection preserves image, mask, and graph."""
        image_id = "test-image"
        state_manager.create_session(image_id, sample_image, sample_road_mask, sample_graph)
        state_manager.set_start_point(image_id, 40, 40)
        
        state_manager.clear_selection(image_id)
        
        session = state_manager.get_session(image_id)
        assert np.array_equal(session['image'], sample_image)
        assert np.array_equal(session['road_mask'], sample_road_mask)
        assert session['graph'] == sample_graph
    
    def test_clear_selection_nonexistent_session(self, state_manager):
        """Test clearing selection for non-existent session raises KeyError."""
        with pytest.raises(KeyError):
            state_manager.clear_selection("nonexistent-id")


class TestStateConsistency:
    """Test state consistency across operations."""
    
    def test_workflow_consistency(self, state_manager, sample_image, sample_road_mask, sample_graph):
        """Test complete workflow maintains state consistency."""
        image_id = "test-image"
        
        # Create session
        state_manager.create_session(image_id, sample_image, sample_road_mask, sample_graph)
        assert state_manager.session_exists(image_id)
        
        # Set start point
        state_manager.set_start_point(image_id, 40, 40)
        session = state_manager.get_session(image_id)
        assert session['start_point'] == (40, 40)
        assert session['goal_point'] is None
        assert session['path'] is None
        
        # Set goal point
        state_manager.set_goal_point(image_id, 60, 60)
        session = state_manager.get_session(image_id)
        assert session['start_point'] == (40, 40)
        assert session['goal_point'] == (60, 60)
        assert session['path'] is None
        
        # Set path
        path = [(40, 40), (50, 50), (60, 60)]
        state_manager.set_path(image_id, path)
        session = state_manager.get_session(image_id)
        assert session['start_point'] == (40, 40)
        assert session['goal_point'] == (60, 60)
        assert session['path'] == path
        
        # Clear selection
        state_manager.clear_selection(image_id)
        session = state_manager.get_session(image_id)
        assert session['start_point'] is None
        assert session['goal_point'] is None
        assert session['path'] is None
    
    def test_reselection_workflow(self, state_manager, sample_image, sample_road_mask, sample_graph):
        """Test reselecting points clears path appropriately."""
        image_id = "test-image"
        state_manager.create_session(image_id, sample_image, sample_road_mask, sample_graph)
        
        # Initial selection
        state_manager.set_start_point(image_id, 40, 40)
        state_manager.set_goal_point(image_id, 60, 60)
        state_manager.set_path(image_id, [(40, 40), (50, 50), (60, 60)])
        
        # Reselect start point
        state_manager.set_start_point(image_id, 45, 45)
        session = state_manager.get_session(image_id)
        assert session['start_point'] == (45, 45)
        assert session['goal_point'] == (60, 60)
        assert session['path'] is None  # Path should be cleared
        
        # Set new path
        state_manager.set_path(image_id, [(45, 45), (52, 52), (60, 60)])
        
        # Reselect goal point
        state_manager.set_goal_point(image_id, 65, 65)
        session = state_manager.get_session(image_id)
        assert session['start_point'] == (45, 45)
        assert session['goal_point'] == (65, 65)
        assert session['path'] is None  # Path should be cleared again
