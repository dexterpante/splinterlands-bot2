"""
Test helper utilities.
"""

import asyncio
import pytest
from unittest.mock import Mock, AsyncMock
from src.utils.helpers import parse_ecr_from_text, calculate_ecr_recovery_time, get_deck_from_color

class TestHelpers:
    """Test cases for helper functions."""
    
    def test_parse_ecr_from_text_valid(self):
        """Test parsing valid ECR text."""
        assert parse_ecr_from_text("85.5%") == 85.0
        assert parse_ecr_from_text("100%") == 100.0
        assert parse_ecr_from_text("42") == 42.0
        assert parse_ecr_from_text("99.9%") == 99.0
    
    def test_parse_ecr_from_text_invalid(self):
        """Test parsing invalid ECR text."""
        assert parse_ecr_from_text("invalid") is None
        assert parse_ecr_from_text("") is None
        assert parse_ecr_from_text("abc%") is None
    
    def test_calculate_ecr_recovery_time(self):
        """Test ECR recovery time calculation."""
        # Test recovery from 50% to 100%
        time_needed = calculate_ecr_recovery_time(50.0, 100.0)
        expected = 50.0 / 1.04  # 50% difference / 1.04% per hour
        assert abs(time_needed - expected) < 0.1
        
        # Test no recovery needed
        time_needed = calculate_ecr_recovery_time(100.0, 100.0)
        assert time_needed == 0.0
        
        # Test negative difference (should return 0)
        time_needed = calculate_ecr_recovery_time(100.0, 50.0)
        assert time_needed == 0.0
    
    def test_get_deck_from_color(self):
        """Test color to deck mapping."""
        assert get_deck_from_color("Red") == "Fire"
        assert get_deck_from_color("Blue") == "Water"
        assert get_deck_from_color("White") == "Life"
        assert get_deck_from_color("Black") == "Death"
        assert get_deck_from_color("Green") == "Earth"
        assert get_deck_from_color("Invalid") == ""
    
    @pytest.mark.asyncio
    async def test_sleep_function(self):
        """Test async sleep function."""
        from src.utils.helpers import sleep
        
        start_time = asyncio.get_event_loop().time()
        await sleep(0.1)
        end_time = asyncio.get_event_loop().time()
        
        # Should have slept for at least 0.1 seconds
        assert end_time - start_time >= 0.1