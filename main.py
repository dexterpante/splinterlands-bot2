"""
Splinterlands Bot - Python Version
A bot to automate Splinterlands gameplay using best practices.
"""

import os
import sys
import asyncio
import logging
from pathlib import Path
from dotenv import load_dotenv
from rich.console import Console
from rich.logging import RichHandler

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from src.config import Config
from src.bot_controller import BotController
from src.utils.logger import setup_logger

console = Console()

def main():
    """Main entry point for the Splinterlands bot."""
    
    # Load environment variables
    load_dotenv()
    
    # Setup logging
    setup_logger()
    logger = logging.getLogger(__name__)
    
    try:
        # Load configuration
        config = Config()
        
        # Initialize bot controller
        bot_controller = BotController(config)
        
        # Run bot
        if config.multi_account:
            console.print("[green]Starting multi-account mode[/green]")
            asyncio.run(bot_controller.run_multi_account())
        else:
            console.print("[green]Starting single-account mode[/green]")
            asyncio.run(bot_controller.run_single_account())
            
    except KeyboardInterrupt:
        console.print("\n[yellow]Bot stopped by user[/yellow]")
        logger.info("Bot stopped by user")
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        logger.error(f"Fatal error: {e}", exc_info=True)
        sys.exit(1)

if __name__ == "__main__":
    main()