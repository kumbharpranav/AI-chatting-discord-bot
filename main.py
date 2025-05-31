#!/usr/bin/env python3

import asyncio
import logging
import os
from dotenv import load_dotenv
from bot.moon_bot import MoonBot

# Load the .env file for secrets
load_dotenv()

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("moon_bot.log"),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

async def main():
    try:
        discord_token = os.getenv("DISCORD_TOKEN")
        if not discord_token:
            logger.error("DISCORD_TOKEN is missing!")
            return

        bot = MoonBot()
        logger.info("Starting Moon bot... 🌙💕")
        await bot.start(discord_token)

    except KeyboardInterrupt:
        logger.info("Bot shutting down gracefully... 💔")
    except Exception as e:
        logger.error(f"Error running bot: {e}")

if __name__ == "__main__":
    asyncio.run(main())
