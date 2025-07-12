#!/bin/bash
# Installation script for Splinterlands Bot Python version

set -e

echo "🚀 Installing Splinterlands Bot Python version..."

# Check Python version
python_version=$(python3 --version 2>&1 | cut -d' ' -f2)
echo "Python version: $python_version"

# Check if Python 3.8+ is available
if ! python3 -c "import sys; sys.exit(0 if sys.version_info >= (3, 8) else 1)"; then
    echo "❌ Python 3.8+ is required"
    exit 1
fi

# Create virtual environment
echo "📦 Creating virtual environment..."
python3 -m venv venv

# Activate virtual environment
echo "🔌 Activating virtual environment..."
source venv/bin/activate

# Upgrade pip
echo "⬆️ Upgrading pip..."
pip install --upgrade pip

# Install requirements
echo "📥 Installing Python dependencies..."
pip install -r requirements.txt

# Install Chrome/Chromium if not present
if ! command -v google-chrome &> /dev/null && ! command -v chromium-browser &> /dev/null; then
    echo "🌐 Installing Chrome/Chromium..."
    if command -v apt-get &> /dev/null; then
        sudo apt-get update
        sudo apt-get install -y chromium-browser
        # Install additional dependencies
        sudo apt-get install -y libpangocairo-1.0-0 libx11-xcb1 libxcomposite1 libxcursor1 libxdamage1 libxi6 libxtst6 libnss3 libcups2 libxss1 libxrandr2 libgconf2-4 libasound2 libatk1.0-0 libgtk-3-0 libgbm-dev
    elif command -v yum &> /dev/null; then
        sudo yum install -y chromium
    elif command -v dnf &> /dev/null; then
        sudo dnf install -y chromium
    else
        echo "⚠️ Could not install Chrome/Chromium automatically. Please install it manually."
    fi
fi

# Create necessary directories
echo "📁 Creating directories..."
mkdir -p logs
mkdir -p data/ai_helper
mkdir -p screenshots

# Copy example .env file if it doesn't exist
if [ ! -f .env ]; then
    echo "⚙️ Creating .env file from example..."
    cp .env-example .env
    echo "✏️ Please edit .env file with your credentials:"
    echo "   - ACCOUNT: your Splinterlands username"
    echo "   - PASSWORD: your posting key (not login password!)"
fi

# Run a quick test
echo "🧪 Testing installation..."
if python3 -c "import sys; sys.path.insert(0, '.'); from src.config import Config; print('✅ Installation test passed')"; then
    echo "✅ Installation completed successfully!"
    echo ""
    echo "🎯 Next steps:"
    echo "1. Edit .env file with your credentials"
    echo "2. Run: source venv/bin/activate"
    echo "3. Run: python main.py"
    echo ""
    echo "📚 For more information, see README-Python.md"
else
    echo "❌ Installation test failed. Please check the error messages above."
    exit 1
fi