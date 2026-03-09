"""
Property-based tests for PointValidator component.

Tests point validation logic using hypothesis for property-based testing.
"""

import pytest
import numpy as np
from hypothesis import given, strategies as st, assume
from src.api.point_validator import PointValidator


@pytest.fixture
def point_validator():
    """Create PointValidator instance."""
    return PointValidator()


@pytest.fixture
def sample_road_mask():
    """Create sample road mask with known road region."""
    mask = np.zeros((100, 100), dtype=np.uint8)
    mask[40:60, 40:60] = 255  # Road region in center
    return mask


class TestPointValidatorUnit:
    """Unit tests for PointValidator with specific examples."""
    
    def test_valid_point_on_road(self, point_validator, sample_road_mask):
        """Test that a point on a road pixel is validated as True."""
        # Point (50, 50) is in the road region [40:60, 40:60]
        result = point_validator.validate_point(sample_road_mask, 50, 50)
        assert result == True
    
    def test_invalid_point_off_road(self, point_validator, sample_road_mask):
        """Test that a point off a road pixel is validated as False."""
        # Point (10, 10) is outside the road region
        result = point_validator.validate_point(sample_road_mask, 10, 10)
        assert result == False
    
    def test_point_out_of_bounds_negative(self, point_validator, sample_road_mask):
        """Test that negative coordinates are rejected."""
        result = point_validator.validate_point(sample_road_mask, -1, 50)
        assert result == False
        
        result = point_validator.validate_point(sample_road_mask, 50, -1)
        assert result == False
    
    def test_point_out_of_bounds_exceeds_dimensions(self, point_validator, sample_road_mask):
        """Test that coordinates exceeding image dimensions are rejected."""
        result = point_validator.validate_point(sample_road_mask, 100, 50)
        assert result == False
        
        result = point_validator.validate_point(sample_road_mask, 50, 100)
        assert result == False
    
    def test_point_at_boundary_valid(self, point_validator, sample_road_mask):
        """Test points at the boundary of the road region."""
        # Point (40, 40) is at the start of the road region
        result = point_validator.validate_point(sample_road_mask, 40, 40)
        assert result == True
        
        # Point (59, 59) is at the end of the road region (inclusive)
        result = point_validator.validate_point(sample_road_mask, 59, 59)
        assert result == True
    
    def test_point_at_boundary_invalid(self, point_validator, sample_road_mask):
        """Test points just outside the road region boundary."""
        # Point (39, 50) is just before the road region
        result = point_validator.validate_point(sample_road_mask, 39, 50)
        assert result == False
        
        # Point (60, 50) is just after the road region
        result = point_validator.validate_point(sample_road_mask, 60, 50)
        assert result == False
    
    def test_point_at_image_corner(self, point_validator, sample_road_mask):
        """Test points at image corners."""
        # Top-left corner (0, 0) - not on road
        result = point_validator.validate_point(sample_road_mask, 0, 0)
        assert result == False
        
        # Bottom-right corner (99, 99) - not on road
        result = point_validator.validate_point(sample_road_mask, 99, 99)
        assert result == False
    
    def test_multichannel_road_mask(self, point_validator):
        """Test validation with multi-channel (RGB) road mask."""
        # Create RGB road mask
        mask = np.zeros((100, 100, 3), dtype=np.uint8)
        mask[40:60, 40:60, 0] = 255  # Red channel has road
        
        # Point on road should be valid
        result = point_validator.validate_point(mask, 50, 50)
        assert result == True
        
        # Point off road should be invalid
        result = point_validator.validate_point(mask, 10, 10)
        assert result == False


