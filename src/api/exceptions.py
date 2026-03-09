"""
Custom exception classes for API error handling.

Defines exception hierarchy for different error scenarios in the backend API.
Each exception maps to specific HTTP status codes and error codes.
"""

import logging

logger = logging.getLogger(__name__)


class APIException(Exception):
    """Base exception class for all API errors."""
    
    def __init__(self, message: str, error_code: str, status_code: int = 500, details: str = None):
        """
        Initialize API exception.
        
        Args:
            message: Brief error message
            error_code: Error code identifier
            status_code: HTTP status code (default: 500)
            details: Additional error details (optional)
        """
        super().__init__(message)
        self.message = message
        self.error_code = error_code
        self.status_code = status_code
        self.details = details or message
        
        # Log the error
        logger.error(f"{error_code}: {message} - {details}")
    
    def to_dict(self):
        """Convert exception to dictionary for JSON response."""
        return {
            "error": self.message,
            "code": self.error_code,
            "details": self.details
        }


class InvalidImageError(APIException):
    """Raised when image format or size is invalid."""
    
    def __init__(self, message: str = "Invalid image file", details: str = None):
        super().__init__(
            message=message,
            error_code="INVALID_IMAGE",
            status_code=400,
            details=details
        )


class SegmentationFailedError(APIException):
    """Raised when road segmentation fails."""
    
    def __init__(self, message: str = "Road segmentation failed", details: str = None):
        super().__init__(
            message=message,
            error_code="SEGMENTATION_FAILED",
            status_code=500,
            details=details
        )


class GraphConstructionFailedError(APIException):
    """Raised when graph construction fails."""
    
    def __init__(self, message: str = "Graph construction failed", details: str = None):
        super().__init__(
            message=message,
            error_code="GRAPH_CONSTRUCTION_FAILED",
            status_code=500,
            details=details
        )


class PointNotOnRoadError(APIException):
    """Raised when selected point is not on a road."""
    
    def __init__(self, message: str = "Point is not on a road", details: str = None):
        super().__init__(
            message=message,
            error_code="POINT_NOT_ON_ROAD",
            status_code=400,
            details=details
        )


class PathfindingFailedError(APIException):
    """Raised when pathfinding computation fails."""
    
    def __init__(self, message: str = "Pathfinding failed", details: str = None, status_code: int = 500):
        super().__init__(
            message=message,
            error_code="PATHFINDING_FAILED",
            status_code=status_code,
            details=details
        )


class ImageNotFoundError(APIException):
    """Raised when image_id is not found in state."""
    
    def __init__(self, message: str = "Image not found", details: str = None):
        super().__init__(
            message=message,
            error_code="IMAGE_NOT_FOUND",
            status_code=404,
            details=details
        )


class InvalidCoordinatesError(APIException):
    """Raised when coordinates are out of bounds."""
    
    def __init__(self, message: str = "Invalid coordinates", details: str = None):
        super().__init__(
            message=message,
            error_code="INVALID_COORDINATES",
            status_code=400,
            details=details
        )
