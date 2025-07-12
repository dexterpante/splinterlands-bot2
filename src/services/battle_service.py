"""
Battle service for handling battle logic and team selection.
Converted from battles.js and possibleTeams.js concepts.
"""

import logging
import json
import random
from typing import Dict, List, Optional, Any, Tuple
from pathlib import Path
from dataclasses import dataclass

from src.services.card_service import CardService
from src.services.quest_service import QuestDetails
from src.utils.ai_helper import AIHelper, BattleAnalysis

logger = logging.getLogger(__name__)

@dataclass
class BattleRules:
    """Data class for battle rules."""
    mana_cap: int
    rules: List[str]
    inactive_splinters: List[str]
    
    def has_rule(self, rule_name: str) -> bool:
        """Check if a specific rule is active."""
        return rule_name.lower() in [r.lower() for r in self.rules]

@dataclass
class TeamComposition:
    """Data class for team composition."""
    summoner: int
    monsters: List[int]
    total_mana: int
    splinter: str
    
    def to_list(self) -> List[int]:
        """Convert to list format (summoner + monsters)."""
        return [self.summoner] + self.monsters

class BattleService:
    """Service for handling battle-related operations."""
    
    def __init__(self, card_service: CardService, data_dir: str = "data"):
        self.card_service = card_service
        self.data_dir = Path(data_dir)
        self.ai_helper = AIHelper()
        
        # Load battle history if available
        self.battle_history_file = self.data_dir / "newHistory.json"
        self.battle_history = self._load_battle_history()
    
    def _load_battle_history(self) -> List[Dict[str, Any]]:
        """Load battle history from JSON file."""
        try:
            if self.battle_history_file.exists():
                with open(self.battle_history_file, 'r') as f:
                    return json.load(f)
            else:
                logger.info("No battle history file found, starting fresh")
                return []
        except (json.JSONDecodeError, IOError) as e:
            logger.error(f"Error loading battle history: {e}")
            return []
    
    def find_optimal_team(
        self, 
        available_cards: List[int], 
        preferred_cards: List[int],
        battle_rules: BattleRules, 
        quest: Optional[QuestDetails] = None
    ) -> Optional[TeamComposition]:
        """
        Find the optimal team composition for given battle conditions.
        
        Args:
            available_cards: List of available card IDs
            preferred_cards: List of preferred card IDs (e.g., rented cards)
            battle_rules: Battle rules and constraints
            quest: Current quest details for prioritization
        
        Returns:
            TeamComposition or None if no valid team found
        """
        try:
            # Get possible teams based on battle rules
            possible_teams = self._get_possible_teams(
                available_cards, 
                preferred_cards,
                battle_rules,
                quest
            )
            
            if not possible_teams:
                logger.warning("No possible teams found for battle conditions")
                return None
            
            # Select best team based on historical performance
            best_team = self._select_best_team(possible_teams, battle_rules)
            
            if best_team:
                logger.info(f"Selected team: {best_team.splinter} splinter, "
                           f"mana: {best_team.total_mana}/{battle_rules.mana_cap}")
                return best_team
            
            logger.warning("Could not select optimal team")
            return None
            
        except Exception as e:
            logger.error(f"Error finding optimal team: {e}")
            return None
    
    def _get_possible_teams(
        self, 
        available_cards: List[int], 
        preferred_cards: List[int],
        battle_rules: BattleRules,
        quest: Optional[QuestDetails]
    ) -> List[TeamComposition]:
        """Generate possible team compositions."""
        possible_teams = []
        
        # Get available summoners
        summoners = self.card_service.get_summoners(available_cards)
        
        # Filter summoners by inactive splinters
        active_summoners = []
        for summoner in summoners:
            summoner_color = self.card_service.get_card_color(summoner)
            summoner_splinter = self.card_service.get_deck_from_color(summoner_color)
            
            if summoner_splinter and summoner_splinter.lower() not in [s.lower() for s in battle_rules.inactive_splinters]:
                active_summoners.append(summoner)
        
        # Prioritize quest splinter if applicable
        if quest and quest.splinter:
            quest_summoners = []
            for summoner in active_summoners:
                summoner_color = self.card_service.get_card_color(summoner)
                summoner_splinter = self.card_service.get_deck_from_color(summoner_color)
                if summoner_splinter and summoner_splinter.lower() == quest.splinter.lower():
                    quest_summoners.append(summoner)
            
            if quest_summoners:
                # Try quest summoners first
                active_summoners = quest_summoners + [s for s in active_summoners if s not in quest_summoners]
        
        # Generate teams for each summoner
        for summoner in active_summoners[:10]:  # Limit to avoid too many combinations
            teams = self._generate_teams_for_summoner(
                summoner, 
                available_cards, 
                preferred_cards,
                battle_rules
            )
            possible_teams.extend(teams)
        
        logger.info(f"Generated {len(possible_teams)} possible teams")
        return possible_teams
    
    def _generate_teams_for_summoner(
        self, 
        summoner: int, 
        available_cards: List[int], 
        preferred_cards: List[int],
        battle_rules: BattleRules
    ) -> List[TeamComposition]:
        """Generate team compositions for a specific summoner."""
        teams = []
        
        # Get summoner details
        summoner_color = self.card_service.get_card_color(summoner)
        summoner_splinter = self.card_service.get_deck_from_color(summoner_color)
        summoner_mana = self.card_service.get_card_mana_cost(summoner) or 0
        
        # Get available monsters for this splinter
        monsters = self.card_service.get_monsters(available_cards)
        
        # Filter monsters by splinter (same as summoner) and neutral
        splinter_monsters = []
        for monster in monsters:
            monster_color = self.card_service.get_card_color(monster)
            monster_splinter = self.card_service.get_deck_from_color(monster_color)
            
            # Include same splinter or neutral monsters
            if monster_splinter == summoner_splinter or monster_color == 'Gray':
                splinter_monsters.append(monster)
        
        # Filter by mana cap
        available_mana = battle_rules.mana_cap - summoner_mana
        viable_monsters = self.card_service.get_cards_by_mana_cost(
            splinter_monsters, 
            available_mana, 
            0
        )
        
        if not viable_monsters:
            return teams
        
        # Generate different team compositions
        team_compositions = self._create_team_compositions(
            viable_monsters, 
            preferred_cards,
            available_mana,
            battle_rules
        )
        
        # Create TeamComposition objects
        for composition in team_compositions:
            total_mana = summoner_mana + sum(
                self.card_service.get_card_mana_cost(card) or 0 
                for card in composition
            )
            
            if total_mana <= battle_rules.mana_cap:
                teams.append(TeamComposition(
                    summoner=summoner,
                    monsters=composition,
                    total_mana=total_mana,
                    splinter=summoner_splinter
                ))
        
        return teams
    
    def _create_team_compositions(
        self, 
        available_monsters: List[int], 
        preferred_cards: List[int],
        available_mana: int,
        battle_rules: BattleRules
    ) -> List[List[int]]:
        """Create different monster compositions."""
        compositions = []
        
        # Prioritize preferred cards
        preferred_monsters = [m for m in available_monsters if m in preferred_cards]
        regular_monsters = [m for m in available_monsters if m not in preferred_cards]
        
        # Sort by mana cost for better team building
        all_monsters = preferred_monsters + regular_monsters
        all_monsters.sort(key=lambda x: self.card_service.get_card_mana_cost(x) or 0, reverse=True)
        
        # Generate compositions of different sizes
        for team_size in range(1, 7):  # 1-6 monsters
            composition = self._build_team_composition(
                all_monsters, 
                available_mana, 
                team_size,
                battle_rules
            )
            
            if composition:
                compositions.append(composition)
        
        return compositions[:5]  # Limit to 5 compositions per summoner
    
    def _build_team_composition(
        self, 
        monsters: List[int], 
        available_mana: int, 
        target_size: int,
        battle_rules: BattleRules
    ) -> Optional[List[int]]:
        """Build a team composition of specific size."""
        composition = []
        remaining_mana = available_mana
        
        # Simple greedy approach - can be improved with more sophisticated algorithms
        for monster in monsters:
            if len(composition) >= target_size:
                break
            
            monster_mana = self.card_service.get_card_mana_cost(monster) or 0
            if monster_mana <= remaining_mana:
                composition.append(monster)
                remaining_mana -= monster_mana
        
        return composition if len(composition) > 0 else None
    
    def _select_best_team(
        self, 
        possible_teams: List[TeamComposition], 
        battle_rules: BattleRules
    ) -> Optional[TeamComposition]:
        """Select the best team from possible teams based on historical performance."""
        if not possible_teams:
            return None
        
        # If no battle history, return a random team
        if not self.battle_history:
            return random.choice(possible_teams)
        
        # Score teams based on historical performance
        team_scores = []
        for team in possible_teams:
            score = self._calculate_team_score(team, battle_rules)
            team_scores.append((team, score))
        
        # Sort by score (descending)
        team_scores.sort(key=lambda x: x[1], reverse=True)
        
        # Return the best team
        return team_scores[0][0]
    
    def _calculate_team_score(self, team: TeamComposition, battle_rules: BattleRules) -> float:
        """Calculate a score for a team based on historical performance."""
        score = 0.0
        
        # Base score
        score += 1.0
        
        # Bonus for mana efficiency
        mana_efficiency = team.total_mana / battle_rules.mana_cap
        score += mana_efficiency * 0.5
        
        # Bonus for team size (more monsters usually better)
        score += len(team.monsters) * 0.1
        
        # Historical performance bonus
        similar_battles = self._find_similar_battles(team, battle_rules)
        if similar_battles:
            wins = sum(1 for b in similar_battles if b.get('winner') == 'player')
            win_rate = wins / len(similar_battles)
            score += win_rate * 2.0
        
        return score
    
    def _find_similar_battles(self, team: TeamComposition, battle_rules: BattleRules) -> List[Dict[str, Any]]:
        """Find similar battles in history."""
        similar_battles = []
        
        for battle in self.battle_history:
            # Check if battle has similar conditions
            if (battle.get('mana_cap') == battle_rules.mana_cap and
                battle.get('splinter') == team.splinter):
                similar_battles.append(battle)
        
        return similar_battles
    
    def record_battle_outcome(
        self, 
        team: TeamComposition, 
        opponent_team: List[int],
        battle_rules: BattleRules,
        outcome: str,
        rating_change: int = 0
    ) -> None:
        """Record a battle outcome for learning."""
        try:
            battle_analysis = BattleAnalysis(
                battle_id=f"battle_{len(self.battle_history) + 1}",
                outcome=outcome,
                team_used=team.to_list(),
                opponent_team=opponent_team,
                mana_cap=battle_rules.mana_cap,
                rules=battle_rules.rules,
                rating_change=rating_change,
                timestamp=self.ai_helper.datetime.now()
            )
            
            # Record with AI helper for analysis
            insights = self.ai_helper.analyze_battle_outcome(battle_analysis)
            
            # Log insights
            logger.info(f"Battle outcome recorded: {outcome}")
            logger.info(f"Current win rate: {insights['win_rate']:.2%}")
            
            if insights['suggested_improvements']:
                logger.info("Suggested improvements:")
                for improvement in insights['suggested_improvements']:
                    logger.info(f"  - {improvement}")
            
        except Exception as e:
            logger.error(f"Error recording battle outcome: {e}")
    
    def get_battle_statistics(self) -> Dict[str, Any]:
        """Get comprehensive battle statistics."""
        return self.ai_helper._get_battle_statistics()
    
    def get_team_performance(self, team: List[int]) -> Dict[str, Any]:
        """Get performance statistics for a specific team."""
        return self.ai_helper._analyze_team_performance(team)