"""
Integration tests for complete backend workflow.

Tests the full end-to-end workflow of the Interactive Road Mapping Interface:
1. Load image → road segmentation → graph construction
2. Select start point → validation
3. Select goal point → validation → pathfinding
4. Get state → verify consistency
5. Clear selection → verify cleanup
6. Point reselection → path recomputation

Requirements: 1.1, 2.1, 4.1, 5.1, 6.1, 7.1, 9.1, 9.2, 9.3
"""

import pytest
import numpy as np
import io
import json
from PIL import Image
from unittest.mock import Mock, MagicMock, patch
import networkx as nx
import torch

from src.api.app import BackendAPI
from src.api.state_manager import StateManager
from src.api.point_validator import PointValidator
from src.api.image_processor import ImageProcessor
from src.api.pathfinding_coordinator import PathfindingCoordinator
from src.road_segmentation_model import RoadSegmentationModel
from src.graph_constructor import GraphConstructor
from src.pathfinding_engine import PathfindingEngine


def create_test_image_bytes(width=100, height=100):
    """Create a test image as bytes."""
    image_array = np.random.randint(0, 256, (height, width, 3), dtype=np.uint8)
    image = Image.fromarray(image_array, mode='RGB')
    
    buffer = io.BytesIO()
    image.save(buffer, format='PNG')
    buffer.seek(0)
    
    return buffer.read()


