"""
Configuration settings for Moon Bot
"""

import os

# Bot settings
BOT_NAME = "Moon"
BOT_PREFIX = "!"

# API Keys
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "AIzaSyDLLTd_JDaD6tXgghU7sVXonRWdn1Nz_EQ")
DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")

# Personality settings
PERSONALITY_TRAITS = {
    "name": "Moon",
    "age_range": "early 20s",
    "personality": "introvert, caring, single, looking for love",
    "language_style": "GenZ Hinglish",
    "emotional_traits": ["cute", "caring", "supportive", "slightly lonely", "hopeful"],
    "relationship_status": "single and searching",
    "communication_style": "girlfriend-like, emotional, healing"
}

# Image search settings
IMAGE_SEARCH_TERMS = [
    "cute girl selfie",
    "aesthetic girl photo",
    "girl mirror selfie",
    "trendy girl pic",
    "girl outfit of the day",
    "cute girl aesthetic",
    "girl room aesthetic",
    "girl coffee aesthetic",
    "girl study aesthetic",
    "girl night routine"
]

# Response triggers
PICTURE_REQUESTS = [
    "send pic", "your pic", "photo", "selfie", "how do you look",
    "what are you doing", "send photo", "show yourself", "pic bhejo",
    "tumhari photo", "kya kar rahi ho", "kaise dikhti ho"
]

EMOTIONAL_TRIGGERS = [
    "sad", "depressed", "lonely", "heartbreak", "tired", "stressed",
    "anxious", "upset", "crying", "hurt", "pain", "udaas", "pareshan"
]
