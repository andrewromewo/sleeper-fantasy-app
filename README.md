# Sleeper Fantasy App

## Setup
```bash
# Install uv if you haven't
curl -LsSf https://astral.sh/uv/install.sh | sh

# Make an .env file with your user name. This file is ignored by git. 
echo "SLEEPER_USER=your_sleeper_username" > .env

# Clone and install dependencies
git clone https://github.com/YOUR_USERNAME/sleeper-fantasy-app.git
cd sleeper-fantasy-app
uv sync
```

## Usage
```bash
uv run main.py
```