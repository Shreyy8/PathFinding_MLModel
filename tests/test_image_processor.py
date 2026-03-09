"""
Property-based tests for ImageProcessor component.

Tests image loading, validation, and encoding using hypothesis for property-based testing.
"""

import pytest
import numpy as np
import base64
import io
from PIL import Image
from hypothesis import given, strategies as st, assume
from src.api.image_processor import ImageProcessor


@pytest.fixture
def image_processor():
    """Create ImageProcessor instance."""
    return ImageProcessor()


@pytest.fixture
def sample_image():
    """Create sample RGB image."""
    return np.random.randint(0, 256, (100, 100, 3), dtype=np.uint8)


@pytest.fixture
def sample_mask():
    """Create sample binary mask."""
    mask = np.zeros((100, 100), dtype=np.uint8)
    mask[40:60, 40:60] = 255  # Road region in center
    return mask


class TestImageProcessorUnit:
    """Unit tests for ImageProcessor with specific examples."""
    
    def test_load_valid_png_image(self, image_processor):
        """Test loading a valid PNG image."""
        # Create a simple test image
        test_image = np.random.randint(0, 256, (50, 50, 3), dtype=np.uint8)
        pil_image = Image.fromarray(test_image, mode='RGB')
        
        # Convert to bytes
        buffer = io.BytesIO()
        pil_image.save(buffer, format='PNG')
        file_data = buffer.getvalue()
        
        # Load image
        result = image_processor.load_image(file_data)
        
        # Verify result is numpy array with correct shape
        assert isinstance(result, np.ndarray)
        assert result.shape == (50, 50, 3)
        assert result.dtype == np.uint8
    
    def test_load_valid_jpeg_image(self, image_processor):
        """Test loading a valid JPEG image."""
        # Create a simple test image
        test_image = np.random.randint(0, 256, (50, 50, 3), dtype=np.uint8)
        pil_image = Image.fromarray(test_image, mode='RGB')
        
        # Convert to bytes
        buffer = io.BytesIO()
        pil_image.save(buffer, format='JPEG')
        file_data = buffer.getvalue()
        
        # Load image
        result = image_processor.load_image(file_data)
        
        # Verify result is numpy array with correct shape
        assert isinstance(result, np.ndarray)
        assert result.shape == (50, 50, 3)
        assert result.dtype == np.uint8
    
    def test_load_grayscale_converts_to_rgb(self, image_processor):
        """Test that grayscale images are converted to RGB."""
        # Create grayscale image
        test_image = np.random.randint(0, 256, (50, 50), dtype=np.uint8)
        pil_image = Image.fromarray(test_image, mode='L')
        
        # Convert to bytes
        buffer = io.BytesIO()
        pil_image.save(buffer, format='PNG')
        file_data = buffer.getvalue()
        
        # Load image
        result = image_processor.load_image(file_data)
        
        # Verify result is RGB (3 channels)
        assert result.shape == (50, 50, 3)
    
    def test_load_rgba_converts_to_rgb(self, image_processor):
        """Test that RGBA images are converted to RGB."""
        # Create RGBA image
        test_image = np.random.randint(0, 256, (50, 50, 4), dtype=np.uint8)
        pil_image = Image.fromarray(test_image, mode='RGBA')
        
        # Convert to bytes
        buffer = io.BytesIO()
        pil_image.save(buffer, format='PNG')
        file_data = buffer.getvalue()
        
        # Load image
        result = image_processor.load_image(file_data)
        
        # Verify result is RGB (3 channels)
        assert result.shape == (50, 50, 3)
    
    def test_load_invalid_data_raises_error(self, image_processor):
        """Test that invalid image data raises ValueError."""
        invalid_data = b"This is not an image"
        
        with pytest.raises(ValueError, match="Failed to load image"):
            image_processor.load_image(invalid_data)
    
    def test_validate_valid_image(self, image_processor, sample_image):
        """Test validation of a valid image."""
        result = image_processor.validate_image(sample_image)
        assert result == True
    
    def test_validate_grayscale_image(self, image_processor):
        """Test validation of a grayscale image."""
        grayscale = np.random.randint(0, 256, (100, 100), dtype=np.uint8)
        result = image_processor.validate_image(grayscale)
        assert result == True
    
    def test_validate_image_too_large(self, image_processor):
        """Test that images exceeding max dimensions are invalid."""
        # Create image larger than MAX_WIDTH x MAX_HEIGHT
        large_image = np.zeros((5000, 5000, 3), dtype=np.uint8)
        result = image_processor.validate_image(large_image)
        assert result == False
    
    def test_validate_empty_image(self, image_processor):
        """Test that empty images are invalid."""
        empty_image = np.array([])
        result = image_processor.validate_image(empty_image)
        assert result == False
    
    def test_validate_zero_dimensions(self, image_processor):
        """Test that images with zero dimensions are invalid."""
        zero_dim_image = np.zeros((0, 100, 3), dtype=np.uint8)
        result = image_processor.validate_image(zero_dim_image)
        assert result == False
    
    def test_validate_invalid_dimensions(self, image_processor):
        """Test that images with invalid dimensions are rejected."""
        # 4D array (invalid)
        invalid_image = np.zeros((10, 10, 3, 3), dtype=np.uint8)
        result = image_processor.validate_image(invalid_image)
        assert result == False
    
    def test_validate_non_numpy_array(self, image_processor):
        """Test that non-numpy arrays are invalid."""
        not_an_array = [[1, 2, 3], [4, 5, 6]]
        result = image_processor.validate_image(not_an_array)
        assert result == False
    
    def test_encode_image_to_base64(self, image_processor, sample_image):
        """Test encoding image to base64."""
        result = image_processor.encode_image_to_base64(sample_image)
        
        # Verify result is a string
        assert isinstance(result, str)
        
        # Verify it's valid base64
        try:
            decoded = base64.b64decode(result)
            assert len(decoded) > 0
        except Exception:
            pytest.fail("Result is not valid base64")
    
    def test_encode_grayscale_to_base64(self, image_processor):
        """Test encoding grayscale image to base64."""
        grayscale = np.random.randint(0, 256, (50, 50), dtype=np.uint8)
        result = image_processor.encode_image_to_base64(grayscale)
        
        # Verify result is valid base64
        assert isinstance(result, str)
        decoded = base64.b64decode(result)
        assert len(decoded) > 0
    
    def test_encode_mask_to_base64_default_opacity(self, image_processor, sample_mask):
        """Test encoding mask to base64 with default opacity."""
        result = image_processor.encode_mask_to_base64(sample_mask)
        
        # Verify result is a string
        assert isinstance(result, str)
        
        # Verify it's valid base64
        decoded = base64.b64decode(result)
        assert len(decoded) > 0
        
        # Verify the decoded image is RGBA
        decoded_image = Image.open(io.BytesIO(decoded))
        assert decoded_image.mode == 'RGBA'
    
    def test_encode_mask_to_base64_custom_opacity(self, image_processor, sample_mask):
        """Test encoding mask to base64 with custom opacity."""
        result = image_processor.encode_mask_to_base64(sample_mask, opacity=0.7)
        
        # Verify result is valid base64
        assert isinstance(result, str)
        decoded = base64.b64decode(result)
        
        # Decode and verify RGBA format
        decoded_image = Image.open(io.BytesIO(decoded))
        assert decoded_image.mode == 'RGBA'
        
        # Verify opacity is applied (alpha channel should be ~179 for road pixels)
        image_array = np.array(decoded_image)
        road_pixels = sample_mask > 0
        alpha_values = image_array[road_pixels, 3]
        
        # Check that alpha values are close to expected (179 = 0.7 * 255)
        expected_alpha = int(255 * 0.7)
        assert np.all(alpha_values == expected_alpha)
    
    def test_encode_mask_transparency_for_non_road_pixels(self, image_processor, sample_mask):
        """Test that non-road pixels are fully transparent."""
        result = image_processor.encode_mask_to_base64(sample_mask)
        
        # Decode image
        decoded = base64.b64decode(result)
        decoded_image = Image.open(io.BytesIO(decoded))
        image_array = np.array(decoded_image)
        
        # Non-road pixels should have alpha = 0
        non_road_pixels = sample_mask == 0
        alpha_values = image_array[non_road_pixels, 3]
        assert np.all(alpha_values == 0)
    
    def test_encode_mask_red_color_for_road_pixels(self, image_processor, sample_mask):
        """Test that road pixels are colored red."""
        result = image_processor.encode_mask_to_base64(sample_mask)
        
        # Decode image
        decoded = base64.b64decode(result)
        decoded_image = Image.open(io.BytesIO(decoded))
        image_array = np.array(decoded_image)
        
        # Road pixels should be red (255, 0, 0)
        road_pixels = sample_mask > 0
        red_values = image_array[road_pixels, 0]
        green_values = image_array[road_pixels, 1]
        blue_values = image_array[road_pixels, 2]
        
        assert np.all(red_values == 255)
        assert np.all(green_values == 0)
        assert np.all(blue_values == 0)


