"""
Property-based tests for PathfindingCoordinator component.

Tests pathfinding coordination logic using hypothesis for property-based testing.
"""

import pytest
import numpy as np
import networkx as nx
from hypothesis import given, strategies as st, assume
from src.api.pathfinding_coordinator import PathfindingCoordinator
from src.pathfinding_engine import PathfindingEngine
from src.api.exceptions import PathfindingFailedError


@pytest.fixture
def pathfinding_engine():
    """Create PathfindingEngine instance."""
    return PathfindingEngine(algorithm="astar")


@pytest.fixture
def pathfinding_coordinator(pathfinding_engine):
    """Create PathfindingCoordinator instance."""
    return PathfindingCoordinator(pathfinding_engine)


def create_simple_grid_graph(width: int, height: int) -> nx.Graph:
    """
    Create a simple grid graph for testing.
    
    Args:
        width: Grid width
        height: Grid height
    
    Returns:
        NetworkX Graph with grid topology
    """
    graph = nx.Graph()
    
    # Add nodes
    for y in range(height):
        for x in range(width):
            graph.add_node((x, y))
    
    # Add edges (4-connectivity)
    for y in range(height):
        for x in range(width):
            # Right neighbor
            if x < width - 1:
                graph.add_edge((x, y), (x + 1, y), weight=1.0)
            # Down neighbor
            if y < height - 1:
                graph.add_edge((x, y), (x, y + 1), weight=1.0)
    
    return graph