class TestPointValidatorProperties:
    """Property-based tests for PointValidator."""
    
    @given(
        width=st.integers(min_value=10, max_value=500),
        height=st.integers(min_value=10, max_value=500),
        x=st.integers(min_value=-10, max_value=510),
        y=st.integers(min_value=-10, max_value=510)
    )
    def test_property_6_point_validation(self, width, height, x, y):
        """
        Property 6: Point Validation
        
        For any coordinates (x, y) and road mask, validate_point should check:
        1. Coordinates are within image bounds
        2. Coordinates correspond to road pixel (mask value > 0)
        
        **Validates: Requirements 5.2, 6.2**
        """
        point_validator = PointValidator()
        
        # Create a road mask with some road pixels
        road_mask = np.zeros((height, width), dtype=np.uint8)
        # Add a road region in the center
        if height > 4 and width > 4:
            road_mask[2:height-2, 2:width-2] = 255
        
        result = point_validator.validate_point(road_mask, x, y)
        
        # Property: result should be True if and only if:
        # 1. Point is within bounds
        # 2. Point is on a road pixel
        is_within_bounds = (0 <= x < width) and (0 <= y < height)
        
        if is_within_bounds:
            is_on_road = road_mask[y, x] > 0
            assert result == is_on_road, \
                f"Point ({x}, {y}) validation mismatch: expected {is_on_road}, got {result}"
        else:
            assert result == False, \
                f"Out-of-bounds point ({x}, {y}) should be invalid"
    
    @given(
        width=st.integers(min_value=10, max_value=500),
        height=st.integers(min_value=10, max_value=500)
    )
    def test_property_7_valid_point_acceptance(self, width, height):
        """
        Property 7: Valid Point Acceptance
        
        For any coordinates that lie on a road pixel (within bounds and mask value > 0),
        validate_point should return True.
        
        **Validates: Requirements 5.3, 6.3**
        """
        point_validator = PointValidator()
        
        # Create a road mask with a known road region
        road_mask = np.zeros((height, width), dtype=np.uint8)
        
        # Ensure we have a valid road region
        assume(height > 4 and width > 4)
        
        # Create road region in center
        road_y_start = height // 4
        road_y_end = 3 * height // 4
        road_x_start = width // 4
        road_x_end = 3 * width // 4
        road_mask[road_y_start:road_y_end, road_x_start:road_x_end] = 255
        
        # Select a point that is definitely on the road
        x = (road_x_start + road_x_end) // 2
        y = (road_y_start + road_y_end) // 2
        
        result = point_validator.validate_point(road_mask, x, y)
        
        # Property: Any point on a road pixel should be accepted
        assert result == True, \
            f"Valid road point ({x}, {y}) should be accepted"
        
        # Verify the point is indeed on a road pixel
        assert road_mask[y, x] > 0, \
            f"Test setup error: point ({x}, {y}) should be on road"
    
    @given(
        width=st.integers(min_value=10, max_value=500),
        height=st.integers(min_value=10, max_value=500)
    )
    def test_property_8_invalid_point_rejection(self, width, height):
        """
        Property 8: Invalid Point Rejection
        
        For any coordinates that do not lie on a road pixel (out of bounds or mask value == 0),
        validate_point should return False.
        
        **Validates: Requirements 5.4, 6.4**
        """
        point_validator = PointValidator()
        
        # Create a road mask with a known road region
        road_mask = np.zeros((height, width), dtype=np.uint8)
        
        # Ensure we have space for both road and non-road regions
        assume(height > 10 and width > 10)
        
        # Create road region in center, leaving borders as non-road
        road_mask[5:height-5, 5:width-5] = 255
        
        # Test 1: Out of bounds points should be rejected
        out_of_bounds_points = [
            (-1, height // 2),  # Negative x
            (width // 2, -1),   # Negative y
            (width, height // 2),  # x >= width
            (width // 2, height),  # y >= height
        ]
        
        for x, y in out_of_bounds_points:
            result = point_validator.validate_point(road_mask, x, y)
            assert result == False, \
                f"Out-of-bounds point ({x}, {y}) should be rejected"
        
        # Test 2: Points on non-road pixels (within bounds) should be rejected
        # Select a point in the non-road border region
        non_road_points = [
            (2, 2),  # Top-left corner (non-road)
            (width - 3, 2),  # Top-right corner (non-road)
            (2, height - 3),  # Bottom-left corner (non-road)
        ]
        
        for x, y in non_road_points:
            # Ensure point is within bounds
            if 0 <= x < width and 0 <= y < height:
                result = point_validator.validate_point(road_mask, x, y)
                # Property: Points on non-road pixels should be rejected
                assert result == False, \
                    f"Non-road point ({x}, {y}) should be rejected"
                # Verify the point is indeed not on a road pixel
                assert road_mask[y, x] == 0, \
                    f"Test setup error: point ({x}, {y}) should not be on road"
