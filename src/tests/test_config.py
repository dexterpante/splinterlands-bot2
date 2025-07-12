"""
Test configuration management.
"""

import os
import pytest
from unittest.mock import patch
from src.config import Config

class TestConfig:
    """Test cases for the Config class."""
    
    def test_config_initialization_single_account(self):
        """Test config initialization for single account."""
        with patch.dict(os.environ, {
            'ACCOUNT': 'testuser',
            'PASSWORD': 'testkey',
            'MULTI_ACCOUNT': 'false',
            'QUEST_PRIORITY': 'true',
            'MINUTES_BATTLES_INTERVAL': '30'
        }):
            config = Config()
            
            assert config.account == 'testuser'
            assert config.password == 'testkey'
            assert config.multi_account is False
            assert config.quest_priority is True
            assert config.minutes_battles_interval == 30
    
    def test_config_initialization_multi_account(self):
        """Test config initialization for multi-account."""
        with patch.dict(os.environ, {
            'ACCOUNT': 'user1,user2,user3',
            'PASSWORD': 'key1,key2,key3',
            'MULTI_ACCOUNT': 'true'
        }):
            config = Config()
            
            assert config.accounts == ['user1', 'user2', 'user3']
            assert config.passwords == ['key1', 'key2', 'key3']
            assert config.multi_account is True
    
    def test_config_validation_multi_account_mismatch(self):
        """Test validation error for mismatched accounts and passwords."""
        with patch.dict(os.environ, {
            'ACCOUNT': 'user1,user2',
            'PASSWORD': 'key1,key2,key3',
            'MULTI_ACCOUNT': 'true'
        }):
            with pytest.raises(ValueError, match="Number of passwords must match"):
                Config()
    
    def test_config_favourite_deck_validation(self):
        """Test validation for favourite deck."""
        with patch.dict(os.environ, {
            'ACCOUNT': 'testuser',
            'PASSWORD': 'testkey',
            'FAVOURITE_DECK': 'invalid_deck'
        }):
            with pytest.raises(ValueError, match="Favourite deck must be one of"):
                Config()
    
    def test_config_skip_quest_parsing(self):
        """Test skip quest parsing."""
        with patch.dict(os.environ, {
            'ACCOUNT': 'testuser',
            'PASSWORD': 'testkey',
            'SKIP_QUEST': 'life,snipe,neutral'
        }):
            config = Config()
            
            assert config.skip_quest == ['life', 'snipe', 'neutral']
    
    def test_config_email_prefix_removal(self):
        """Test that email prefixes are removed from usernames."""
        with patch.dict(os.environ, {
            'ACCOUNT': 'testuser@example.com',
            'PASSWORD': 'testkey'
        }):
            config = Config()
            
            assert config.account == 'testuser'
            assert config.accounts == ['testuser']