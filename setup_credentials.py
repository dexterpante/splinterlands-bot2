"""
Account Setup Prompt - Splinterlands Bot Python Version

This file helps you set up your Splinterlands account credentials securely.
"""

import os
import getpass
from pathlib import Path
from typing import List, Tuple

def get_account_credentials() -> Tuple[str, str]:
    """
    Prompt user for account credentials.
    
    Returns:
        Tuple of (username, posting_key)
    """
    print("🔐 Splinterlands Account Setup")
    print("=" * 40)
    print()
    
    # Get username
    while True:
        username = input("Enter your Splinterlands username: ").strip()
        
        if not username:
            print("❌ Username cannot be empty!")
            continue
        
        if '@' in username:
            print("⚠️  Warning: Use your username, not email address!")
            confirm = input("Continue with this username? (y/n): ").strip().lower()
            if confirm != 'y':
                continue
        
        break
    
    # Get posting key
    while True:
        print()
        print("📝 Enter your posting key:")
        print("   - NOT your login password!")
        print("   - Get it from Splinterlands > Menu > Request Keys")
        print("   - Keep it secret and secure!")
        print()
        
        posting_key = getpass.getpass("Posting key (hidden): ").strip()
        
        if not posting_key:
            print("❌ Posting key cannot be empty!")
            continue
        
        if len(posting_key) < 40:
            print("⚠️  Warning: Posting key seems too short!")
            confirm = input("Continue with this key? (y/n): ").strip().lower()
            if confirm != 'y':
                continue
        
        break
    
    return username, posting_key

def get_multi_account_credentials() -> Tuple[List[str], List[str]]:
    """
    Prompt user for multiple account credentials.
    
    Returns:
        Tuple of (usernames, posting_keys)
    """
    print("🔐 Multi-Account Setup")
    print("=" * 40)
    print()
    
    usernames = []
    posting_keys = []
    
    while True:
        account_num = len(usernames) + 1
        print(f"Account #{account_num}:")
        
        username, posting_key = get_account_credentials()
        usernames.append(username)
        posting_keys.append(posting_key)
        
        print(f"✅ Account {account_num} added: {username}")
        print()
        
        if len(usernames) >= 2:
            add_more = input("Add another account? (y/n): ").strip().lower()
            if add_more != 'y':
                break
        else:
            print("Multi-account mode requires at least 2 accounts.")
    
    return usernames, posting_keys

def setup_configuration():
    """Set up bot configuration interactively."""
    print("🎮 Splinterlands Bot Configuration")
    print("=" * 40)
    print()
    
    config = {}
    
    # Multi-account mode
    multi_account = input("Use multi-account mode? (y/n): ").strip().lower() == 'y'
    
    if multi_account:
        usernames, posting_keys = get_multi_account_credentials()
        config['MULTI_ACCOUNT'] = 'true'
        config['ACCOUNT'] = ','.join(usernames)
        config['PASSWORD'] = ','.join(posting_keys)
    else:
        username, posting_key = get_account_credentials()
        config['MULTI_ACCOUNT'] = 'false'
        config['ACCOUNT'] = username
        config['PASSWORD'] = posting_key
    
    print()
    print("⚙️  Additional Configuration")
    print("-" * 30)
    
    # Quest priority
    quest_priority = input("Prioritize daily quests? (y/n) [default: y]: ").strip().lower()
    config['QUEST_PRIORITY'] = 'true' if quest_priority != 'n' else 'false'
    
    # Battle interval
    while True:
        try:
            interval = input("Battle interval in minutes [default: 30]: ").strip()
            if not interval:
                interval = '30'
            interval_int = int(interval)
            if interval_int < 20:
                print("⚠️  Warning: Intervals below 20 minutes may reduce rewards!")
            config['MINUTES_BATTLES_INTERVAL'] = interval
            break
        except ValueError:
            print("❌ Please enter a valid number!")
    
    # Headless mode
    headless = input("Run in headless mode (no browser window)? (y/n) [default: y]: ").strip().lower()
    config['HEADLESS'] = 'true' if headless != 'n' else 'false'
    
    # ECR management
    ecr_management = input("Set ECR stop limit? (y/n) [default: n]: ").strip().lower()
    if ecr_management == 'y':
        while True:
            try:
                ecr_limit = input("ECR stop limit (0-100): ").strip()
                ecr_limit_int = int(ecr_limit)
                if 0 <= ecr_limit_int <= 100:
                    config['ECR_STOP_LIMIT'] = ecr_limit
                    
                    ecr_recover = input("ECR recover to [default: 99]: ").strip()
                    if not ecr_recover:
                        ecr_recover = '99'
                    config['ECR_RECOVER_TO'] = ecr_recover
                    break
                else:
                    print("❌ ECR limit must be between 0 and 100!")
            except ValueError:
                print("❌ Please enter a valid number!")
    
    # Favorite deck
    favorite_deck = input("Favorite deck (fire/water/earth/life/death/dragon) [optional]: ").strip().lower()
    if favorite_deck in ['fire', 'water', 'earth', 'life', 'death', 'dragon']:
        config['FAVOURITE_DECK'] = favorite_deck
    
    # Skip quests
    skip_quests = input("Quest types to skip (comma-separated) [optional]: ").strip()
    if skip_quests:
        config['SKIP_QUEST'] = skip_quests
    
    return config

