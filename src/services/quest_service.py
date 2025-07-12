"""
Quest service for handling Splinterlands quests.
Converted from quests.js
"""

import asyncio
import logging
from typing import Dict, Optional, Any
import requests
from dataclasses import dataclass

logger = logging.getLogger(__name__)

@dataclass
class QuestDetails:
    """Data class for quest details."""
    name: str
    splinter: str
    total: int
    completed: int
    
    @property
    def progress_percentage(self) -> float:
        """Calculate quest progress as percentage."""
        if self.total == 0:
            return 0.0
        return (self.completed / self.total) * 100
    
    @property
    def is_completed(self) -> bool:
        """Check if quest is completed."""
        return self.completed >= self.total

# Quest name to element mapping
QUEST_MAPPING = {
    "defend": "life",
    "pirate": "water", 
    "High Priority Targets": "snipe",
    "lyanna": "earth",
    "stir": "fire",
    "rising": "death",
    "Stubborn Mercenaries": "neutral",
    "gloridax": "dragon",
    "Stealth Mission": "sneak",
}

class QuestService:
    """Service for handling quest-related operations."""
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'accept': 'application/json, text/javascript, */*; q=0.01',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
    
    def get_quest_splinter(self, quest_name: str) -> str:
        """
        Get the splinter/element for a quest.
        
        Args:
            quest_name: Name of the quest
        
        Returns:
            Splinter/element name
        """
        return QUEST_MAPPING.get(quest_name, "unknown")
    
    async def get_player_quest(self, username: str) -> Optional[QuestDetails]:
        """
        Get the current quest for a player.
        
        Args:
            username: Player username
        
        Returns:
            QuestDetails object or None if no quest or error
        """
        try:
            # Try primary API first
            quest_data = await self._fetch_quest_from_api(username, 'https://api2.splinterlands.com')
            if quest_data:
                return quest_data
            
            # Fallback to secondary API
            logger.info("Primary API failed, trying secondary API...")
            quest_data = await self._fetch_quest_from_api(username, 'https://api.splinterlands.io')
            if quest_data:
                return quest_data
            
            logger.warning("Both quest APIs failed")
            return None
            
        except Exception as e:
            logger.error(f"Error getting player quest: {e}")
            return None
    
    async def _fetch_quest_from_api(self, username: str, base_url: str) -> Optional[QuestDetails]:
        """
        Fetch quest data from a specific API endpoint.
        
        Args:
            username: Player username
            base_url: Base URL for the API
        
        Returns:
            QuestDetails object or None if failed
        """
        try:
            url = f"{base_url}/players/quests?username={username}"
            
            # Make request in a separate thread to avoid blocking
            loop = asyncio.get_event_loop()
            response = await loop.run_in_executor(None, self.session.get, url)
            response.raise_for_status()
            
            data = response.json()
            
            if not data or not isinstance(data, list) or len(data) == 0:
                logger.warning(f"No quest data found for user {username}")
                return None
            
            quest_info = data[0]
            quest_details = QuestDetails(
                name=quest_info['name'],
                splinter=self.get_quest_splinter(quest_info['name']),
                total=quest_info['total_items'],
                completed=quest_info['completed_items']
            )
            
            logger.info(f"Quest for {username}: {quest_details.name} ({quest_details.splinter}) - "
                       f"{quest_details.completed}/{quest_details.total} "
                       f"({quest_details.progress_percentage:.1f}%)")
            
            return quest_details
            
        except requests.RequestException as e:
            logger.error(f"Quest API request failed for {base_url}: {e}")
            return None
        except (KeyError, IndexError, TypeError) as e:
            logger.error(f"Error parsing quest data: {e}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error fetching quest: {e}")
            return None
    
    def should_prioritize_quest(self, quest: QuestDetails, skip_quests: list) -> bool:
        """
        Check if a quest should be prioritized.
        
        Args:
            quest: QuestDetails object
            skip_quests: List of quest types to skip
        
        Returns:
            True if quest should be prioritized, False otherwise
        """
        if not quest:
            return False
        
        # Skip if quest type is in skip list
        if quest.splinter in skip_quests:
            logger.info(f"Skipping quest {quest.name} ({quest.splinter}) as it's in skip list")
            return False
        
        # Skip if quest is already completed
        if quest.is_completed:
            logger.info(f"Quest {quest.name} is already completed")
            return False
        
        # Skip special quests that are not splinter-based
        special_quests = ['snipe', 'sneak', 'neutral']
        if quest.splinter in special_quests:
            logger.info(f"Skipping special quest {quest.name} ({quest.splinter})")
            return False
        
        return True
    
    def get_quest_preferred_splinter(self, quest: QuestDetails) -> Optional[str]:
        """
        Get the preferred splinter for a quest.
        
        Args:
            quest: QuestDetails object
        
        Returns:
            Preferred splinter name or None if quest should not be prioritized
        """
        if not quest:
            return None
        
        # Map quest splinters to game splinters
        splinter_mapping = {
            'fire': 'fire',
            'water': 'water',
            'earth': 'earth',
            'life': 'life',
            'death': 'death',
            'dragon': 'dragon'
        }
        
        return splinter_mapping.get(quest.splinter)