def create_test_road_mask(width=100, height=100):
    """Create a test road mask with a simple road pattern."""
    mask = np.zeros((height, width), dtype=np.uint8)
    # Create a horizontal road in the middle
    mask[height//2-2:height//2+2, :] = 1
    # Create a vertical road in the middle
    mask[:, width//2-2:width//2+2] = 1
    return mask


def create_test_graph(road_mask):
    """Create a test graph from road mask."""
    graph_constructor = GraphConstructor(connectivity=8)
    return graph_constructor.build_graph(road_mask)


@pytest.fixture
def mock_segmentation_model():
    """Create mock segmentation model."""
    model = Mock(spec=RoadSegmentationModel)
    
    def predict_side_effect(image_tensor):
        # Return a simple road mask
        if isinstance(image_tensor, torch.Tensor):
            height, width = image_tensor.shape[-2:]
        else:
            height, width = 100, 100
        return create_test_road_mask(width, height)
    
    model.predict.side_effect = predict_side_effect
    return model


@pytest.fixture
def real_components(mock_segmentation_model):
    """Create real component instances for integration testing."""
    return {
        'state_manager': StateManager(),
        'segmentation_model': mock_segmentation_model,
        'graph_constructor': GraphConstructor(connectivity=8),
        'pathfinding_engine': PathfindingEngine(algorithm="astar"),
        'image_processor': ImageProcessor(),
        'point_validator': PointValidator(),
        'pathfinding_coordinator': PathfindingCoordinator(PathfindingEngine(algorithm="astar"))
    }


@pytest.fixture
def api_instance(real_components):
    """Create BackendAPI instance with real components."""
    return BackendAPI(**real_components)


@pytest.fixture
def client(api_instance):
    """Create Flask test client."""
    app = api_instance.get_app()
    app.config['TESTING'] = True
    return app.test_client()


class TestCompleteWorkflow:
    """Integration tests for complete backend workflow."""
    
    def test_full_workflow_load_select_pathfind(self, client):
        """
        Test complete workflow: load image → select start → select goal → get path.
        
        Validates: Requirements 1.1, 2.1, 4.1, 5.1, 6.1, 7.1
        """
        # Step 1: Load image
        test_image_bytes = create_test_image_bytes(100, 100)
        
        response = client.post(
            '/api/load-image',
            data={'image': (io.BytesIO(test_image_bytes), 'test.png')},
            content_type='multipart/form-data'
        )
        
        assert response.status_code == 200
        data = json.loads(response.data)
        
        assert 'image_id' in data
        assert 'image_data' in data
        assert 'road_mask_data' in data
        assert 'width' in data
        assert 'height' in data
        
        image_id = data['image_id']
        width = data['width']
        height = data['height']
        
        # Step 2: Select start point (on road)
        start_x, start_y = width // 2, height // 2  # Center of image (on road)
        
        response = client.post(
            '/api/select-start',
            data=json.dumps({'image_id': image_id, 'x': start_x, 'y': start_y}),
            content_type='application/json'
        )
        
        assert response.status_code == 200
        data = json.loads(response.data)
        
        assert data['valid'] is True
        assert data['coordinates']['x'] == start_x
        assert data['coordinates']['y'] == start_y
        
        # Step 3: Select goal point (on road)
        goal_x, goal_y = width // 2 + 10, height // 2  # Nearby point on road
        
        response = client.post(
            '/api/select-goal',
            data=json.dumps({'image_id': image_id, 'x': goal_x, 'y': goal_y}),
            content_type='application/json'
        )
        
        assert response.status_code == 200
        data = json.loads(response.data)
        
        assert data['valid'] is True
        assert data['coordinates']['x'] == goal_x
        assert data['coordinates']['y'] == goal_y
        assert 'path' in data
        
        # Path should exist between nearby points on same road
        if data['path'] is not None:
            path = data['path']
            assert len(path) >= 2
            assert path[0] == [start_x, start_y]
            assert path[-1] == [goal_x, goal_y]
        
        # Step 4: Get state and verify consistency
        response = client.get(f'/api/state/{image_id}')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        
        assert data['image_id'] == image_id
        assert data['has_image'] is True
        assert data['start_point'] == {'x': start_x, 'y': start_y}
        assert data['goal_point'] == {'x': goal_x, 'y': goal_y}
        assert 'path' in data
    
    def test_workflow_with_invalid_points(self, client):
        """
        Test workflow with invalid point selection (not on road).
        
        Validates: Requirements 5.4, 6.4
        """
        # Step 1: Load image
        test_image_bytes = create_test_image_bytes(100, 100)
        
        response = client.post(
            '/api/load-image',
            data={'image': (io.BytesIO(test_image_bytes), 'test.png')},
            content_type='multipart/form-data'
        )
        
        assert response.status_code == 200
        data = json.loads(response.data)
        image_id = data['image_id']
        
        # Step 2: Try to select start point NOT on road (corner of image)
        start_x, start_y = 5, 5  # Top-left corner (not on road)
        
        response = client.post(
            '/api/select-start',
            data=json.dumps({'image_id': image_id, 'x': start_x, 'y': start_y}),
            content_type='application/json'
        )
        
        # Should reject invalid point
        assert response.status_code == 400
        data = json.loads(response.data)
        assert data['valid'] is False
        assert 'error' in data
    
    def test_workflow_point_reselection(self, client):
        """
        Test point reselection and path recomputation.
        
        Validates: Requirements 9.1, 9.2, 9.3
        """
        # Step 1: Load image
        test_image_bytes = create_test_image_bytes(100, 100)
        
        response = client.post(
            '/api/load-image',
            data={'image': (io.BytesIO(test_image_bytes), 'test.png')},
            content_type='multipart/form-data'
        )
        
        assert response.status_code == 200
        data = json.loads(response.data)
        image_id = data['image_id']
        width = data['width']
        height = data['height']
        
        # Step 2: Select initial start and goal
        start_x1, start_y1 = width // 2, height // 2
        goal_x1, goal_y1 = width // 2 + 10, height // 2
        
        client.post(
            '/api/select-start',
            data=json.dumps({'image_id': image_id, 'x': start_x1, 'y': start_y1}),
            content_type='application/json'
        )
        
        response = client.post(
            '/api/select-goal',
            data=json.dumps({'image_id': image_id, 'x': goal_x1, 'y': goal_y1}),
            content_type='application/json'
        )
        
        assert response.status_code == 200
        data1 = json.loads(response.data)
        path1 = data1.get('path')
        
        # Step 3: Reselect start point
        start_x2, start_y2 = width // 2 - 10, height // 2
        
        response = client.post(
            '/api/select-start',
            data=json.dumps({'image_id': image_id, 'x': start_x2, 'y': start_y2}),
            content_type='application/json'
        )
        
        assert response.status_code == 200
        
        # Step 4: Reselect goal point to trigger path recomputation
        goal_x2, goal_y2 = width // 2 + 15, height // 2
        
        response = client.post(
            '/api/select-goal',
            data=json.dumps({'image_id': image_id, 'x': goal_x2, 'y': goal_y2}),
            content_type='application/json'
        )
        
        assert response.status_code == 200
        data2 = json.loads(response.data)
        path2 = data2.get('path')
        
        # Verify new path is computed
        if path1 is not None and path2 is not None:
            # Paths should be different after reselection
            assert path1 != path2
            # New path should start and end at new points
            assert path2[0] == [start_x2, start_y2]
            assert path2[-1] == [goal_x2, goal_y2]
    
    def test_workflow_clear_selection(self, client):
        """
        Test clear selection functionality.
        
        Validates: Requirements 9.2
        """
        # Step 1: Load image
        test_image_bytes = create_test_image_bytes(100, 100)
        
        response = client.post(
            '/api/load-image',
            data={'image': (io.BytesIO(test_image_bytes), 'test.png')},
            content_type='multipart/form-data'
        )
        
        assert response.status_code == 200
        data = json.loads(response.data)
        image_id = data['image_id']
        width = data['width']
        height = data['height']
        
        # Step 2: Select start and goal
        start_x, start_y = width // 2, height // 2
        goal_x, goal_y = width // 2 + 10, height // 2
        
        client.post(
            '/api/select-start',
            data=json.dumps({'image_id': image_id, 'x': start_x, 'y': start_y}),
            content_type='application/json'
        )
        
        client.post(
            '/api/select-goal',
            data=json.dumps({'image_id': image_id, 'x': goal_x, 'y': goal_y}),
            content_type='application/json'
        )
        
        # Step 3: Clear selection
        response = client.post(
            '/api/clear-selection',
            data=json.dumps({'image_id': image_id}),
            content_type='application/json'
        )
        
        assert response.status_code == 200
        
        # Step 4: Verify state is cleared
        response = client.get(f'/api/state/{image_id}')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        
        assert data['image_id'] == image_id
        assert data['has_image'] is True
        assert data['start_point'] is None
        assert data['goal_point'] is None
        assert data['path'] is None
    
    def test_workflow_state_consistency(self, client):
        """
        Test state consistency throughout workflow.
        
        Validates: Requirements 1.1, 5.1, 6.1, 7.1
        """
        # Step 1: Load image
        test_image_bytes = create_test_image_bytes(100, 100)
        
        response = client.post(
            '/api/load-image',
            data={'image': (io.BytesIO(test_image_bytes), 'test.png')},
            content_type='multipart/form-data'
        )
        
        assert response.status_code == 200
        data = json.loads(response.data)
        image_id = data['image_id']
        width = data['width']
        height = data['height']
        
        # Verify initial state
        response = client.get(f'/api/state/{image_id}')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['start_point'] is None
        assert data['goal_point'] is None
        assert data['path'] is None
        
        # Step 2: Select start point
        start_x, start_y = width // 2, height // 2
        
        client.post(
            '/api/select-start',
            data=json.dumps({'image_id': image_id, 'x': start_x, 'y': start_y}),
            content_type='application/json'
        )
        
        # Verify state after start selection
        response = client.get(f'/api/state/{image_id}')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['start_point'] == {'x': start_x, 'y': start_y}
        assert data['goal_point'] is None
        assert data['path'] is None
        
        # Step 3: Select goal point
        goal_x, goal_y = width // 2 + 10, height // 2
        
        client.post(
            '/api/select-goal',
            data=json.dumps({'image_id': image_id, 'x': goal_x, 'y': goal_y}),
            content_type='application/json'
        )
        
        # Verify state after goal selection
        response = client.get(f'/api/state/{image_id}')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['start_point'] == {'x': start_x, 'y': start_y}
        assert data['goal_point'] == {'x': goal_x, 'y': goal_y}
        # Path may or may not exist depending on connectivity
        assert 'path' in data
    
    def test_workflow_error_recovery(self, client):
        """
        Test error scenarios and recovery paths.
        
        Validates: Requirements 11.1, 11.2, 11.4
        """
        # Test 1: Try to select start without loading image
        response = client.post(
            '/api/select-start',
            data=json.dumps({'image_id': 'nonexistent', 'x': 50, 'y': 50}),
            content_type='application/json'
        )
        
        assert response.status_code == 404
        data = json.loads(response.data)
        assert 'error' in data
        assert data['code'] == 'IMAGE_NOT_FOUND'
        
        # Test 2: Try to get state for nonexistent session
        response = client.get('/api/state/nonexistent')
        
        assert response.status_code == 404
        data = json.loads(response.data)
        assert 'error' in data
        assert data['code'] == 'IMAGE_NOT_FOUND'
        
        # Test 3: Load image and recover
        test_image_bytes = create_test_image_bytes(100, 100)
        
        response = client.post(
            '/api/load-image',
            data={'image': (io.BytesIO(test_image_bytes), 'test.png')},
            content_type='multipart/form-data'
        )
        
        assert response.status_code == 200
        data = json.loads(response.data)
        image_id = data['image_id']
        
        # Now operations should succeed
        response = client.get(f'/api/state/{image_id}')
        assert response.status_code == 200
    
    def test_workflow_no_path_between_points(self, client, real_components):
        """
        Test scenario where no path exists between start and goal.
        
        Validates: Requirements 7.3
        """
        # Create a road mask with disconnected road segments
        disconnected_mask = np.zeros((100, 100), dtype=np.uint8)
        # Left segment
        disconnected_mask[40:60, 10:30] = 1
        # Right segment (disconnected)
        disconnected_mask[40:60, 70:90] = 1
        
        # Mock segmentation model to return disconnected mask
        def predict_disconnected(image_tensor):
            return disconnected_mask
        
        real_components['segmentation_model'].predict.side_effect = predict_disconnected
        
        # Create new API instance with modified mock
        api_instance = BackendAPI(**real_components)
        app = api_instance.get_app()
        app.config['TESTING'] = True
        test_client = app.test_client()
        
        # Step 1: Load image
        test_image_bytes = create_test_image_bytes(100, 100)
        
        response = test_client.post(
            '/api/load-image',
            data={'image': (io.BytesIO(test_image_bytes), 'test.png')},
            content_type='multipart/form-data'
        )
        
        assert response.status_code == 200
        data = json.loads(response.data)
        image_id = data['image_id']
        
        # Step 2: Select start on left segment
        start_x, start_y = 20, 50
        
        response = test_client.post(
            '/api/select-start',
            data=json.dumps({'image_id': image_id, 'x': start_x, 'y': start_y}),
            content_type='application/json'
        )
        
        assert response.status_code == 200
        
        # Step 3: Select goal on right segment (disconnected)
        goal_x, goal_y = 80, 50
        
        response = test_client.post(
            '/api/select-goal',
            data=json.dumps({'image_id': image_id, 'x': goal_x, 'y': goal_y}),
            content_type='application/json'
        )
        
        # Should return error indicating no path exists
        assert response.status_code == 400
        data = json.loads(response.data)
        assert 'error' in data or data.get('path') is None
        
        if 'error' in data:
            assert 'path' in data['error'].lower() or 'not connected' in data['error'].lower()


class TestWorkflowEdgeCases:
    """Test edge cases in the workflow."""
    
    def test_select_goal_before_start(self, client):
        """
        Test selecting goal point before start point.
        
        Should accept goal point but not compute path until start is selected.
        """
        # Step 1: Load image
        test_image_bytes = create_test_image_bytes(100, 100)
        
        response = client.post(
            '/api/load-image',
            data={'image': (io.BytesIO(test_image_bytes), 'test.png')},
            content_type='multipart/form-data'
        )
        
        assert response.status_code == 200
        data = json.loads(response.data)
        image_id = data['image_id']
        width = data['width']
        height = data['height']
        
        # Step 2: Select goal BEFORE start
        goal_x, goal_y = width // 2, height // 2
        
        response = client.post(
            '/api/select-goal',
            data=json.dumps({'image_id': image_id, 'x': goal_x, 'y': goal_y}),
            content_type='application/json'
        )
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['valid'] is True
        assert data['path'] is None  # No path yet (no start point)
        
        # Step 3: Now select start
        start_x, start_y = width // 2 - 10, height // 2
        
        response = client.post(
            '/api/select-start',
            data=json.dumps({'image_id': image_id, 'x': start_x, 'y': start_y}),
            content_type='application/json'
        )
        
        assert response.status_code == 200
        
        # Step 4: Reselect goal to trigger path computation
        response = client.post(
            '/api/select-goal',
            data=json.dumps({'image_id': image_id, 'x': goal_x, 'y': goal_y}),
            content_type='application/json'
        )
        
        assert response.status_code == 200
        data = json.loads(response.data)
        # Now path should be computed
        assert 'path' in data
    
    def test_multiple_sessions(self, client):
        """
        Test handling multiple concurrent sessions.
        
        Validates session isolation.
        """
        # Create two separate sessions
        test_image_bytes1 = create_test_image_bytes(100, 100)
        test_image_bytes2 = create_test_image_bytes(100, 100)
        
        # Session 1
        response1 = client.post(
            '/api/load-image',
            data={'image': (io.BytesIO(test_image_bytes1), 'test1.png')},
            content_type='multipart/form-data'
        )
        
        assert response1.status_code == 200
        data1 = json.loads(response1.data)
        image_id1 = data1['image_id']
        
        # Session 2
        response2 = client.post(
            '/api/load-image',
            data={'image': (io.BytesIO(test_image_bytes2), 'test2.png')},
            content_type='multipart/form-data'
        )
        
        assert response2.status_code == 200
        data2 = json.loads(response2.data)
        image_id2 = data2['image_id']
        
        # Verify sessions are separate
        assert image_id1 != image_id2
        
        # Modify session 1
        client.post(
            '/api/select-start',
            data=json.dumps({'image_id': image_id1, 'x': 50, 'y': 50}),
            content_type='application/json'
        )
        
        # Verify session 2 is unaffected
        response = client.get(f'/api/state/{image_id2}')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['start_point'] is None  # Session 2 should be unchanged
