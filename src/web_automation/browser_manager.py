"""
Browser manager for handling Selenium WebDriver operations.
"""

import asyncio
import logging
from typing import Optional
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import WebDriverException

from src.config import Config

logger = logging.getLogger(__name__)

class BrowserManager:
    """Manager for browser operations using Selenium."""
    
    def __init__(self, config: Config):
        self.config = config
        self.driver: Optional[webdriver.Chrome] = None
        self.wait: Optional[WebDriverWait] = None
    
    async def initialize(self) -> None:
        """Initialize the browser driver."""
        try:
            # Set up Chrome options
            chrome_options = Options()
            
            # Add arguments for better performance and stability
            chrome_options.add_argument("--no-sandbox")
            chrome_options.add_argument("--disable-dev-shm-usage")
            chrome_options.add_argument("--disable-gpu")
            chrome_options.add_argument("--disable-features=VizDisplayCompositor")
            chrome_options.add_argument("--disable-extensions")
            chrome_options.add_argument("--disable-plugins")
            chrome_options.add_argument("--disable-images")
            chrome_options.add_argument("--disable-javascript-harmony-shipping")
            chrome_options.add_argument("--disable-background-timer-throttling")
            chrome_options.add_argument("--disable-backgrounding-occluded-windows")
            chrome_options.add_argument("--disable-renderer-backgrounding")
            chrome_options.add_argument("--window-size=1920,1080")
            
            # Set headless mode
            if self.config.headless:
                chrome_options.add_argument("--headless")
                logger.info("Running in headless mode")
            else:
                logger.info("Running in non-headless mode")
            
            # Set user agent
            chrome_options.add_argument(
                "--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                "(KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
            )
            
            # Disable notifications
            prefs = {
                "profile.default_content_setting_values": {
                    "notifications": 2,
                    "media_stream": 2,
                }
            }
            chrome_options.add_experimental_option("prefs", prefs)
            
            # Set chrome executable path if specified
            if self.config.chrome_exec:
                chrome_options.binary_location = self.config.chrome_exec
            
            # Initialize the driver
            service = Service() if not self.config.chrome_exec else Service(self.config.chrome_exec)
            
            # Run driver initialization in executor to avoid blocking
            loop = asyncio.get_event_loop()
            self.driver = await loop.run_in_executor(
                None, lambda: webdriver.Chrome(service=service, options=chrome_options)
            )
            
            # Set timeouts
            self.driver.set_page_load_timeout(60)
            self.driver.implicitly_wait(10)
            
            # Initialize WebDriverWait
            self.wait = WebDriverWait(self.driver, 30)
            
            logger.info("Browser initialized successfully")
            
        except WebDriverException as e:
            logger.error(f"Failed to initialize browser: {e}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error initializing browser: {e}")
            raise
    
    async def navigate_to(self, url: str) -> None:
        """Navigate to a URL."""
        if not self.driver:
            raise RuntimeError("Browser not initialized")
        
        try:
            logger.info(f"Navigating to: {url}")
            loop = asyncio.get_event_loop()
            await loop.run_in_executor(None, self.driver.get, url)
            
            # Wait for page to load
            await self.wait_for_page_load()
            
        except Exception as e:
            logger.error(f"Error navigating to {url}: {e}")
            raise
    
    async def wait_for_page_load(self, timeout: float = 30.0) -> None:
        """Wait for page to finish loading."""
        if not self.driver:
            return
        
        try:
            loop = asyncio.get_event_loop()
            await loop.run_in_executor(
                None,
                lambda: WebDriverWait(self.driver, timeout).until(
                    lambda d: d.execute_script("return document.readyState") == "complete"
                )
            )
        except Exception as e:
            logger.warning(f"Page load timeout: {e}")
    
    async def refresh_page(self) -> None:
        """Refresh the current page."""
        if not self.driver:
            return
        
        try:
            logger.info("Refreshing page...")
            loop = asyncio.get_event_loop()
            await loop.run_in_executor(None, self.driver.refresh)
            await self.wait_for_page_load()
            
        except Exception as e:
            logger.error(f"Error refreshing page: {e}")
    
    async def execute_script(self, script: str, *args):
        """Execute JavaScript in the browser."""
        if not self.driver:
            return None
        
        try:
            loop = asyncio.get_event_loop()
            return await loop.run_in_executor(None, self.driver.execute_script, script, *args)
        except Exception as e:
            logger.error(f"Error executing script: {e}")
            return None
    
    async def take_screenshot(self, filename: str) -> bool:
        """Take a screenshot of the current page."""
        if not self.driver:
            return False
        
        try:
            loop = asyncio.get_event_loop()
            success = await loop.run_in_executor(None, self.driver.save_screenshot, filename)
            if success:
                logger.info(f"Screenshot saved: {filename}")
            return success
        except Exception as e:
            logger.error(f"Error taking screenshot: {e}")
            return False
    
    async def close(self) -> None:
        """Close the browser."""
        if self.driver:
            try:
                logger.info("Closing browser...")
                loop = asyncio.get_event_loop()
                await loop.run_in_executor(None, self.driver.quit)
                self.driver = None
                self.wait = None
                logger.info("Browser closed successfully")
            except Exception as e:
                logger.error(f"Error closing browser: {e}")
    
    def get_driver(self) -> Optional[webdriver.Chrome]:
        """Get the WebDriver instance."""
        return self.driver
    
    def get_wait(self) -> Optional[WebDriverWait]:
        """Get the WebDriverWait instance."""
        return self.wait
    
    async def is_element_present(self, by: By, value: str) -> bool:
        """Check if an element is present on the page."""
        if not self.driver:
            return False
        
        try:
            loop = asyncio.get_event_loop()
            elements = await loop.run_in_executor(None, self.driver.find_elements, by, value)
            return len(elements) > 0
        except Exception:
            return False
    
    async def wait_for_element(self, by: By, value: str, timeout: float = 30.0):
        """Wait for an element to be present."""
        if not self.driver:
            return None
        
        try:
            wait = WebDriverWait(self.driver, timeout)
            loop = asyncio.get_event_loop()
            return await loop.run_in_executor(
                None,
                lambda: wait.until(EC.presence_of_element_located((by, value)))
            )
        except Exception as e:
            logger.debug(f"Element not found: {value} - {e}")
            return None
    
    async def wait_for_clickable_element(self, by: By, value: str, timeout: float = 30.0):
        """Wait for an element to be clickable."""
        if not self.driver:
            return None
        
        try:
            wait = WebDriverWait(self.driver, timeout)
            loop = asyncio.get_event_loop()
            return await loop.run_in_executor(
                None,
                lambda: wait.until(EC.element_to_be_clickable((by, value)))
            )
        except Exception as e:
            logger.debug(f"Element not clickable: {value} - {e}")
            return None