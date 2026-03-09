"""
Image processing module for the Interactive Road Mapping Interface.

This module provides functionality to load, validate, and encode images
for API responses in the backend integration layer.
"""

import base64
import io
import numpy as np
from PIL import Image
from typing import Optional


class ImageProcessor:
    """
    Handles image loading, validation, and encoding for API responses.
    
    The ImageProcessor converts uploaded file bytes to numpy arrays, validates
    image format and size, and encodes images/masks to base64 for transmission
    to the frontend.
    """
    
    # Maximum image dimensions (width x height)
    MAX_WIDTH = 4096
    MAX_HEIGHT = 4096
    
    # Supported image formats
    SUPPORTED_FORMATS = {'PNG', 'JPEG', 'JPG', 'BMP', 'TIFF'}
    
    def load_image(self, file_data: bytes) -> np.ndarray:
        """
        Convert uploaded file bytes to numpy array.
        
        Args:
            file_data: Raw bytes from uploaded image file
        
        Returns:
            Numpy array representation of the image in RGB format
        
        Raises:
            ValueError: If the file cannot be opened or is not a valid image
        
        Postconditions:
            - Returns numpy array with shape (height, width, 3) for RGB images
            - Image is converted to RGB if it was in a different mode
        """
        try:
            # Open image from bytes
            image = Image.open(io.BytesIO(file_data))
            
            # Convert to RGB if necessary (handles RGBA, grayscale, etc.)
            if image.mode != 'RGB':
                image = image.convert('RGB')
            
            # Convert to numpy array
            image_array = np.array(image)
            
            return image_array
            
        except Exception as e:
            raise ValueError(f"Failed to load image: {str(e)}")
    
    def validate_image(self, image: np.ndarray) -> bool:
        """
        Check if image format and size are valid.
        
        Args:
            image: Numpy array representation of the image
        
        Returns:
            True if image is valid, False otherwise
        
        Postconditions:
            - Returns True if and only if:
              - Image is a valid numpy array
              - Image has 2 or 3 dimensions
              - Image dimensions are within MAX_WIDTH x MAX_HEIGHT
              - Image has non-zero dimensions
            - Returns False otherwise
        """
        # Check if image is a valid numpy array
        if not isinstance(image, np.ndarray):
            return False
        
        # Check if image has valid dimensions (2D grayscale or 3D RGB)
        if image.ndim not in [2, 3]:
            return False
        
        # Check if image has non-zero dimensions
        if image.size == 0:
            return False
        
        # Get image dimensions
        height, width = image.shape[:2]
        
        # Check if dimensions are within limits
        if width <= 0 or height <= 0:
            return False
        
        if width > self.MAX_WIDTH or height > self.MAX_HEIGHT:
            return False
        
        return True
    
    def encode_image_to_base64(self, image: np.ndarray) -> str:
        """
        Encode image to base64 string for API response.
        
        Args:
            image: Numpy array representation of the image
        
        Returns:
            Base64-encoded string of the image in PNG format
        
        Postconditions:
            - Returns base64 string that can be used in data URLs
            - Image is encoded as PNG to preserve quality
        """
        # Convert numpy array to PIL Image
        if image.ndim == 2:
            # Grayscale image
            pil_image = Image.fromarray(image, mode='L')
        elif image.ndim == 3 and image.shape[2] == 3:
            # RGB image
            pil_image = Image.fromarray(image, mode='RGB')
        elif image.ndim == 3 and image.shape[2] == 4:
            # RGBA image
            pil_image = Image.fromarray(image, mode='RGBA')
        else:
            raise ValueError(f"Unsupported image shape: {image.shape}")
        
        # Encode to PNG in memory
        buffer = io.BytesIO()
        pil_image.save(buffer, format='PNG')
        buffer.seek(0)
        
        # Encode to base64
        base64_string = base64.b64encode(buffer.read()).decode('utf-8')
        
        return base64_string
    
    def encode_mask_to_base64(self, mask: np.ndarray, opacity: float = 0.5) -> str:
        """
        Encode mask to base64 with transparency overlay.
        
        Args:
            mask: Binary mask where road pixels have value > 0
            opacity: Transparency level (0.0 = fully transparent, 1.0 = fully opaque)
        
        Returns:
            Base64-encoded string of the mask as RGBA PNG with transparency
        
        Postconditions:
            - Returns base64 string with RGBA image
            - Road pixels (mask > 0) are colored with specified opacity
            - Non-road pixels are fully transparent
            - Default color is red (255, 0, 0) for road pixels
        """
        # Ensure opacity is in valid range
        opacity = max(0.0, min(1.0, opacity))
        
        # Get mask dimensions
        height, width = mask.shape[:2]
        
        # Create RGBA image (Red, Green, Blue, Alpha)
        rgba_image = np.zeros((height, width, 4), dtype=np.uint8)
        
        # Determine which pixels are roads (handle both 2D and 3D masks)
        if mask.ndim == 2:
            road_pixels = mask > 0
        else:
            # For multi-channel masks, check if any channel has value > 0
            road_pixels = np.any(mask > 0, axis=2)
        
        # Set road pixels to red with specified opacity
        rgba_image[road_pixels] = [255, 0, 0, int(255 * opacity)]
        
        # Non-road pixels remain [0, 0, 0, 0] (fully transparent)
        
        # Convert to PIL Image
        pil_image = Image.fromarray(rgba_image, mode='RGBA')
        
        # Encode to PNG in memory
        buffer = io.BytesIO()
        pil_image.save(buffer, format='PNG')
        buffer.seek(0)
        
        # Encode to base64
        base64_string = base64.b64encode(buffer.read()).decode('utf-8')
        
        return base64_string
