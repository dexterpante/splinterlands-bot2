"""
Card service for handling Splinterlands card data.
Converted from cards.js
"""

import logging
from typing import Dict, List, Optional, Any
import json
from pathlib import Path

logger = logging.getLogger(__name__)

class CardService:
    """Service for handling card-related operations."""
    
    def __init__(self, data_dir: str = "data"):
        self.data_dir = Path(data_dir)
        self.cards_details = self._load_cards_details()
        self.color_to_deck = {
            'Red': 'Fire',
            'Blue': 'Water',
            'White': 'Life',
            'Black': 'Death',
            'Green': 'Earth'
        }
        self.valid_decks = ['Red', 'Blue', 'White', 'Black', 'Green']
    
    def _load_cards_details(self) -> Dict[str, Any]:
        """Load card details from JSON file."""
        cards_file = self.data_dir / "cardsDetails.json"
        try:
            if cards_file.exists():
                with open(cards_file, 'r') as f:
                    return json.load(f)
            else:
                logger.warning(f"Cards details file not found: {cards_file}")
                return {}
        except (json.JSONDecodeError, IOError) as e:
            logger.error(f"Error loading cards details: {e}")
            return {}
    
    def get_card_color(self, card_id: int) -> Optional[str]:
        """
        Get the color of a card by its ID.
        
        Args:
            card_id: The card ID
        
        Returns:
            The card color or None if not found
        """
        if not self.cards_details:
            return None
        
        # Handle both list and dict formats
        if isinstance(self.cards_details, list):
            card = next((c for c in self.cards_details if c.get('id') == card_id), None)
        else:
            card = self.cards_details.get(str(card_id))
        
        return card.get('color') if card else None
    
    def get_card_details(self, card_id: int) -> Optional[Dict[str, Any]]:
        """
        Get detailed information about a card.
        
        Args:
            card_id: The card ID
        
        Returns:
            Dictionary with card details or None if not found
        """
        if not self.cards_details:
            return None
        
        # Handle both list and dict formats
        if isinstance(self.cards_details, list):
            return next((c for c in self.cards_details if c.get('id') == card_id), None)
        else:
            return self.cards_details.get(str(card_id))
    
    def get_card_name(self, card_id: int) -> Optional[str]:
        """Get the name of a card by its ID."""
        card = self.get_card_details(card_id)
        return card.get('name') if card else None
    
    def get_card_rarity(self, card_id: int) -> Optional[str]:
        """Get the rarity of a card by its ID."""
        card = self.get_card_details(card_id)
        return card.get('rarity') if card else None
    
    def get_card_type(self, card_id: int) -> Optional[str]:
        """Get the type of a card by its ID (summoner or monster)."""
        card = self.get_card_details(card_id)
        return card.get('type') if card else None
    
    def get_card_mana_cost(self, card_id: int) -> Optional[int]:
        """Get the mana cost of a card by its ID."""
        card = self.get_card_details(card_id)
        stats = card.get('stats') if card else None
        if stats and isinstance(stats, dict):
            return stats.get('mana')
        return None
    
    def get_card_attack(self, card_id: int) -> Optional[int]:
        """Get the attack value of a card by its ID."""
        card = self.get_card_details(card_id)
        stats = card.get('stats') if card else None
        if stats and isinstance(stats, dict):
            return stats.get('attack')
        return None
    
    def get_card_health(self, card_id: int) -> Optional[int]:
        """Get the health value of a card by its ID."""
        card = self.get_card_details(card_id)
        stats = card.get('stats') if card else None
        if stats and isinstance(stats, dict):
            return stats.get('health')
        return None
    
    def get_card_speed(self, card_id: int) -> Optional[int]:
        """Get the speed value of a card by its ID."""
        card = self.get_card_details(card_id)
        stats = card.get('stats') if card else None
        if stats and isinstance(stats, dict):
            return stats.get('speed')
        return None
    
    def get_card_armor(self, card_id: int) -> Optional[int]:
        """Get the armor value of a card by its ID."""
        card = self.get_card_details(card_id)
        stats = card.get('stats') if card else None
        if stats and isinstance(stats, dict):
            return stats.get('armor')
        return None
    
    def get_card_abilities(self, card_id: int) -> List[str]:
        """Get the abilities of a card by its ID."""
        card = self.get_card_details(card_id)
        return card.get('abilities', []) if card else []
    
    def is_summoner(self, card_id: int) -> bool:
        """Check if a card is a summoner."""
        card_type = self.get_card_type(card_id)
        return card_type == 'Summoner' if card_type else False
    
    def is_monster(self, card_id: int) -> bool:
        """Check if a card is a monster."""
        card_type = self.get_card_type(card_id)
        return card_type == 'Monster' if card_type else False
    
    def get_deck_from_color(self, color: str) -> str:
        """Convert color to deck name."""
        return self.color_to_deck.get(color, '')
    
    def get_team_splinter(self, team_cards: List[int]) -> str:
        """
        Determine the main splinter of a team based on the cards.
        
        Args:
            team_cards: List of card IDs in the team
        
        Returns:
            The main splinter name
        """
        if not team_cards:
            return ''
        
        # Get the summoner (first card) to determine splinter
        summoner_id = team_cards[0]
        summoner_color = self.get_card_color(summoner_id)
        
        if summoner_color and summoner_color in self.valid_decks:
            return self.color_to_deck[summoner_color]
        
        # Fallback: check other cards
        for card_id in team_cards[1:]:
            card_color = self.get_card_color(card_id)
            if card_color and card_color in self.valid_decks:
                return self.color_to_deck[card_color]
        
        return ''
    
    def filter_cards_by_splinter(self, card_ids: List[int], splinter: str) -> List[int]:
        """
        Filter cards by splinter.
        
        Args:
            card_ids: List of card IDs to filter
            splinter: Target splinter name (Fire, Water, etc.)
        
        Returns:
            List of card IDs matching the splinter
        """
        # Convert splinter name to color
        color_map = {v: k for k, v in self.color_to_deck.items()}
        target_color = color_map.get(splinter)
        
        if not target_color:
            return []
        
        filtered_cards = []
        for card_id in card_ids:
            card_color = self.get_card_color(card_id)
            if card_color == target_color:
                filtered_cards.append(card_id)
        
        return filtered_cards
    
    def get_cards_by_type(self, card_ids: List[int], card_type: str) -> List[int]:
        """
        Filter cards by type (Summoner or Monster).
        
        Args:
            card_ids: List of card IDs to filter
            card_type: Type to filter by ('Summoner' or 'Monster')
        
        Returns:
            List of card IDs matching the type
        """
        filtered_cards = []
        for card_id in card_ids:
            if self.get_card_type(card_id) == card_type:
                filtered_cards.append(card_id)
        
        return filtered_cards
    
    def get_summoners(self, card_ids: List[int]) -> List[int]:
        """Get all summoners from a list of card IDs."""
        return self.get_cards_by_type(card_ids, 'Summoner')
    
    def get_monsters(self, card_ids: List[int]) -> List[int]:
        """Get all monsters from a list of card IDs."""
        return self.get_cards_by_type(card_ids, 'Monster')
    
    def get_cards_by_mana_cost(self, card_ids: List[int], max_mana: int, min_mana: int = 0) -> List[int]:
        """
        Filter cards by mana cost range.
        
        Args:
            card_ids: List of card IDs to filter
            max_mana: Maximum mana cost
            min_mana: Minimum mana cost
        
        Returns:
            List of card IDs within the mana range
        """
        filtered_cards = []
        for card_id in card_ids:
            mana_cost = self.get_card_mana_cost(card_id)
            if mana_cost is not None and min_mana <= mana_cost <= max_mana:
                filtered_cards.append(card_id)
        
        return filtered_cards
    
    def calculate_team_mana_cost(self, team_cards: List[int]) -> int:
        """Calculate the total mana cost of a team."""
        total_mana = 0
        for card_id in team_cards:
            mana_cost = self.get_card_mana_cost(card_id)
            if mana_cost is not None:
                total_mana += mana_cost
        return total_mana
    
    def is_team_valid_for_mana_cap(self, team_cards: List[int], mana_cap: int) -> bool:
        """Check if a team is valid for a given mana cap."""
        total_mana = self.calculate_team_mana_cost(team_cards)
        return total_mana <= mana_cap
    
    def get_card_stats_summary(self, card_id: int) -> Dict[str, Any]:
        """Get a summary of card statistics."""
        return {
            'id': card_id,
            'name': self.get_card_name(card_id),
            'color': self.get_card_color(card_id),
            'type': self.get_card_type(card_id),
            'rarity': self.get_card_rarity(card_id),
            'mana_cost': self.get_card_mana_cost(card_id),
            'attack': self.get_card_attack(card_id),
            'health': self.get_card_health(card_id),
            'speed': self.get_card_speed(card_id),
            'armor': self.get_card_armor(card_id),
            'abilities': self.get_card_abilities(card_id)
        }