# Sleeper Fantasy App

## Intro
I don't know where this project is going but I'll find out. 
Yes, this is mainly claude sonnet 4 generated. How else would I have the time to do this.

## Todo:
1. Learn the sleeper python API. Seems like it does a lot.
2. Figure out wtf I'm doing here.
3. Refactor this whole repo.

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