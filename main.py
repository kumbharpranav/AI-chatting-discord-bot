#!/usr/bin/env python3
"""
Main entry point for Moon Discord Bot
A GenZ Hinglish girlfriend personality bot using Gemini 2.0 Flash
"""

import asyncio
import logging
import os
from dotenv import load_dotenv
from bot.moon_bot import MoonBot

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('moon_bot.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

async def main():
    """Main function to run the Moon bot"""
    try:
        # Get Discord token from environment
        discord_token = os.getenv('DISCORD_TOKEN')
        if not discord_token:
            logger.error("DISCORD_TOKEN not found in environment variables!")
            return
        
        # Initialize and run the bot
        moon = MoonBot()
        logger.info("Starting Moon bot... 🌙💕")
        await moon.start(discord_token)
        
    except KeyboardInterrupt:
        logger.info("Bot shutting down gracefully... 💔")
    except Exception as e:
        logger.error(f"Error running bot: {e}")

if __name__ == "__main__":
    asyncio.run(main())
