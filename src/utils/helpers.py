"""
Utility functions for the Splinterlands bot.
Converted from helper.js
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from rich.console import Console

console = Console()
logger = logging.getLogger(__name__)

# Color to deck mapping
COLOR_TO_DECK = {
    'Red': 'Fire',
    'Blue': 'Water', 
    'White': 'Life',
    'Black': 'Death',
    'Green': 'Earth'
}

VALID_DECKS = ['Red', 'Blue', 'White', 'Black', 'Green']

async def sleep(seconds: float) -> None:
    """Async sleep function."""
    await asyncio.sleep(seconds)

def get_deck_from_color(color: str) -> str:
    """Convert color to deck name."""
    return COLOR_TO_DECK.get(color, '')

def team_actual_splinter_to_play(team_ids: List[int]) -> str:
    """Determine the actual splinter to play based on team IDs."""
    # This would need card details to implement properly
    # For now, return empty string as placeholder
    return ''

async def click_on_element(
    driver, 
    selector: str, 
    timeout: float = 20.0, 
    delay_before_clicking: float = 0.0,
    by: By = By.CSS_SELECTOR
) -> bool:
    """
    Click on an element if it exists.
    
    Args:
        driver: WebDriver instance
        selector: CSS selector or XPath
        timeout: Maximum wait time in seconds
        delay_before_clicking: Delay before clicking
        by: How to locate the element (CSS_SELECTOR, XPATH, etc.)
    
    Returns:
        True if element was found and clicked, False otherwise
    """
    try:
        element = WebDriverWait(driver, timeout).until(
            EC.element_to_be_clickable((by, selector))
        )
        
        if element:
            if delay_before_clicking > 0:
                await sleep(delay_before_clicking)
            
            logger.info(f"Clicking element: {selector}")
            element.click()
            return True
            
    except TimeoutException:
        logger.debug(f"Element not found or not clickable: {selector}")
    except Exception as e:
        logger.error(f"Error clicking element {selector}: {e}")
    
    logger.debug(f"No element {selector} to be clicked")
    return False

async def get_element_text(
    driver, 
    selector: str, 
    timeout: float = 15.0,
    by: By = By.CSS_SELECTOR
) -> Optional[str]:
    """
    Get text content of an element.
    
    Args:
        driver: WebDriver instance
        selector: CSS selector or XPath
        timeout: Maximum wait time in seconds
        by: How to locate the element
    
    Returns:
        Text content of the element or None if not found
    """
    try:
        element = WebDriverWait(driver, timeout).until(
            EC.presence_of_element_located((by, selector))
        )
        return element.text
        
    except TimeoutException:
        logger.debug(f"Element not found: {selector}")
        return None
    except Exception as e:
        logger.error(f"Error getting text from element {selector}: {e}")
        return None

async def get_element_text_by_xpath(
    driver, 
    xpath: str, 
    timeout: float = 15.0
) -> Optional[str]:
    """Get text content of an element by XPath."""
    return await get_element_text(driver, xpath, timeout, By.XPATH)

async def reload_page(driver) -> None:
    """Reload the current page."""
    logger.info("Reloading page...")
    driver.refresh()

def format_battle_result(result: str) -> str:
    """Format battle result for display."""
    if result.lower() == 'win':
        return console.style("WIN", color="green", bold=True)
    elif result.lower() == 'loss':
        return console.style("LOSS", color="red", bold=True)
    else:
        return console.style("DRAW", color="yellow", bold=True)

async def wait_for_element_to_disappear(
    driver, 
    selector: str, 
    timeout: float = 30.0,
    by: By = By.CSS_SELECTOR
) -> bool:
    """
    Wait for an element to disappear from the page.
    
    Args:
        driver: WebDriver instance
        selector: CSS selector or XPath
        timeout: Maximum wait time in seconds
        by: How to locate the element
    
    Returns:
        True if element disappeared, False if timeout
    """
    try:
        WebDriverWait(driver, timeout).until_not(
            EC.presence_of_element_located((by, selector))
        )
        return True
    except TimeoutException:
        logger.debug(f"Element {selector} did not disappear within {timeout} seconds")
        return False

async def wait_for_page_load(driver, timeout: float = 30.0) -> bool:
    """Wait for page to finish loading."""
    try:
        WebDriverWait(driver, timeout).until(
            lambda d: d.execute_script("return document.readyState") == "complete"
        )
        return True
    except TimeoutException:
        logger.warning("Page did not finish loading within timeout")
        return False

def calculate_ecr_recovery_time(current_ecr: float, target_ecr: float = 100.0) -> float:
    """
    Calculate time needed to recover ECR.
    
    Args:
        current_ecr: Current ECR percentage
        target_ecr: Target ECR percentage
    
    Returns:
        Time in hours needed for recovery
    """
    ecr_recovery_rate_per_hour = 1.04
    ecr_diff = target_ecr - current_ecr
    return max(0, ecr_diff / ecr_recovery_rate_per_hour)

def parse_ecr_from_text(ecr_text: str) -> Optional[float]:
    """Parse ECR percentage from text."""
    try:
        # Extract number from text like "85.5%"
        ecr_str = ecr_text.split('.')[0] if '.' in ecr_text else ecr_text
        ecr_str = ecr_str.replace('%', '').strip()
        return float(ecr_str)
    except (ValueError, IndexError):
        logger.error(f"Could not parse ECR from text: {ecr_text}")
        return None