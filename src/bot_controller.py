"""
Bot controller for the Splinterlands bot.
Converted from index.js and main.js
"""

import asyncio
import logging
import time
from typing import Dict, List, Optional
from datetime import datetime, timedelta
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn

from src.config import Config
from src.services.user_service import UserService
from src.services.quest_service import QuestService, QuestDetails
from src.web_automation.browser_manager import BrowserManager
from src.web_automation.splinterlands_page import SplinterlandsPage
from src.utils.helpers import sleep, calculate_ecr_recovery_time

console = Console()
logger = logging.getLogger(__name__)

class BotController:
    """Main controller for the Splinterlands bot."""
    
    def __init__(self, config: Config):
        self.config = config
        self.user_service = UserService()
        self.quest_service = QuestService()
        self.browser_manager = BrowserManager(config)
        self.splinterlands_page = None
        
        # Stats tracking
        self.total_sps = 0
        self.win_total = 0
        self.lose_total = 0
        self.undefined_total = 0
        
        # Current account info
        self.current_account = ""
        self.current_password = ""
        self.is_multi_account_mode = config.multi_account
    
    def setup_account(self, account: str, password: str):
        """Set up account credentials for the current session."""
        self.current_account = account
        self.current_password = password
        
        logger.info(f"Account set up: {account}")
    
    async def run_single_account(self):
        """Run bot in single account mode."""
        if not self.config.account or not self.config.password:
            raise ValueError("ACCOUNT and PASSWORD must be set in environment variables")
        
        self.setup_account(self.config.account, self.config.password)
        
        try:
            await self.run_bot_session()
        except Exception as e:
            logger.error(f"Error in single account mode: {e}")
            raise
    
    async def run_multi_account(self):
        """Run bot in multi account mode."""
        if len(self.config.accounts) < 2:
            raise ValueError("Multi-account mode requires at least 2 accounts")
        
        if len(self.config.accounts) != len(self.config.passwords):
            raise ValueError("Number of accounts and passwords must match")
        
        sleep_time = self.config.minutes_battles_interval * 60
        count = 1
        
        console.print(f"[green]Accounts count: {len(self.config.accounts)}, passwords count: {len(self.config.passwords)}[/green]")
        console.print("[bold white]List of accounts to run:[/bold white]")
        
        for i, account in enumerate(self.config.accounts):
            console.print(f"[bold white]{i+1}. {account}[/bold white]")
        
        while True:
            console.print(f"[bold white on green]Running bot iteration [{count}][/bold white on green]")
            
            for i, (account, password) in enumerate(zip(self.config.accounts, self.config.passwords)):
                console.print(f"[cyan]Running account {i+1}/{len(self.config.accounts)}: {account}[/cyan]")
                
                self.setup_account(account, password)
                
                try:
                    await self.run_bot_session()
                except Exception as e:
                    logger.error(f"Error running account {account}: {e}")
                    console.print(f"[red]Error running {account}: {e}[/red]")
                
                console.print(f"[green]Finished running {account} account[/green]\n")
            
            next_run_time = datetime.now() + timedelta(seconds=sleep_time)
            console.print(f"[yellow]Waiting for the next battle in {self.config.minutes_battles_interval} minutes "
                         f"at {next_run_time.strftime('%Y-%m-%d %H:%M:%S')}[/yellow]\n")
            
            await sleep(sleep_time)
            count += 1
    
    async def run_bot_session(self):
        """Run a single bot session for the current account."""
        try:
            # Initialize browser and page
            await self.browser_manager.initialize()
            self.splinterlands_page = SplinterlandsPage(
                self.browser_manager.driver, 
                self.current_account, 
                self.current_password
            )
            
            # Navigate to Splinterlands and login
            await self.splinterlands_page.navigate_and_login()
            
            # Close any popups
            await self.close_popups()
            
            # Get user cards
            my_cards = await self.get_cards()
            logger.info(f"Loaded {len(my_cards)} cards for {self.current_account}")
            
            # Get preferred cards (rented)
            preferred_cards = await self.get_preferred_cards()
            logger.info(f"Loaded {len(preferred_cards)} preferred cards for {self.current_account}")
            
            # Get quest information
            quest = await self.get_quest()
            if quest:
                logger.info(f"Current quest: {quest.name} ({quest.splinter}) - "
                           f"{quest.completed}/{quest.total}")
            
            # Check ECR
            ecr_ok = await self.check_ecr()
            if not ecr_ok:
                logger.info("ECR too low, skipping battle")
                return
            
            # Claim rewards if enabled
            if self.config.claim_season_reward:
                await self.claim_season_rewards()
            
            if self.config.claim_daily_quest_reward:
                await self.claim_daily_quest_rewards()
            
            # Skip quest if needed
            if quest and self.should_skip_quest(quest):
                await self.skip_quest()
                # Get quest again after skipping
                quest = await self.get_quest()
            
            # Start battle
            await self.start_battle(my_cards, preferred_cards, quest)
            
        except Exception as e:
            logger.error(f"Error in bot session: {e}")
            raise
        finally:
            # Clean up
            if self.browser_manager:
                await self.browser_manager.close()
    
    async def get_cards(self) -> List[int]:
        """Get user's playable cards."""
        return await self.user_service.get_player_cards(self.current_account)
    
    async def get_preferred_cards(self) -> List[int]:
        """Get user's preferred (rented) cards."""
        return await self.user_service.get_rented_cards(self.current_account)
    
    async def get_quest(self) -> Optional[QuestDetails]:
        """Get current quest for the user."""
        return await self.quest_service.get_player_quest(self.current_account)
    
    async def close_popups(self):
        """Close any modal popups."""
        logger.info("Checking for popups to close...")
        await self.splinterlands_page.close_popups()
    
    async def check_ecr(self) -> bool:
        """
        Check Energy Capture Rate and determine if battle should proceed.
        
        Returns:
            True if ECR is acceptable, False otherwise
        """
        try:
            ecr = await self.splinterlands_page.get_ecr()
            if ecr is None:
                logger.warning("Could not get ECR, proceeding with battle")
                return True
            
            console.print(f"[bold magenta]Your current Energy Capture Rate is {ecr:.0f}%[/bold magenta]")
            
            # Check if ECR is too low
            if self.config.ecr_stop_limit is not None and ecr < self.config.ecr_stop_limit:
                recovery_time = calculate_ecr_recovery_time(ecr, self.config.ecr_recover_to)
                console.print(f"[yellow]ECR is below {self.config.ecr_stop_limit}%. "
                             f"Waiting {recovery_time:.1f} hours to recover to {self.config.ecr_recover_to}%[/yellow]")
                
                # Wait for ECR recovery
                await sleep(recovery_time * 3600)  # Convert hours to seconds
                return False
            
            return True
            
        except Exception as e:
            logger.error(f"Error checking ECR: {e}")
            return True  # Proceed if we can't check ECR
    
    async def claim_season_rewards(self):
        """Claim season rewards if available."""
        try:
            await self.splinterlands_page.claim_season_rewards()
        except Exception as e:
            logger.error(f"Error claiming season rewards: {e}")
    
    async def claim_daily_quest_rewards(self):
        """Claim daily quest rewards if available."""
        try:
            await self.splinterlands_page.claim_daily_quest_rewards()
        except Exception as e:
            logger.error(f"Error claiming daily quest rewards: {e}")
    
    def should_skip_quest(self, quest: QuestDetails) -> bool:
        """Check if quest should be skipped."""
        if not quest:
            return False
        
        return quest.splinter in self.config.skip_quest
    
    async def skip_quest(self):
        """Skip current quest and get a new one."""
        try:
            logger.info("Skipping current quest...")
            await self.splinterlands_page.skip_quest()
        except Exception as e:
            logger.error(f"Error skipping quest: {e}")
    
    async def start_battle(self, my_cards: List[int], preferred_cards: List[int], quest: Optional[QuestDetails]):
        """
        Start a battle with the given cards and quest.
        
        Args:
            my_cards: List of available card IDs
            preferred_cards: List of preferred card IDs
            quest: Current quest details
        """
        try:
            # Navigate to battle page
            await self.splinterlands_page.navigate_to_battle()
            
            # Find and start a battle
            battle_found = await self.splinterlands_page.find_battle()
            if not battle_found:
                logger.warning("No battle found")
                return
            
            # Get battle rules and mana
            battle_info = await self.splinterlands_page.get_battle_info()
            if not battle_info:
                logger.error("Could not get battle information")
                return
            
            logger.info(f"Battle found - Mana: {battle_info.get('mana', 'Unknown')}, "
                       f"Rules: {battle_info.get('rules', 'None')}")
            
            # TODO: Implement team selection logic
            # This would involve:
            # 1. Analyzing battle rules and mana cap
            # 2. Selecting optimal team based on historical data
            # 3. Considering quest requirements
            # 4. Submitting team selection
            
            logger.info("Team selection logic not yet implemented")
            
        except Exception as e:
            logger.error(f"Error starting battle: {e}")
            raise