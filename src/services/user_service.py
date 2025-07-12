"""
User service for handling Splinterlands user data.
Converted from user.js
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

logger = logging.getLogger(__name__)

# Basic cards available to all players (from basicCards.js)
BASIC_CARDS = [
    157, 158, 159, 160, 395, 396, 397, 398, 399, 161, 162, 163, 167, 400, 401, 402, 403, 440,
    168, 169, 170, 171, 381, 382, 383, 384, 385, 172, 173, 174, 178, 386, 387, 388, 389, 437,
    179, 180, 181, 182, 334, 367, 368, 369, 370, 371, 183, 184, 185, 189, 372, 373, 374, 375,
    439, 146, 147, 148, 149, 409, 410, 411, 412, 413, 150, 151, 152, 156, 414, 415, 416, 417,
    135, 135, 136, 137, 138, 353, 354, 355, 356, 357, 139, 140, 141, 145, 358, 359, 360, 361,
    438, 224, 190, 191, 192, 157, 423, 424, 425, 426, 194, 195, 196, 427, 428, 429, 441
]

class UserService:
    """Service for handling user-related operations."""
    
    def __init__(self):
        self.session = requests.Session()
        
        # Set up retry strategy
        retry_strategy = Retry(
            total=3,
            backoff_factor=1,
            status_forcelist=[429, 500, 502, 503, 504],
        )
        
        adapter = HTTPAdapter(max_retries=retry_strategy)
        self.session.mount("http://", adapter)
        self.session.mount("https://", adapter)
        
        # Set headers
        self.session.headers.update({
            'accept': 'application/json, text/javascript, */*; q=0.01',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
    
    def is_playable(self, username: str, card: Dict[str, Any]) -> bool:
        """
        Check if a card is playable by the user.
        
        Args:
            username: Player username
            card: Card data dictionary
        
        Returns:
            True if card is playable, False otherwise
        """
        # Card delegated to player or owned
        delegated_ok = (
            card.get('delegated_to') == username or 
            card.get('delegated_to') is None or 
            card.get('delegated_to') == ''
        )
        
        # Not listed on market (or delegated to player)
        market_ok = (
            card.get('market_listing_status') is None or
            card.get('market_listing_status') == '' or
            (card.get('market_listing_status') is not None and card.get('delegated_to') == username)
        )
        
        # Not locked
        unlock_ok = (
            card.get('unlock_date') is None or
            card.get('unlock_date') == ''
        )
        
        # Rental lock check
        rental_ok = (
            card.get('last_used_player') == username or
            card.get('last_used_player') is None or
            (card.get('last_used_player') != username and self._is_rental_lock_expired(card))
        )
        
        # Not gladiator (edition 6 not playable in ranked)
        edition_ok = card.get('edition') != 6
        
        return delegated_ok and market_ok and unlock_ok and rental_ok and edition_ok
    
    def is_rented(self, username: str, card: Dict[str, Any]) -> bool:
        """
        Check if a card is rented by the user.
        
        Args:
            username: Player username
            card: Card data dictionary
        
        Returns:
            True if card is rented, False otherwise
        """
        # Card is delegated to player but not owned
        delegated_ok = (
            card.get('delegated_to') == username and
            card.get('player') != username
        )
        
        # Not locked
        unlock_ok = (
            card.get('unlock_date') is None or
            card.get('unlock_date') == ''
        )
        
        # Rental lock check
        rental_ok = (
            card.get('last_used_player') == username or
            card.get('last_used_player') is None or
            (card.get('last_used_player') != username and self._is_rental_lock_expired(card))
        )
        
        return delegated_ok and unlock_ok and rental_ok
    
    def _is_rental_lock_expired(self, card: Dict[str, Any]) -> bool:
        """Check if rental lock has expired (more than 1 day)."""
        last_used_date = card.get('last_used_date')
        if not last_used_date:
            return True
        
        try:
            # Parse date and check if more than 1 day has passed
            used_date = datetime.fromisoformat(last_used_date.replace('Z', '+00:00'))
            return (datetime.now() - used_date).days > 1
        except (ValueError, TypeError):
            return True
    
    async def get_player_cards(self, username: str) -> List[int]:
        """
        Get playable cards for a player.
        
        Args:
            username: Player username
        
        Returns:
            List of card IDs that are playable
        """
        try:
            # Try primary API first
            response = await self._fetch_cards_from_api(username, 'https://api2.splinterlands.com')
            if response:
                return response
            
            # Fallback to secondary API
            logger.info("Primary API failed, trying secondary API...")
            response = await self._fetch_cards_from_api(username, 'https://api.splinterlands.io')
            if response:
                return response
            
            # If both APIs fail, return basic cards
            logger.warning("Both APIs failed, using only basic cards")
            return BASIC_CARDS
            
        except Exception as e:
            logger.error(f"Error getting player cards: {e}")
            return BASIC_CARDS
    
    async def get_rented_cards(self, username: str) -> List[int]:
        """
        Get rented cards for a player.
        
        Args:
            username: Player username
        
        Returns:
            List of rented card IDs
        """
        try:
            # Try primary API first
            response = await self._fetch_cards_from_api(username, 'https://api2.splinterlands.com', rented_only=True)
            if response:
                return response
            
            # Fallback to secondary API
            logger.info("Primary API failed, trying secondary API...")
            response = await self._fetch_cards_from_api(username, 'https://api.splinterlands.io', rented_only=True)
            if response:
                return response
            
            return []
            
        except Exception as e:
            logger.error(f"Error getting rented cards: {e}")
            return []
    
    async def _fetch_cards_from_api(self, username: str, base_url: str, rented_only: bool = False) -> Optional[List[int]]:
        """
        Fetch cards from a specific API endpoint.
        
        Args:
            username: Player username
            base_url: Base URL for the API
            rented_only: If True, only return rented cards
        
        Returns:
            List of card IDs or None if failed
        """
        try:
            url = f"{base_url}/cards/collection/{username}"
            
            # Make request in a separate thread to avoid blocking
            loop = asyncio.get_event_loop()
            response = await loop.run_in_executor(None, self.session.get, url)
            response.raise_for_status()
            
            data = response.json()
            cards = data.get('cards', [])
            
            if not cards:
                logger.warning(f"No cards found for user {username}")
                return None
            
            # Filter cards based on criteria
            if rented_only:
                filtered_cards = [
                    card['card_detail_id'] for card in cards 
                    if self.is_rented(username, card)
                ]
            else:
                filtered_cards = [
                    card['card_detail_id'] for card in cards 
                    if self.is_playable(username, card)
                ]
            
            # Add basic cards if not rented_only
            if not rented_only:
                filtered_cards.extend(BASIC_CARDS)
            
            logger.info(f"Found {len(filtered_cards)} {'rented' if rented_only else 'playable'} cards for {username}")
            return filtered_cards
            
        except requests.RequestException as e:
            logger.error(f"API request failed for {base_url}: {e}")
            return None
        except Exception as e:
            logger.error(f"Error processing cards data: {e}")
            return None
    
    async def get_player_balance(self, username: str) -> Optional[Dict[str, Any]]:
        """
        Get player balance information.
        
        Args:
            username: Player username
        
        Returns:
            Dictionary with balance information or None if failed
        """
        try:
            url = f"https://api2.splinterlands.com/players/balances?username={username}"
            
            loop = asyncio.get_event_loop()
            response = await loop.run_in_executor(None, self.session.get, url)
            response.raise_for_status()
            
            return response.json()
            
        except Exception as e:
            logger.error(f"Error getting player balance: {e}")
            return None
    
    async def get_player_details(self, username: str) -> Optional[Dict[str, Any]]:
        """
        Get player details.
        
        Args:
            username: Player username
        
        Returns:
            Dictionary with player details or None if failed
        """
        try:
            url = f"https://api2.splinterlands.com/players/details?name={username}"
            
            loop = asyncio.get_event_loop()
            response = await loop.run_in_executor(None, self.session.get, url)
            response.raise_for_status()
            
            return response.json()
            
        except Exception as e:
            logger.error(f"Error getting player details: {e}")
            return None