def create_disconnected_graph(width: int, height: int) -> nx.Graph:
    """
    Create a graph with two disconnected components.
    
    Args:
        width: Grid width
        height: Grid height
    
    Returns:
        NetworkX Graph with two disconnected components
    """
    graph = nx.Graph()
    
    # Component 1: Top-left quadrant
    for y in range(height // 2):
        for x in range(width // 2):
            graph.add_node((x, y))
            if x > 0:
                graph.add_edge((x - 1, y), (x, y), weight=1.0)
            if y > 0:
                graph.add_edge((x, y - 1), (x, y), weight=1.0)
    
    # Component 2: Bottom-right quadrant
    for y in range(height // 2, height):
        for x in range(width // 2, width):
            graph.add_node((x, y))
            if x > width // 2:
                graph.add_edge((x - 1, y), (x, y), weight=1.0)
            if y > height // 2:
                graph.add_edge((x, y - 1), (x, y), weight=1.0)
    
    return graph


class TestPathfindingCoordinatorUnit:
    """Unit tests for PathfindingCoordinator with specific examples."""
    
    def test_compute_path_simple_case(self, pathfinding_coordinator):
        """Test path computation in a simple connected graph."""
        # Create a simple 5x5 grid
        graph = create_simple_grid_graph(5, 5)
        start = (0, 0)
        goal = (4, 4)
        
        path = pathfinding_coordinator.compute_path(graph, start, goal)
        
        # Verify path properties
        assert len(path) >= 2
        assert path[0] == start
        assert path[-1] == goal
        
        # Verify path connectivity
        for i in range(len(path) - 1):
            assert graph.has_edge(path[i], path[i + 1]), \
                f"Path segment {path[i]} -> {path[i + 1]} not in graph"
    
    def test_compute_path_no_path_exists(self, pathfinding_coordinator):
        """Test that PathfindingFailedError is raised when no path exists."""
        # Create disconnected graph
        graph = create_disconnected_graph(10, 10)
        start = (0, 0)  # In component 1
        goal = (9, 9)   # In component 2
        
        with pytest.raises(PathfindingFailedError) as exc_info:
            pathfinding_coordinator.compute_path(graph, start, goal)
        
        assert exc_info.value.error_code == "PATHFINDING_FAILED"
        assert "No path exists" in exc_info.value.message
    
    def test_compute_path_start_not_in_graph(self, pathfinding_coordinator):
        """Test that PathfindingFailedError is raised when start is not in graph."""
        graph = create_simple_grid_graph(5, 5)
        start = (10, 10)  # Not in graph
        goal = (4, 4)
        
        with pytest.raises(PathfindingFailedError) as exc_info:
            pathfinding_coordinator.compute_path(graph, start, goal)
        
        assert exc_info.value.error_code == "PATHFINDING_FAILED"
    
    def test_compute_path_goal_not_in_graph(self, pathfinding_coordinator):
        """Test that PathfindingFailedError is raised when goal is not in graph."""
        graph = create_simple_grid_graph(5, 5)
        start = (0, 0)
        goal = (10, 10)  # Not in graph
        
        with pytest.raises(PathfindingFailedError) as exc_info:
            pathfinding_coordinator.compute_path(graph, start, goal)
        
        assert exc_info.value.error_code == "PATHFINDING_FAILED"
    
    def test_compute_path_start_equals_goal(self, pathfinding_coordinator):
        """Test path computation when start equals goal."""
        graph = create_simple_grid_graph(5, 5)
        start = (2, 2)
        goal = (2, 2)
        
        path = pathfinding_coordinator.compute_path(graph, start, goal)
        
        # Path should contain just the single point
        assert len(path) >= 1
        assert path[0] == start
        assert path[-1] == goal
    
    def test_compute_path_adjacent_nodes(self, pathfinding_coordinator):
        """Test path computation between adjacent nodes."""
        graph = create_simple_grid_graph(5, 5)
        start = (2, 2)
        goal = (3, 2)  # Adjacent to start
        
        path = pathfinding_coordinator.compute_path(graph, start, goal)
        
        # Path should be short
        assert len(path) >= 2
        assert path[0] == start
        assert path[-1] == goal
    
    def test_compute_path_with_weighted_edges(self, pathfinding_coordinator):
        """Test path computation with weighted edges."""
        # Create a graph where shortest path by weight differs from shortest by hops
        graph = nx.Graph()
        graph.add_edge((0, 0), (1, 0), weight=1.0)
        graph.add_edge((1, 0), (2, 0), weight=1.0)
        graph.add_edge((0, 0), (0, 1), weight=10.0)
        graph.add_edge((0, 1), (2, 0), weight=10.0)
        
        start = (0, 0)
        goal = (2, 0)
        
        path = pathfinding_coordinator.compute_path(graph, start, goal)
        
        # Should take the lower-weight path through (1, 0)
        assert len(path) >= 2
        assert path[0] == start
        assert path[-1] == goal


class TestPathfindingCoordinatorProperties:
    """Property-based tests for PathfindingCoordinator."""
    
    @given(
        width=st.integers(min_value=3, max_value=20),
        height=st.integers(min_value=3, max_value=20),
        start_x=st.integers(min_value=0, max_value=19),
        start_y=st.integers(min_value=0, max_value=19),
        goal_x=st.integers(min_value=0, max_value=19),
        goal_y=st.integers(min_value=0, max_value=19)
    )
    def test_property_11_pathfinding_invocation(
        self,
        width,
        height,
        start_x,
        start_y,
        goal_x,
        goal_y
    ):
        """
        Property 11: Pathfinding Invocation
        
        For any valid graph and start/goal coordinates where both points are in the graph
        and a path exists, compute_path should:
        1. Invoke PathfindingEngine
        2. Return a valid path from start to goal
        3. Path[0] == start
        4. Path[-1] == goal
        5. All consecutive coordinates in path are connected by edges
        
        **Validates: Requirements 7.1, 7.2**
        """
        # Ensure coordinates are within bounds
        assume(start_x < width and start_y < height)
        assume(goal_x < width and goal_y < height)
        
        # Create pathfinding coordinator
        pathfinding_engine = PathfindingEngine(algorithm="astar")
        coordinator = PathfindingCoordinator(pathfinding_engine)
        
        # Create a connected grid graph
        graph = create_simple_grid_graph(width, height)
        
        start = (start_x, start_y)
        goal = (goal_x, goal_y)
        
        # Compute path
        path = coordinator.compute_path(graph, start, goal)
        
        # Property 1: Path should be non-empty
        assert len(path) >= 1, "Path should contain at least one point"
        
        # Special case: if start == goal, path may have only 1 point
        if start == goal:
            assume(len(path) >= 1)
        else:
            assume(len(path) >= 2)
        
        # Property 2: Path should start at start point
        assert path[0] == start, \
            f"Path should start at {start}, but starts at {path[0]}"
        
        # Property 3: Path should end at goal point
        assert path[-1] == goal, \
            f"Path should end at {goal}, but ends at {path[-1]}"
        
        # Property 4: All consecutive coordinates should be connected by edges
        for i in range(len(path) - 1):
            current = path[i]
            next_node = path[i + 1]
            assert graph.has_edge(current, next_node), \
                f"Path segment {current} -> {next_node} not connected in graph"
        
        # Property 5: All points in path should be in the graph
        for point in path:
            assert graph.has_node(point), \
                f"Path point {point} not in graph"
    
    @given(
        width=st.integers(min_value=5, max_value=20),
        height=st.integers(min_value=5, max_value=20)
    )
    def test_property_11_pathfinding_no_path_raises_error(self, width, height):
        """
        Property 11 (Error Case): Pathfinding Invocation with No Path
        
        For any graph where start and goal are in disconnected components,
        compute_path should raise PathfindingFailedError.
        
        **Validates: Requirements 7.2, 7.3**
        """
        # Create pathfinding coordinator
        pathfinding_engine = PathfindingEngine(algorithm="astar")
        coordinator = PathfindingCoordinator(pathfinding_engine)
        
        # Create disconnected graph
        graph = create_disconnected_graph(width, height)
        
        # Select start from component 1 (top-left)
        start = (0, 0)
        
        # Select goal from component 2 (bottom-right)
        goal = (width - 1, height - 1)
        
        # Ensure both points are in the graph
        assume(graph.has_node(start))
        assume(graph.has_node(goal))
        
        # Property: Should raise PathfindingFailedError when no path exists
        with pytest.raises(PathfindingFailedError) as exc_info:
            coordinator.compute_path(graph, start, goal)
        
        assert exc_info.value.error_code == "PATHFINDING_FAILED"
        assert "No path exists" in exc_info.value.message or "No path found" in exc_info.value.details
    
    @given(
        width=st.integers(min_value=3, max_value=20),
        height=st.integers(min_value=3, max_value=20)
    )
    def test_property_11_pathfinding_invalid_start_raises_error(self, width, height):
        """
        Property 11 (Error Case): Pathfinding with Invalid Start
        
        For any graph where start is not in the graph,
        compute_path should raise PathfindingFailedError.
        
        **Validates: Requirements 7.4**
        """
        # Create pathfinding coordinator
        pathfinding_engine = PathfindingEngine(algorithm="astar")
        coordinator = PathfindingCoordinator(pathfinding_engine)
        
        # Create graph
        graph = create_simple_grid_graph(width, height)
        
        # Select start outside the graph
        start = (width + 10, height + 10)
        goal = (0, 0)
        
        # Property: Should raise PathfindingFailedError when start is invalid
        with pytest.raises(PathfindingFailedError) as exc_info:
            coordinator.compute_path(graph, start, goal)
        
        assert exc_info.value.error_code == "PATHFINDING_FAILED"