def save_configuration(config: dict):
    """Save configuration to .env file."""
    env_file = Path('.env')
    
    # Backup existing .env if it exists
    if env_file.exists():
        backup_file = Path('.env.backup')
        env_file.rename(backup_file)
        print(f"📋 Existing .env backed up to {backup_file}")
    
    # Write new configuration
    with open(env_file, 'w') as f:
        f.write("# Splinterlands Bot Configuration\n")
        f.write("# Generated by setup script\n")
        f.write(f"# Created: {os.popen('date').read().strip()}\n\n")
        
        f.write("# Account Configuration\n")
        for key in ['MULTI_ACCOUNT', 'ACCOUNT', 'PASSWORD']:
            if key in config:
                f.write(f"{key}={config[key]}\n")
        
        f.write("\n# Game Settings\n")
        game_settings = [
            'QUEST_PRIORITY', 'MINUTES_BATTLES_INTERVAL', 'HEADLESS',
            'ECR_STOP_LIMIT', 'ECR_RECOVER_TO', 'FAVOURITE_DECK', 'SKIP_QUEST'
        ]
        for key in game_settings:
            if key in config:
                f.write(f"{key}={config[key]}\n")
        
        f.write("\n# Optional Settings\n")
        f.write("CLAIM_SEASON_REWARD=false\n")
        f.write("CLAIM_DAILY_QUEST_REWARD=true\n")
        f.write("DELEGATED_CARDS_PRIORITY=false\n")
        f.write("FORCE_LOCAL_HISTORY=true\n")
        f.write("#CHROME_EXEC=/usr/bin/google-chrome-stable\n")
    
    print(f"✅ Configuration saved to {env_file}")

def main():
    """Main setup function."""
    print("🚀 Welcome to Splinterlands Bot Setup!")
    print("This wizard will help you configure your bot.")
    print()
    
    try:
        config = setup_configuration()
        save_configuration(config)
        
        print()
        print("🎉 Setup completed successfully!")
        print()
        print("Next steps:")
        print("1. Install dependencies: pip install -r requirements.txt")
        print("2. Run the bot: python main.py")
        print("3. Check logs in: logs/bot.log")
        print()
        print("⚠️  Important reminders:")
        print("- Keep your posting keys secure!")
        print("- Don't share your credentials with anyone!")
        print("- Use reasonable battle intervals (20+ minutes)")
        print("- Monitor your ECR to maintain rewards")
        
    except KeyboardInterrupt:
        print("\n❌ Setup cancelled by user.")
    except Exception as e:
        print(f"\n❌ Setup failed: {e}")

if __name__ == "__main__":
    main()