"""
PathfindingCoordinator: Coordinate pathfinding execution and handle errors.

This module provides a coordination layer between the API and the PathfindingEngine,
handling error cases and converting path formats for API responses.
"""

from typing import List, Tuple
import logging
from src.pathfinding_engine import PathfindingEngine
from src.api.exceptions import PathfindingFailedError
import networkx as nx

logger = logging.getLogger(__name__)


class PathfindingCoordinator:
    """
    Coordinate pathfinding execution and handle errors.
    
    This class wraps the PathfindingEngine to provide error handling and
    format conversion suitable for the API layer.
    
    Attributes:
        pathfinding_engine: PathfindingEngine instance for computing paths
    """
    
    def __init__(self, pathfinding_engine: PathfindingEngine):
        """
        Initialize PathfindingCoordinator.
        
        Args:
            pathfinding_engine: PathfindingEngine instance to use for pathfinding
        """
        self.pathfinding_engine = pathfinding_engine
        logger.info("PathfindingCoordinator initialized")
    
    def compute_path(
        self,
        graph: nx.Graph,
        start: Tuple[int, int],
        goal: Tuple[int, int]
    ) -> List[Tuple[int, int]]:
        """
        Compute shortest path between start and goal.
        
        Invokes the PathfindingEngine to compute the shortest path and handles
        errors appropriately. Converts the path result to a list of (x, y)
        coordinate tuples suitable for API responses.
        
        Args:
            graph: NetworkX Graph representing the road network
            start: Starting coordinate (x, y)
            goal: Goal coordinate (x, y)
        
        Returns:
            List of (x, y) coordinate tuples forming path from start to goal.
            Path[0] == start, Path[-1] == goal.
        
        Raises:
            PathfindingFailedError: If no path exists or pathfinding fails
        
        Preconditions:
            - graph is a valid road graph
            - start and goal are valid coordinates on road pixels
        
        Postconditions:
            - Returns list of (x, y) coordinates forming path from start to goal
            - Path[0] == start
            - Path[-1] == goal
            - All intermediate points are on roads
            - Raises PathfindingFailedError if no path exists
        """
        try:
            logger.info(f"Computing path from {start} to {goal}")
            
            # Invoke PathfindingEngine
            path = self.pathfinding_engine.find_path(graph, start, goal)
            
            # Check if path was found
            if path is None:
                logger.warning(f"No path found from {start} to {goal}")
                raise PathfindingFailedError(
                    message="No path exists between start and goal",
                    details=f"No path found from {start} to {goal}. Points may be in disconnected road segments.",
                    status_code=400
                )
            
            # Validate path result
            if len(path) < 1:
                logger.error(f"Invalid path result: path has {len(path)} points")
                raise PathfindingFailedError(
                    message="Invalid path result",
                    details=f"Path must have at least 1 point, got {len(path)}"
                )
            
            if path[0] != start:
                logger.error(f"Path does not start at start point: {path[0]} != {start}")
                raise PathfindingFailedError(
                    message="Invalid path result",
                    details=f"Path does not start at start point"
                )
            
            if path[-1] != goal:
                logger.error(f"Path does not end at goal point: {path[-1]} != {goal}")
                raise PathfindingFailedError(
                    message="Invalid path result",
                    details=f"Path does not end at goal point"
                )
            
            logger.info(f"Path computed successfully with {len(path)} waypoints")
            return path
            
        except ValueError as e:
            # Handle PathfindingEngine ValueError (start/goal not in graph)
            logger.error(f"PathfindingEngine ValueError: {str(e)}")
            raise PathfindingFailedError(
                message="Pathfinding failed",
                details=str(e),
                status_code=400
            )
        except PathfindingFailedError:
            # Re-raise our own exceptions
            raise
        except Exception as e:
            # Handle unexpected errors
            logger.error(f"Unexpected error during pathfinding: {str(e)}", exc_info=True)
            raise PathfindingFailedError(
                message="Pathfinding failed due to unexpected error",
                details=str(e)
            )
