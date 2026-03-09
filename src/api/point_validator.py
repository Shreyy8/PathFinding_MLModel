"""
Point validation module for the Interactive Road Mapping Interface.

This module provides functionality to validate that user-selected coordinates
lie on road pixels in the segmented road mask.
"""

import numpy as np


class PointValidator:
    """
    Validates that click coordinates lie on road pixels.
    
    The PointValidator checks if given (x, y) coordinates are within the bounds
    of the road mask and correspond to a road pixel (mask value > 0).
    """
    
    def validate_point(self, road_mask: np.ndarray, x: int, y: int) -> bool:
        """
        Validate that point (x, y) lies on a road pixel.
        
        Args:
            road_mask: Binary mask where road pixels have value > 0
            x: X-coordinate (horizontal position, increases to the right)
            y: Y-coordinate (vertical position, increases downward)
        
        Returns:
            True if the point is within bounds and on a road pixel, False otherwise
        
        Preconditions:
            - road_mask is a valid numpy array (0 or 255 values for binary masks)
            - x and y are integers
        
        Postconditions:
            - Returns True if and only if:
              - 0 <= x < road_mask.shape[1] (width)
              - 0 <= y < road_mask.shape[0] (height)
              - road_mask[y, x] > 0 (road pixel)
            - Returns False otherwise
        """
        # Check if coordinates are within image bounds
        height, width = road_mask.shape[:2]  # Handle both 2D and 3D arrays
        
        if x < 0 or x >= width or y < 0 or y >= height:
            return False
        
        # Check if the pixel at (x, y) is a road pixel (value > 0)
        # Note: numpy arrays are indexed as [row, column] which is [y, x]
        pixel_value = road_mask[y, x]
        
        # For multi-channel images, check if any channel has value > 0
        if isinstance(pixel_value, np.ndarray):
            return np.any(pixel_value > 0)
        
        return pixel_value > 0
