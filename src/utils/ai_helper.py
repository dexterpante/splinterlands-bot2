"""
AI Helper and Debugger utilities for the Splinterlands bot.
This module provides AI-assisted debugging and decision-making capabilities.
"""

import logging
import json
import traceback
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
from datetime import datetime
from pathlib import Path

logger = logging.getLogger(__name__)

@dataclass
class BattleAnalysis:
    """Analysis of a battle outcome."""
    battle_id: str
    outcome: str  # 'win', 'loss', 'draw'
    team_used: List[int]
    opponent_team: List[int]
    mana_cap: int
    rules: List[str]
    rating_change: int
    timestamp: datetime
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        data = asdict(self)
        data['timestamp'] = self.timestamp.isoformat()
        return data

@dataclass
class ErrorAnalysis:
    """Analysis of an error occurrence."""
    error_type: str
    error_message: str
    stack_trace: str
    timestamp: datetime
    context: Dict[str, Any]
    suggested_fixes: List[str]
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        data = asdict(self)
        data['timestamp'] = self.timestamp.isoformat()
        return data

class AIHelper:
    """AI-assisted debugging and decision-making helper."""
    
    def __init__(self, data_dir: str = "data/ai_helper"):
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)
        
        # Initialize data storage
        self.battle_history_file = self.data_dir / "battle_history.json"
        self.error_history_file = self.data_dir / "error_history.json"
        self.performance_metrics_file = self.data_dir / "performance_metrics.json"
        
        self.battle_history = self._load_json(self.battle_history_file, [])
        self.error_history = self._load_json(self.error_history_file, [])
        self.performance_metrics = self._load_json(self.performance_metrics_file, {})
    
    def _load_json(self, file_path: Path, default_value: Any) -> Any:
        """Load JSON data from file."""
        try:
            if file_path.exists():
                with open(file_path, 'r') as f:
                    return json.load(f)
        except (json.JSONDecodeError, IOError) as e:
            logger.warning(f"Could not load {file_path}: {e}")
        return default_value
    
    def _save_json(self, file_path: Path, data: Any) -> None:
        """Save JSON data to file."""
        try:
            with open(file_path, 'w') as f:
                json.dump(data, f, indent=2, default=str)
        except IOError as e:
            logger.error(f"Could not save {file_path}: {e}")
    
    def analyze_error(self, error: Exception, context: Dict[str, Any] = None) -> ErrorAnalysis:
        """
        Analyze an error and provide suggested fixes.
        
        Args:
            error: The exception that occurred
            context: Additional context information
        
        Returns:
            ErrorAnalysis with suggested fixes
        """
        error_type = type(error).__name__
        error_message = str(error)
        stack_trace = traceback.format_exc()
        
        # Generate suggested fixes based on error type
        suggested_fixes = self._generate_error_fixes(error_type, error_message, context or {})
        
        analysis = ErrorAnalysis(
            error_type=error_type,
            error_message=error_message,
            stack_trace=stack_trace,
            timestamp=datetime.now(),
            context=context or {},
            suggested_fixes=suggested_fixes
        )
        
        # Store error for learning
        self.error_history.append(analysis.to_dict())
        self._save_json(self.error_history_file, self.error_history)
        
        return analysis
    
    def _generate_error_fixes(self, error_type: str, error_message: str, context: Dict[str, Any]) -> List[str]:
        """Generate suggested fixes for common errors."""
        fixes = []
        
        # Common Selenium errors
        if "TimeoutException" in error_type:
            fixes.extend([
                "Check if the page is loading correctly",
                "Verify element selectors are correct",
                "Increase timeout values",
                "Check network connection",
                "Ensure Splinterlands website is accessible"
            ])
        
        elif "NoSuchElementException" in error_type:
            fixes.extend([
                "Verify element exists on the page",
                "Check if page layout has changed",
                "Wait for page to load completely",
                "Update element selectors",
                "Check if user is logged in"
            ])
        
        elif "WebDriverException" in error_type:
            fixes.extend([
                "Check if Chrome/Chromium is installed",
                "Verify ChromeDriver compatibility",
                "Check CHROME_EXEC path in configuration",
                "Ensure sufficient system resources",
                "Try restarting the browser"
            ])
        
        # Network errors
        elif "ConnectionError" in error_type or "RequestException" in error_type:
            fixes.extend([
                "Check internet connection",
                "Verify Splinterlands API endpoints",
                "Check for API rate limiting",
                "Try alternative API endpoints",
                "Implement retry logic with backoff"
            ])
        
        # Authentication errors
        elif "login" in error_message.lower() or "auth" in error_message.lower():
            fixes.extend([
                "Verify username and posting key are correct",
                "Check if account is locked or suspended",
                "Ensure using username, not email",
                "Try logging in manually first",
                "Check if account has sufficient rating"
            ])
        
        # ECR-related errors
        elif "ecr" in error_message.lower() or "energy" in error_message.lower():
            fixes.extend([
                "Check current ECR level",
                "Adjust ECR_STOP_LIMIT if needed",
                "Wait for ECR to recover",
                "Verify ECR parsing logic",
                "Check if ECR display has changed"
            ])
        
        # Battle-related errors
        elif "battle" in error_message.lower() or "team" in error_message.lower():
            fixes.extend([
                "Check if account has sufficient cards",
                "Verify battle rules compatibility",
                "Ensure account has proper rating",
                "Check if battles are available",
                "Verify team selection logic"
            ])
        
        # Configuration errors
        elif "config" in error_message.lower() or "ValidationError" in error_type:
            fixes.extend([
                "Check .env file configuration",
                "Verify required environment variables",
                "Check configuration value formats",
                "Ensure proper multi-account setup",
                "Validate deck and quest settings"
            ])
        
        # Add generic fixes if no specific ones found
        if not fixes:
            fixes.extend([
                "Check application logs for more details",
                "Verify system requirements are met",
                "Try restarting the application",
                "Check for recent configuration changes",
                "Ensure all dependencies are installed"
            ])
        
        return fixes
    
    def analyze_battle_outcome(self, battle_analysis: BattleAnalysis) -> Dict[str, Any]:
        """
        Analyze a battle outcome and provide insights.
        
        Args:
            battle_analysis: Analysis of the battle
        
        Returns:
            Dictionary with analysis insights
        """
        # Store battle for learning
        self.battle_history.append(battle_analysis.to_dict())
        self._save_json(self.battle_history_file, self.battle_history)
        
        # Calculate win rate
        recent_battles = self.battle_history[-100:]  # Last 100 battles
        total_battles = len(recent_battles)
        wins = sum(1 for b in recent_battles if b['outcome'] == 'win')
        win_rate = wins / total_battles if total_battles > 0 else 0
        
        # Analyze team performance
        team_performance = self._analyze_team_performance(battle_analysis.team_used)
        
        # Analyze rule effectiveness
        rule_effectiveness = self._analyze_rule_effectiveness(battle_analysis.rules, battle_analysis.outcome)
        
        insights = {
            'win_rate': win_rate,
            'total_battles_analyzed': total_battles,
            'team_performance': team_performance,
            'rule_effectiveness': rule_effectiveness,
            'suggested_improvements': self._generate_battle_improvements(battle_analysis)
        }
        
        return insights
    
    def _analyze_team_performance(self, team: List[int]) -> Dict[str, Any]:
        """Analyze how well a team performs."""
        team_str = ','.join(map(str, team))
        team_battles = [b for b in self.battle_history if ','.join(map(str, b['team_used'])) == team_str]
        
        if not team_battles:
            return {'usage_count': 0, 'win_rate': 0}
        
        wins = sum(1 for b in team_battles if b['outcome'] == 'win')
        win_rate = wins / len(team_battles)
        
        return {
            'usage_count': len(team_battles),
            'win_rate': win_rate,
            'total_rating_change': sum(b['rating_change'] for b in team_battles)
        }
    
    def _analyze_rule_effectiveness(self, rules: List[str], outcome: str) -> Dict[str, Any]:
        """Analyze effectiveness under specific rules."""
        rule_battles = [b for b in self.battle_history if set(b['rules']) == set(rules)]
        
        if not rule_battles:
            return {'battles_count': 0, 'win_rate': 0}
        
        wins = sum(1 for b in rule_battles if b['outcome'] == 'win')
        win_rate = wins / len(rule_battles)
        
        return {
            'battles_count': len(rule_battles),
            'win_rate': win_rate,
            'rules': rules
        }
    
    def _generate_battle_improvements(self, battle_analysis: BattleAnalysis) -> List[str]:
        """Generate suggestions for battle improvements."""
        improvements = []
        
        # Analyze recent performance
        recent_battles = self.battle_history[-20:]  # Last 20 battles
        recent_wins = sum(1 for b in recent_battles if b['outcome'] == 'win')
        recent_win_rate = recent_wins / len(recent_battles) if recent_battles else 0
        
        if recent_win_rate < 0.4:
            improvements.append("Consider adjusting team selection strategy - win rate is below 40%")
        
        if battle_analysis.outcome == 'loss':
            improvements.append("Analyze opponent's team composition for future reference")
            improvements.append("Consider alternative strategies for these battle rules")
        
        # Mana cap analysis
        mana_battles = [b for b in self.battle_history if b['mana_cap'] == battle_analysis.mana_cap]
        if len(mana_battles) > 5:
            mana_wins = sum(1 for b in mana_battles if b['outcome'] == 'win')
            mana_win_rate = mana_wins / len(mana_battles)
            
            if mana_win_rate < 0.3:
                improvements.append(f"Low win rate ({mana_win_rate:.1%}) for {battle_analysis.mana_cap} mana battles")
        
        return improvements
    
    def get_debug_recommendations(self) -> List[str]:
        """Get general debugging recommendations based on error history."""
        recommendations = []
        
        if not self.error_history:
            return ["No errors recorded yet - system appears stable"]
        
        # Analyze error patterns
        recent_errors = self.error_history[-10:]  # Last 10 errors
        error_types = [e['error_type'] for e in recent_errors]
        
        # Count error frequency
        error_counts = {}
        for error_type in error_types:
            error_counts[error_type] = error_counts.get(error_type, 0) + 1
        
        # Generate recommendations
        for error_type, count in error_counts.items():
            if count > 3:
                recommendations.append(f"Frequent {error_type} errors detected ({count} times) - consider investigating")
        
        return recommendations or ["Error patterns analysis complete - no critical issues found"]
    
    def export_performance_report(self) -> str:
        """Export a comprehensive performance report."""
        report = {
            'timestamp': datetime.now().isoformat(),
            'battle_statistics': self._get_battle_statistics(),
            'error_statistics': self._get_error_statistics(),
            'performance_metrics': self.performance_metrics,
            'debug_recommendations': self.get_debug_recommendations()
        }
        
        report_file = self.data_dir / f"performance_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        self._save_json(report_file, report)
        
        return str(report_file)
    
    def _get_battle_statistics(self) -> Dict[str, Any]:
        """Get comprehensive battle statistics."""
        if not self.battle_history:
            return {'total_battles': 0, 'win_rate': 0}
        
        total_battles = len(self.battle_history)
        wins = sum(1 for b in self.battle_history if b['outcome'] == 'win')
        losses = sum(1 for b in self.battle_history if b['outcome'] == 'loss')
        draws = sum(1 for b in self.battle_history if b['outcome'] == 'draw')
        
        return {
            'total_battles': total_battles,
            'wins': wins,
            'losses': losses,
            'draws': draws,
            'win_rate': wins / total_battles,
            'total_rating_change': sum(b['rating_change'] for b in self.battle_history)
        }
    
    def _get_error_statistics(self) -> Dict[str, Any]:
        """Get comprehensive error statistics."""
        if not self.error_history:
            return {'total_errors': 0, 'error_types': {}}
        
        total_errors = len(self.error_history)
        error_types = {}
        
        for error in self.error_history:
            error_type = error['error_type']
            error_types[error_type] = error_types.get(error_type, 0) + 1
        
        return {
            'total_errors': total_errors,
            'error_types': error_types,
            'most_common_error': max(error_types, key=error_types.get) if error_types else None
        }