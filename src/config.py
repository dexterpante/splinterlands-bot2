"""
Configuration management for the Splinterlands bot.
"""

import os
from typing import List, Optional
from pydantic import BaseModel, validator
from dotenv import load_dotenv

load_dotenv()

class Config(BaseModel):
    """Configuration settings for the bot."""
    
    # Account settings
    account: str
    password: str
    accounts: List[str] = []
    passwords: List[str] = []
    multi_account: bool = False
    
    # Game settings
    quest_priority: bool = True
    minutes_battles_interval: int = 30
    claim_season_reward: bool = False
    claim_daily_quest_reward: bool = True
    headless: bool = True
    ecr_stop_limit: Optional[int] = None
    ecr_recover_to: int = 99
    favourite_deck: Optional[str] = None
    skip_quest: List[str] = []
    delegated_cards_priority: bool = False
    force_local_history: bool = True
    
    # Browser settings
    chrome_exec: Optional[str] = None
    
    def __init__(self, **data):
        """Initialize configuration from environment variables."""
        
        # Load from environment
        account = os.getenv('ACCOUNT', '')
        password = os.getenv('PASSWORD', '')
        
        # Handle multi-account setup
        multi_account = os.getenv('MULTI_ACCOUNT', 'false').lower() == 'true'
        
        if multi_account:
            accounts = [acc.strip() for acc in account.split(',')]
            passwords = [pwd.strip() for pwd in password.split(',')]
            # Remove email prefix if present
            accounts = [acc.split('@')[0] for acc in accounts]
        else:
            accounts = [account.split('@')[0]]  # Remove email prefix
            passwords = [password]
        
        # Parse skip_quest
        skip_quest_str = os.getenv('SKIP_QUEST', '')
        skip_quest = [q.strip() for q in skip_quest_str.split(',') if q.strip()]
        
        config_data = {
            'account': accounts[0] if accounts else '',
            'password': passwords[0] if passwords else '',
            'accounts': accounts,
            'passwords': passwords,
            'multi_account': multi_account,
            'quest_priority': os.getenv('QUEST_PRIORITY', 'true').lower() == 'true',
            'minutes_battles_interval': int(os.getenv('MINUTES_BATTLES_INTERVAL', '30')),
            'claim_season_reward': os.getenv('CLAIM_SEASON_REWARD', 'false').lower() == 'true',
            'claim_daily_quest_reward': os.getenv('CLAIM_DAILY_QUEST_REWARD', 'true').lower() == 'true',
            'headless': os.getenv('HEADLESS', 'true').lower() == 'true',
            'ecr_stop_limit': int(os.getenv('ECR_STOP_LIMIT')) if os.getenv('ECR_STOP_LIMIT') else None,
            'ecr_recover_to': int(os.getenv('ECR_RECOVER_TO', '99')),
            'favourite_deck': os.getenv('FAVOURITE_DECK'),
            'skip_quest': skip_quest,
            'delegated_cards_priority': os.getenv('DELEGATED_CARDS_PRIORITY', 'false').lower() == 'true',
            'force_local_history': os.getenv('FORCE_LOCAL_HISTORY', 'true').lower() == 'true',
            'chrome_exec': os.getenv('CHROME_EXEC'),
        }
        
        super().__init__(**config_data)
    
    @validator('accounts')
    def validate_accounts(cls, v, values):
        """Validate accounts configuration."""
        if values.get('multi_account') and len(v) < 2:
            raise ValueError('Multi-account mode requires at least 2 accounts')
        return v
    
    @validator('passwords')
    def validate_passwords(cls, v, values):
        """Validate passwords match accounts."""
        accounts = values.get('accounts', [])
        if len(v) != len(accounts):
            raise ValueError('Number of passwords must match number of accounts')
        return v
    
    @validator('favourite_deck')
    def validate_favourite_deck(cls, v):
        """Validate favourite deck choice."""
        if v and v not in ['fire', 'life', 'earth', 'water', 'death', 'dragon']:
            raise ValueError('Favourite deck must be one of: fire, life, earth, water, death, dragon')
        return v