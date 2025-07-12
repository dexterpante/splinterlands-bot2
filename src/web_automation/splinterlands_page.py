"""
Splinterlands page automation.
Converted from splinterlandsPage.js
"""

import asyncio
import logging
from typing import Dict, Optional, Any
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException

from src.utils.helpers import click_on_element, get_element_text, get_element_text_by_xpath, sleep, parse_ecr_from_text

logger = logging.getLogger(__name__)

class SplinterlandsPage:
    """Handles Splinterlands page automation."""
    
    def __init__(self, driver, account: str, password: str):
        self.driver = driver
        self.account = account
        self.password = password
        self.wait = WebDriverWait(driver, 30)
    
    async def navigate_and_login(self) -> None:
        """Navigate to Splinterlands and login."""
        try:
            # Navigate to login page
            await self._navigate_to_login()
            
            # Perform login
            await self._perform_login()
            
            # Wait for login to complete
            await self._wait_for_login_completion()
            
            logger.info(f"Successfully logged in as {self.account}")
            
        except Exception as e:
            logger.error(f"Error during login process: {e}")
            raise
    
    async def _navigate_to_login(self) -> None:
        """Navigate to the login page."""
        login_url = "https://splinterlands.com/"
        
        loop = asyncio.get_event_loop()
        await loop.run_in_executor(None, self.driver.get, login_url)
        
        # Wait for page to load
        await self._wait_for_page_load()
    
    async def _perform_login(self) -> None:
        """Perform the login process."""
        # Wait for and click login button
        login_clicked = await click_on_element(self.driver, ".login", timeout=10)
        if not login_clicked:
            # Try alternative selectors
            login_clicked = await click_on_element(self.driver, "a[href*='login']", timeout=5)
        
        if not login_clicked:
            raise Exception("Could not find login button")
        
        await sleep(2)
        
        # Enter username
        await self._enter_credentials()
        
        # Submit login form
        await self._submit_login()
    
    async def _enter_credentials(self) -> None:
        """Enter username and password."""
        # Enter username
        username_field = await self._wait_for_element(By.NAME, "username")
        if username_field:
            await self._type_text(username_field, self.account)
        else:
            raise Exception("Could not find username field")
        
        # Enter password (posting key)
        password_field = await self._wait_for_element(By.NAME, "password")
        if password_field:
            await self._type_text(password_field, self.password)
        else:
            raise Exception("Could not find password field")
    
    async def _submit_login(self) -> None:
        """Submit the login form."""
        # Click login button
        login_button_clicked = await click_on_element(self.driver, "button[type='submit']", timeout=10)
        if not login_button_clicked:
            login_button_clicked = await click_on_element(self.driver, ".btn-primary", timeout=5)
        
        if not login_button_clicked:
            # Try pressing Enter on password field
            password_field = await self._wait_for_element(By.NAME, "password")
            if password_field:
                loop = asyncio.get_event_loop()
                await loop.run_in_executor(None, password_field.send_keys, Keys.RETURN)
            else:
                raise Exception("Could not submit login form")
    
    async def _wait_for_login_completion(self) -> None:
        """Wait for login to complete."""
        # Wait for redirect to main page or battle page
        try:
            # Wait for elements that indicate successful login
            await self._wait_for_any_element([
                (By.CLASS_NAME, "battle-btn"),
                (By.CLASS_NAME, "username"),
                (By.ID, "menu"),
                (By.XPATH, "//div[contains(@class, 'player-info')]")
            ], timeout=30)
            
            await sleep(3)  # Additional wait for page to stabilize
            
        except TimeoutException:
            logger.warning("Login completion timeout - proceeding anyway")
    
    async def close_popups(self) -> None:
        """Close any modal popups."""
        popup_selectors = [
            '.close',
            '.modal-close-new',
            '.modal-close',
            '.popup-close',
            '.dialog-close',
            '.btn-close'
        ]
        
        for selector in popup_selectors:
            try:
                await click_on_element(self.driver, selector, timeout=2)
                await sleep(1)
            except:
                continue
    
    async def get_ecr(self) -> Optional[float]:
        """Get the current Energy Capture Rate."""
        try:
            # Try different selectors for ECR
            ecr_selectors = [
                "//div[@class='sps-options'][1]/div[@class='value'][2]/div",
                "//div[contains(@class, 'energy')]//div[contains(@class, 'value')]",
                ".energy-value",
                ".ecr-value"
            ]
            
            for selector in ecr_selectors:
                if selector.startswith("//"):
                    ecr_text = await get_element_text_by_xpath(self.driver, selector, timeout=5)
                else:
                    ecr_text = await get_element_text(self.driver, selector, timeout=5)
                
                if ecr_text:
                    ecr_value = parse_ecr_from_text(ecr_text)
                    if ecr_value is not None:
                        return ecr_value
            
            logger.warning("Could not find ECR value")
            return None
            
        except Exception as e:
            logger.error(f"Error getting ECR: {e}")
            return None
    
    async def navigate_to_battle(self) -> None:
        """Navigate to the battle page."""
        try:
            # Click on battle button
            battle_clicked = await click_on_element(self.driver, ".battle-btn", timeout=10)
            if not battle_clicked:
                battle_clicked = await click_on_element(self.driver, "a[href*='battle']", timeout=5)
            
            if not battle_clicked:
                raise Exception("Could not find battle button")
            
            await sleep(3)
            await self._wait_for_page_load()
            
        except Exception as e:
            logger.error(f"Error navigating to battle: {e}")
            raise
    
    async def find_battle(self) -> bool:
        """Find and start a battle."""
        try:
            # Click on ranked battle or find opponent button
            find_battle_selectors = [
                ".find-battle-btn",
                ".battle-ranked",
                "button[contains(text(), 'FIND OPPONENT')]",
                ".btn-find-opponent"
            ]
            
            for selector in find_battle_selectors:
                if await click_on_element(self.driver, selector, timeout=5):
                    await sleep(2)
                    return True
            
            logger.warning("Could not find battle button")
            return False
            
        except Exception as e:
            logger.error(f"Error finding battle: {e}")
            return False
    
    async def get_battle_info(self) -> Optional[Dict[str, Any]]:
        """Get battle information like mana cap and rules."""
        try:
            battle_info = {}
            
            # Get mana cap
            mana_text = await get_element_text(self.driver, ".mana-cap", timeout=10)
            if mana_text:
                try:
                    battle_info['mana'] = int(mana_text.strip())
                except ValueError:
                    battle_info['mana'] = None
            
            # Get battle rules
            rules_elements = await self._find_elements(By.CLASS_NAME, "rule-item")
            if rules_elements:
                rules = []
                for rule_element in rules_elements:
                    rule_text = await self._get_element_text(rule_element)
                    if rule_text:
                        rules.append(rule_text.strip())
                battle_info['rules'] = rules
            else:
                battle_info['rules'] = []
            
            return battle_info
            
        except Exception as e:
            logger.error(f"Error getting battle info: {e}")
            return None
    
    async def claim_season_rewards(self) -> None:
        """Claim season rewards if available."""
        try:
            season_reward_clicked = await click_on_element(
                self.driver, 
                ".season-reward-btn", 
                timeout=5
            )
            if season_reward_clicked:
                logger.info("Season rewards claimed")
                await sleep(2)
            
        except Exception as e:
            logger.error(f"Error claiming season rewards: {e}")
    
    async def claim_daily_quest_rewards(self) -> None:
        """Claim daily quest rewards if available."""
        try:
            quest_reward_clicked = await click_on_element(
                self.driver, 
                ".quest-reward-btn", 
                timeout=5
            )
            if quest_reward_clicked:
                logger.info("Daily quest rewards claimed")
                await sleep(2)
            
        except Exception as e:
            logger.error(f"Error claiming daily quest rewards: {e}")
    
    async def skip_quest(self) -> None:
        """Skip the current quest."""
        try:
            skip_clicked = await click_on_element(
                self.driver, 
                ".skip-quest-btn", 
                timeout=5
            )
            if skip_clicked:
                logger.info("Quest skipped")
                await sleep(2)
            
        except Exception as e:
            logger.error(f"Error skipping quest: {e}")
    
    # Helper methods
    async def _wait_for_page_load(self) -> None:
        """Wait for page to finish loading."""
        try:
            loop = asyncio.get_event_loop()
            await loop.run_in_executor(
                None,
                lambda: WebDriverWait(self.driver, 30).until(
                    lambda d: d.execute_script("return document.readyState") == "complete"
                )
            )
        except TimeoutException:
            logger.warning("Page load timeout")
    
    async def _wait_for_element(self, by: By, value: str, timeout: float = 30.0):
        """Wait for an element to be present."""
        try:
            wait = WebDriverWait(self.driver, timeout)
            loop = asyncio.get_event_loop()
            return await loop.run_in_executor(
                None,
                lambda: wait.until(EC.presence_of_element_located((by, value)))
            )
        except TimeoutException:
            return None
    
    async def _wait_for_any_element(self, locators: list, timeout: float = 30.0):
        """Wait for any of the given elements to be present."""
        wait = WebDriverWait(self.driver, timeout)
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(
            None,
            lambda: wait.until(EC.any_of(
                *[EC.presence_of_element_located(loc) for loc in locators]
            ))
        )
    
    async def _type_text(self, element, text: str) -> None:
        """Type text into an element."""
        loop = asyncio.get_event_loop()
        await loop.run_in_executor(None, element.clear)
        await loop.run_in_executor(None, element.send_keys, text)
    
    async def _find_elements(self, by: By, value: str):
        """Find elements by locator."""
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, self.driver.find_elements, by, value)
    
    async def _get_element_text(self, element) -> Optional[str]:
        """Get text from an element."""
        try:
            loop = asyncio.get_event_loop()
            return await loop.run_in_executor(None, lambda: element.text)
        except:
            return None