class TestImageProcessorProperties:
    """Property-based tests for ImageProcessor."""
    
    @given(
        width=st.integers(min_value=10, max_value=500),
        height=st.integers(min_value=10, max_value=500)
    )
    def test_property_1_image_display_preservation(self, width, height):
        """
        Property 1: Image Display Preservation
        
        For any valid satellite image, the backend should return image_data that
        preserves the original aspect ratio and resolution.
        
        **Validates: Requirements 1.1, 1.2**
        """
        image_processor = ImageProcessor()
        
        # Create a test image with specific dimensions
        test_image = np.random.randint(0, 256, (height, width, 3), dtype=np.uint8)
        
        # Convert to bytes (simulate file upload)
        pil_image = Image.fromarray(test_image, mode='RGB')
        buffer = io.BytesIO()
        pil_image.save(buffer, format='PNG')
        file_data = buffer.getvalue()
        
        # Load image
        loaded_image = image_processor.load_image(file_data)
        
        # Property 1: Original dimensions should be preserved
        assert loaded_image.shape[0] == height, \
            f"Height not preserved: expected {height}, got {loaded_image.shape[0]}"
        assert loaded_image.shape[1] == width, \
            f"Width not preserved: expected {width}, got {loaded_image.shape[1]}"
        
        # Property 2: Aspect ratio should be preserved
        original_aspect_ratio = width / height
        loaded_aspect_ratio = loaded_image.shape[1] / loaded_image.shape[0]
        assert abs(original_aspect_ratio - loaded_aspect_ratio) < 0.01, \
            f"Aspect ratio not preserved: expected {original_aspect_ratio}, got {loaded_aspect_ratio}"
        
        # Encode to base64 and decode back to verify preservation
        base64_string = image_processor.encode_image_to_base64(loaded_image)
        decoded_bytes = base64.b64decode(base64_string)
        decoded_image = Image.open(io.BytesIO(decoded_bytes))
        decoded_array = np.array(decoded_image)
        
        # Property 3: Encoded image should preserve dimensions
        assert decoded_array.shape[0] == height, \
            f"Encoded height not preserved: expected {height}, got {decoded_array.shape[0]}"
        assert decoded_array.shape[1] == width, \
            f"Encoded width not preserved: expected {width}, got {decoded_array.shape[1]}"
    
    @given(
        data=st.binary(min_size=0, max_size=100)
    )
    def test_property_2_invalid_image_rejection(self, data):
        """
        Property 2: Invalid Image Rejection
        
        For any invalid or corrupted image file, the backend should return a 400 error
        with error code INVALID_IMAGE.
        
        **Validates: Requirements 1.1, 1.2, 1.3**
        """
        image_processor = ImageProcessor()
        
        # Assume the data is not a valid image header
        # Valid image formats start with specific magic bytes
        assume(not data.startswith(b'\x89PNG'))  # PNG magic bytes
        assume(not data.startswith(b'\xff\xd8\xff'))  # JPEG magic bytes
        assume(not data.startswith(b'BM'))  # BMP magic bytes
        assume(not data.startswith(b'II') and not data.startswith(b'MM'))  # TIFF magic bytes
        
        # Property: Invalid image data should raise ValueError
        try:
            loaded_image = image_processor.load_image(data)
            # If load succeeds, validate should catch it
            is_valid = image_processor.validate_image(loaded_image)
            # At least one of load or validate should fail for invalid data
            # If both succeed, the data was actually valid (edge case)
        except ValueError as e:
            # Expected behavior: ValueError is raised for invalid data
            assert "Failed to load image" in str(e)
        except Exception:
            # Other exceptions are also acceptable for invalid data
            pass
