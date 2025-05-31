#!/usr/bin/env python3
"""
Main entry point for Moon Discord Bot
A GenZ Hinglish girlfriend personality bot using Gemini 2.0 Flash
"""

import asyncio
import logging
from bot.moon_bot import MoonBot

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.FileHandler('moon_bot.log'),
              logging.StreamHandler()])

logger = logging.getLogger(__name__)


async def main():
    """Main function to run the Moon bot"""
    try:
        # Hardcoded token (be cautious with sharing this)
        discord_token = "MTM3Nzc2NzkxNDY4NTU5OTgzNA.GuC6lh.4eNsy_ZW6b1bUUF3tEq5775nNzuVroIdLwb-5U"

        if not discord_token:
            logger.error("DISCORD_TOKEN is missing!")
            return

        moon = MoonBot()
        logger.info("Starting Moon bot... 🌙💕")
        await moon.start(discord_token)

    except KeyboardInterrupt:
        logger.info("Bot shutting down gracefully... 💔")
    except Exception as e:
        logger.error(f"Error running bot: {e}")


if __name__ == "__main__":
    asyncio.run(main())
