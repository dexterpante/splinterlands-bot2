# Splinterlands Bot - Python Version

A modern Python implementation of the Splinterlands game bot with enhanced features, better error handling, and AI-assisted debugging capabilities.

## 🚀 Features

- **Modern Python Architecture**: Clean, maintainable code with proper error handling
- **Async/Await Support**: Non-blocking operations for better performance
- **Rich Console Output**: Beautiful colored terminal output with progress indicators
- **Comprehensive Logging**: Detailed logs with rotation and multiple levels
- **Type Safety**: Full type hints for better IDE support and fewer bugs
- **Configuration Management**: Robust configuration with validation
- **Multi-Account Support**: Run multiple accounts efficiently
- **AI-Assisted Debugging**: Built-in debugging helpers and error analysis
- **Docker Support**: Easy deployment with containerization
- **Extensible Design**: Easy to add new features and modifications

## 📋 Requirements

- Python 3.8 or higher
- Chrome or Chromium browser
- Splinterlands account with posting key

## 🛠️ Installation

### Method 1: Quick Start (Recommended)

1. **Clone the repository**:
   ```bash
   git clone https://github.com/dexterpante/splinterlands-bot2.git
   cd splinterlands-bot2
   ```

2. **Install Python dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Install Chrome/Chromium** (if not already installed):
   ```bash
   # Ubuntu/Debian
   sudo apt-get install chromium-browser
   
   # Or for additional dependencies if needed
   sudo apt-get install libpangocairo-1.0-0 libx11-xcb1 libxcomposite1 libxcursor1 libxdamage1 libxi6 libxtst6 libnss3 libcups2 libxss1 libxrandr2 libgconf2-4 libasound2 libatk1.0-0 libgtk-3-0 libgbm-dev
   ```

4. **Configure your bot**:
   ```bash
   cp .env-example .env
   # Edit .env with your credentials
   ```

5. **Run the bot**:
   ```bash
   python main.py
   ```

### Method 2: Development Installation

1. **Clone and install in development mode**:
   ```bash
   git clone https://github.com/dexterpante/splinterlands-bot2.git
   cd splinterlands-bot2
   pip install -e .
   ```

2. **Install development dependencies**:
   ```bash
   pip install -e ".[dev]"
   ```

## ⚙️ Configuration

Create a `.env` file in the project root with your settings:

```env
# Required: Account credentials
ACCOUNT=your_username
PASSWORD=your_posting_key

# Optional: Game settings
QUEST_PRIORITY=true
MINUTES_BATTLES_INTERVAL=30
CLAIM_SEASON_REWARD=false
CLAIM_DAILY_QUEST_REWARD=true
HEADLESS=true
ECR_STOP_LIMIT=50
ECR_RECOVER_TO=99
FAVOURITE_DECK=dragon
SKIP_QUEST=life,snipe,neutral
DELEGATED_CARDS_PRIORITY=true
FORCE_LOCAL_HISTORY=true

# Optional: Multi-account mode
MULTI_ACCOUNT=false
# For multi-account, use comma-separated values:
# ACCOUNT=user1,user2,user3
# PASSWORD=key1,key2,key3

# Optional: Browser settings
CHROME_EXEC=/usr/bin/google-chrome-stable
```

### Configuration Options

| Option | Description | Default |
|--------|-------------|---------|
| `ACCOUNT` | Your Splinterlands username | Required |
| `PASSWORD` | Your posting key (not login password!) | Required |
| `MULTI_ACCOUNT` | Enable multi-account mode | `false` |
| `QUEST_PRIORITY` | Prioritize quest completion | `true` |
| `MINUTES_BATTLES_INTERVAL` | Time between battles (minutes) | `30` |
| `CLAIM_SEASON_REWARD` | Auto-claim season rewards | `false` |
| `CLAIM_DAILY_QUEST_REWARD` | Auto-claim daily quest rewards | `true` |
| `HEADLESS` | Run browser in headless mode | `true` |
| `ECR_STOP_LIMIT` | ECR threshold to stop battling | None |
| `ECR_RECOVER_TO` | ECR target for recovery | `99` |
| `FAVOURITE_DECK` | Preferred deck (fire/water/earth/life/death/dragon) | None |
| `SKIP_QUEST` | Quest types to skip (comma-separated) | None |
| `DELEGATED_CARDS_PRIORITY` | Prioritize delegated cards | `false` |
| `FORCE_LOCAL_HISTORY` | Use local history instead of API | `true` |

## 🚀 Usage

### Single Account Mode

