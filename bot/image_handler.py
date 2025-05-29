"""
Handles image fetching and management for Moon
"""

import aiohttp
import random
import logging
from typing import Optional, List
from config import IMAGE_SEARCH_TERMS

logger = logging.getLogger(__name__)

class ImageHandler:
    """Handles fetching trendy girl images"""
    
    def __init__(self):
        self.image_urls = []
        self.current_index = 0
        self.fallback_images = [
            "https://images.unsplash.com/photo-1494790108755-2616b612b75c?w=400&h=600&fit=crop&crop=face",
            "https://images.unsplash.com/photo-1517841905240-472988babdf9?w=400&h=600&fit=crop&crop=face", 
            "https://images.unsplash.com/photo-1524504388940-b1c1722653e1?w=400&h=600&fit=crop&crop=face",
            "https://images.unsplash.com/photo-1506863530036-1efeddceb993?w=400&h=600&fit=crop&crop=face",
            "https://images.unsplash.com/photo-1488716820095-cbe80883c496?w=400&h=600&fit=crop&crop=face"
        ]
        
        # Cute GIFs for different moods
        self.cute_gifs = [
            "https://media.giphy.com/media/3oKIPnAiaMCws8nOsE/giphy.gif",  # cute wave
            "https://media.giphy.com/media/ICOgUNjpvO0PC/giphy.gif",       # heart eyes
            "https://media.giphy.com/media/l2Je66zG6mAAZxgqI/giphy.gif",   # sending love
            "https://media.giphy.com/media/26BRzQS5HXcEWM7du/giphy.gif",   # blowing kiss
            "https://media.giphy.com/media/xUA7aM09ByyR1w5YWc/giphy.gif"   # cute smile
        ]
        
    async def get_trendy_girl_image(self) -> Optional[str]:
        """Get a trendy girl image URL"""
        try:
            # Try to get from Unsplash API first
            unsplash_url = await self._get_unsplash_image()
            if unsplash_url:
                return unsplash_url
            
            # Fallback to predefined images
            return self._get_fallback_image()
            
        except Exception as e:
            logger.error(f"Error fetching image: {e}")
            return self._get_fallback_image()
    
    async def _get_unsplash_image(self) -> Optional[str]:
        """Fetch image from Unsplash API"""
        try:
            search_term = random.choice([
                "young woman portrait",
                "girl aesthetic photo", 
                "woman selfie style",
                "female model portrait",
                "cute girl photo"
            ])
            
            # Unsplash API endpoint
            url = f"https://api.unsplash.com/photos/random"
            params = {
                "query": search_term,
                "orientation": "portrait",
                "w": "400",
                "h": "600"
            }
            
            # Note: In production, you'd want to use Unsplash API key
            # For now, using the direct URL method
            async with aiohttp.ClientSession() as session:
                # Construct Unsplash URL directly
                unsplash_id = random.choice([
                    "494790108755-2616b612b75c",
                    "517841905240-472988babdf9", 
                    "524504388940-b1c1722653e1",
                    "506863530036-1efeddceb993",
                    "488716820095-cbe80883c496",
                    "573496359688-212c8331105b",
                    "580489944406-1439066c8a60",
                    "598300042247-d088f8ab3a91"
                ])
                
                image_url = f"https://images.unsplash.com/photo-{unsplash_id}?w=400&h=600&fit=crop&crop=face"
                
                # Validate URL works
                async with session.head(image_url) as response:
                    if response.status == 200:
                        return image_url
                        
        except Exception as e:
            logger.error(f"Error with Unsplash API: {e}")
            
        return None
    
    def _get_fallback_image(self) -> str:
        """Get a fallback image from predefined list"""
        # Rotate through fallback images
        image_url = self.fallback_images[self.current_index]
        self.current_index = (self.current_index + 1) % len(self.fallback_images)
        return image_url
    
    async def get_mood_based_image(self, mood: str) -> Optional[str]:
        """Get image based on current mood"""
        mood_images = {
            "happy": [
                "https://images.unsplash.com/photo-1487412720507-e7ab37603c6f?w=400&h=600&fit=crop&crop=face",
                "https://images.unsplash.com/photo-1580489944406-1439066c8a60?w=400&h=600&fit=crop&crop=face"
            ],
            "sad": [
                "https://images.unsplash.com/photo-1573496359688-212c8331105b?w=400&h=600&fit=crop&crop=face",
                "https://images.unsplash.com/photo-1598300042247-d088f8ab3a91?w=400&h=600&fit=crop&crop=face"
            ],
            "cute": [
                "https://images.unsplash.com/photo-1494790108755-2616b612b75c?w=400&h=600&fit=crop&crop=face",
                "https://images.unsplash.com/photo-1517841905240-472988babdf9?w=400&h=600&fit=crop&crop=face"
            ]
        }
        
        if mood in mood_images:
            return random.choice(mood_images[mood])
        
        return await self.get_trendy_girl_image()
    
    async def get_activity_image(self, activity: str) -> Optional[str]:
        """Get image based on what Moon is 'doing'"""
        activity_images = {
            "studying": "https://images.unsplash.com/photo-1513475382585-d06e58bcb0e0?w=400&h=600&fit=crop",
            "coffee": "https://images.unsplash.com/photo-1509909756405-be0199881695?w=400&h=600&fit=crop", 
            "reading": "https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=400&h=600&fit=crop",
            "music": "https://images.unsplash.com/photo-1493225457124-a3eb161ffa5f?w=400&h=600&fit=crop",
            "selfie": "https://images.unsplash.com/photo-1524504388940-b1c1722653e1?w=400&h=600&fit=crop&crop=face"
        }
        
        if activity in activity_images:
            return activity_images[activity]
        
        return await self.get_trendy_girl_image()
    
    def validate_image_url(self, url: str) -> bool:
        """Basic URL validation"""
        try:
            return url.startswith(('http://', 'https://')) and any(
                url.endswith(ext) for ext in ['.jpg', '.jpeg', '.png', '.webp', '']
            )
        except:
            return False
    
    def get_random_aesthetic_context(self) -> str:
        """Get random context for what Moon is doing in the picture"""
        contexts = [
            "Just woke up, morning vibes 🌅",
            "Coffee date with myself ☕💕", 
            "Study break selfie 📚✨",
            "Late night mood 🌙",
            "Getting ready for the day 💄",
            "Lazy Sunday vibes 🛋️",
            "Missing someone special 🥺",
            "Feeling cute today 💖",
            "Room aesthetic check ✨",
            "Golden hour feels 🌅"
        ]
        return random.choice(contexts)
