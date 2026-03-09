"""
StateManager component for managing backend state.

Manages sessions for loaded images, road masks, graphs, and user selections.
Each session is identified by a unique image_id and stores all related data
for that image processing session.
"""

import logging
from typing import Dict, List, Tuple, Optional
import numpy as np

logger = logging.getLogger(__name__)


class StateManager:
    """
    Manages backend state for loaded images, graphs, and selections.
    
    Stores session data including:
    - Loaded images and metadata
    - Road masks and graphs
    - Start/goal point selections
    - Computed paths
    
    Each session is identified by a unique image_id.
    """
    
    def __init__(self):
        """Initialize StateManager with empty session storage."""
        self._sessions: Dict[str, dict] = {}
        logger.info("StateManager initialized")
    
    def create_session(
        self,
        image_id: str,
        image: np.ndarray,
        road_mask: np.ndarray,
        graph
    ) -> None:
        """
        Create a new session with image, road mask, and graph.
        
        Args:
            image_id: Unique identifier for the session
            image: Satellite image as numpy array
            road_mask: Binary road mask as numpy array
            graph: Road graph constructed from the mask
        
        Postconditions:
            - Session exists with given image_id
            - Session contains image, road_mask, and graph
            - start_point, goal_point, and path are None
        """
        self._sessions[image_id] = {
            'image': image,
            'road_mask': road_mask,
            'graph': graph,
            'start_point': None,
            'goal_point': None,
            'path': None
        }
        logger.info(f"Created session for image_id: {image_id}")
    
    def get_session(self, image_id: str) -> Optional[dict]:
        """
        Retrieve session data for given image_id.
        
        Args:
            image_id: Unique identifier for the session
        
        Returns:
            Session dictionary if exists, None otherwise
            
        Session dictionary contains:
            - image: np.ndarray
            - road_mask: np.ndarray
            - graph: Graph object
            - start_point: Optional[Tuple[int, int]]
            - goal_point: Optional[Tuple[int, int]]
            - path: Optional[List[Tuple[int, int]]]
        """
        session = self._sessions.get(image_id)
        if session is None:
            logger.warning(f"Session not found for image_id: {image_id}")
        return session
    
    def set_start_point(self, image_id: str, x: int, y: int) -> None:
        """
        Set start point for a session.
        
        Args:
            image_id: Unique identifier for the session
            x: X coordinate of start point
            y: Y coordinate of start point
        
        Preconditions:
            - Session must exist for image_id
        
        Postconditions:
            - start_point is set to (x, y)
            - path is cleared (set to None)
        
        Raises:
            KeyError: If session does not exist
        """
        if image_id not in self._sessions:
            logger.error(f"Cannot set start point: session not found for image_id: {image_id}")
            raise KeyError(f"Session not found for image_id: {image_id}")
        
        self._sessions[image_id]['start_point'] = (x, y)
        self._sessions[image_id]['path'] = None  # Clear path when start point changes
        logger.info(f"Set start point ({x}, {y}) for image_id: {image_id}")
    
    def set_goal_point(self, image_id: str, x: int, y: int) -> None:
        """
        Set goal point for a session.
        
        Args:
            image_id: Unique identifier for the session
            x: X coordinate of goal point
            y: Y coordinate of goal point
        
        Preconditions:
            - Session must exist for image_id
        
        Postconditions:
            - goal_point is set to (x, y)
            - path is cleared (set to None)
        
        Raises:
            KeyError: If session does not exist
        """
        if image_id not in self._sessions:
            logger.error(f"Cannot set goal point: session not found for image_id: {image_id}")
            raise KeyError(f"Session not found for image_id: {image_id}")
        
        self._sessions[image_id]['goal_point'] = (x, y)
        self._sessions[image_id]['path'] = None  # Clear path when goal point changes
        logger.info(f"Set goal point ({x}, {y}) for image_id: {image_id}")
    
    def set_path(self, image_id: str, path: List[Tuple[int, int]]) -> None:
        """
        Set computed path for a session.
        
        Args:
            image_id: Unique identifier for the session
            path: List of (x, y) coordinate tuples forming the path
        
        Preconditions:
            - Session must exist for image_id
        
        Postconditions:
            - path is set to the provided path
        
        Raises:
            KeyError: If session does not exist
        """
        if image_id not in self._sessions:
            logger.error(f"Cannot set path: session not found for image_id: {image_id}")
            raise KeyError(f"Session not found for image_id: {image_id}")
        
        self._sessions[image_id]['path'] = path
        logger.info(f"Set path with {len(path)} points for image_id: {image_id}")
    
    def clear_selection(self, image_id: str) -> None:
        """
        Clear start point, goal point, and path for a session.
        
        Args:
            image_id: Unique identifier for the session
        
        Preconditions:
            - Session must exist for image_id
        
        Postconditions:
            - start_point is set to None
            - goal_point is set to None
            - path is set to None
            - image, road_mask, and graph remain unchanged
        
        Raises:
            KeyError: If session does not exist
        """
        if image_id not in self._sessions:
            logger.error(f"Cannot clear selection: session not found for image_id: {image_id}")
            raise KeyError(f"Session not found for image_id: {image_id}")
        
        self._sessions[image_id]['start_point'] = None
        self._sessions[image_id]['goal_point'] = None
        self._sessions[image_id]['path'] = None
        logger.info(f"Cleared selection for image_id: {image_id}")
    
    def session_exists(self, image_id: str) -> bool:
        """
        Check if a session exists for given image_id.
        
        Args:
            image_id: Unique identifier for the session
        
        Returns:
            True if session exists, False otherwise
        """
        exists = image_id in self._sessions
        logger.debug(f"Session exists check for image_id {image_id}: {exists}")
        return exists