```bash
python main.py
```

### Multi-Account Mode

Set up multiple accounts in your `.env` file:

```env
MULTI_ACCOUNT=true
ACCOUNT=user1,user2,user3
PASSWORD=postingkey1,postingkey2,postingkey3
```

### Running with Docker

```bash
# Build the image
docker build -t splinterlands-bot .

# Run the container
docker run -it --env-file .env splinterlands-bot
```

### Running as a Service (Linux)

Create a systemd service file:

```bash
sudo nano /etc/systemd/system/splinterlands-bot.service
```

```ini
[Unit]
Description=Splinterlands Bot
After=network.target

[Service]
Type=simple
User=your_username
WorkingDirectory=/path/to/splinterlands-bot2
ExecStart=/usr/bin/python3 main.py
Restart=always
RestartSec=10
Environment=PYTHONPATH=/path/to/splinterlands-bot2

[Install]
WantedBy=multi-user.target
```

Enable and start the service:

```bash
sudo systemctl daemon-reload
sudo systemctl enable splinterlands-bot
sudo systemctl start splinterlands-bot
```

## 📊 Monitoring and Debugging

### Viewing Logs

Logs are automatically saved to `logs/bot.log` with rotation:

```bash
# View recent logs
tail -f logs/bot.log

# View all logs
cat logs/bot.log
```

### Debug Mode

Run with debug output:

```bash
# Set headless to false to see browser
HEADLESS=false python main.py

# Enable debug logging
LOG_LEVEL=DEBUG python main.py
```

### AI-Assisted Debugging

The bot includes built-in debugging helpers:

- Automatic error detection and suggested fixes
- Performance monitoring and optimization suggestions
- Battle strategy analysis
- Card usage statistics

## 🔧 Development

### Project Structure

```
splinterlands-bot2/
├── src/
│   ├── services/           # API and data services
│   ├── web_automation/     # Browser automation
│   ├── utils/             # Utility functions
│   ├── models/            # Data models
│   └── config.py          # Configuration management
├── tests/                 # Test files
├── logs/                  # Log files
├── data/                  # Game data files
├── main.py               # Application entry point
├── requirements.txt      # Python dependencies
├── setup.py             # Package configuration
└── .env-example         # Example environment file
```

### Running Tests

```bash
# Install test dependencies
pip install -e ".[dev]"

# Run tests
pytest

# Run with coverage
pytest --cov=src
```

### Code Quality

```bash
# Format code
black src/

# Lint code
pylint src/

# Type checking
mypy src/
```

## 🆘 Troubleshooting

### Common Issues

1. **"Cannot find Chrome executable"**
   - Install Chrome/Chromium browser
   - Set `CHROME_EXEC` in `.env` to correct path

2. **"Login failed"**
   - Use username, not email
   - Use posting key, not login password
   - Check account credentials

3. **"ECR too low"**
   - Set `ECR_STOP_LIMIT` to pause when ECR is low
   - Wait for ECR to recover naturally

4. **"No battles found"**
   - Check internet connection
   - Verify account has sufficient rating
   - Try different times of day

### Getting Help

- Check the logs in `logs/bot.log`
- Enable debug mode with `HEADLESS=false`
- Report issues on GitHub
- Join the Discord community

## ⚠️ Important Notes

- **Use at your own risk**: Automated gameplay may violate game terms
- **Posting key safety**: Never share your posting key with anyone
- **ECR management**: Don't be greedy with battle frequency
- **Rate limiting**: Respect API rate limits
- **Account security**: Use strong passwords and secure your credentials

## 📈 Performance Tips

- Use `ECR_STOP_LIMIT` to maintain reward efficiency
- Set appropriate `MINUTES_BATTLES_INTERVAL` (minimum 20-30 minutes)
- Use `DELEGATED_CARDS_PRIORITY` for better team selection
- Enable `FORCE_LOCAL_HISTORY` for faster startup
- Run in headless mode for better performance

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Donations

If you find this bot helpful, consider supporting development:

- **DEC**: Send to player `splinterlava` in game
- **Bitcoin**: `bc1qpluvvtty822dsvfza4en9d3q3sl5yhj2qa2dtn`
- **Ethereum**: `0x8FA3414DC2a2F886e303421D07bda5Ef45C84A3b`

## 📞 Support

- [Discord Community](https://discord.gg/bR6cZDsFSX)
- [Telegram Chat](https://t.me/splinterlandsbot)
- [GitHub Issues](https://github.com/dexterpante/splinterlands-bot2/issues)