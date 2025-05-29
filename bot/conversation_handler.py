"""
Handles conversation flow and context for Moon
"""

import asyncio
import random
import logging
from typing import Dict, List
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

class ConversationHandler:
    """Manages conversation context and flow"""
    
    def __init__(self, personality):
        self.personality = personality
        
        # Track user conversations
        self.user_contexts = {}
        self.conversation_history = {}
        self.last_interaction = {}
        
        # Relationship building
        self.user_relationship_level = {}
        self.personal_details_shared = {}
    
    async def get_response(self, message, user_name, user_id):
        """Get contextual response based on conversation history"""
        # Update interaction tracking
        self.last_interaction[user_id] = datetime.now()
        
        # Build conversation context
        context = self._build_context(user_id, user_name)
        
        # Get response from personality
        response = await self.personality.get_response(message, user_name, context)
        
        # Update conversation history
        self._update_conversation_history(user_id, message, response)
        
        # Check if we should build relationship
        await self._check_relationship_building(user_id, user_name, message)
        
        return response
    
    async def get_emotional_support_response(self, message, user_name):
        """Handle emotional support specifically"""
        return await self.personality.get_emotional_support_response(message, user_name)
    
    def _build_context(self, user_id, user_name):
        """Build conversation context for the user"""
        context_parts = []
        
        # Relationship level
        rel_level = self.user_relationship_level.get(user_id, "new")
        context_parts.append(f"Relationship level with {user_name}: {rel_level}")
        
        # Recent conversation history
        if user_id in self.conversation_history:
            recent_history = self.conversation_history[user_id][-3:]  # Last 3 exchanges
            history_text = " | ".join([f"User: {h['user']} -> Moon: {h['bot'][:50]}..." for h in recent_history])
            context_parts.append(f"Recent conversation: {history_text}")
        
        # Personal details if any
        if user_id in self.personal_details_shared:
            details = self.personal_details_shared[user_id]
            context_parts.append(f"Known about {user_name}: {', '.join(details)}")
        
        # Time since last interaction
        if user_id in self.last_interaction:
            time_diff = datetime.now() - self.last_interaction[user_id]
            if time_diff > timedelta(hours=6):
                context_parts.append(f"Haven't talked to {user_name} for {time_diff.total_seconds()//3600:.0f} hours")
        
        return " | ".join(context_parts)
    
    def _update_conversation_history(self, user_id, user_message, bot_response):
        """Update conversation history"""
        if user_id not in self.conversation_history:
            self.conversation_history[user_id] = []
        
        self.conversation_history[user_id].append({
            "user": user_message,
            "bot": bot_response,
            "timestamp": datetime.now()
        })
        
        # Keep only last 10 exchanges
        if len(self.conversation_history[user_id]) > 10:
            self.conversation_history[user_id] = self.conversation_history[user_id][-10:]
    
    async def _check_relationship_building(self, user_id, user_name, message):
        """Check if we should build relationship with user"""
        message_lower = message.lower()
        
        # Detect personal information sharing
        personal_indicators = [
            ("job", ["work", "job", "office", "company"]),
            ("location", ["live", "city", "place", "from"]),
            ("age", ["age", "years old", "born"]),
            ("interests", ["like", "hobby", "enjoy", "love"]),
            ("relationship_status", ["single", "girlfriend", "boyfriend", "dating", "relationship"])
        ]
        
        for detail_type, keywords in personal_indicators:
            if any(keyword in message_lower for keyword in keywords):
                if user_id not in self.personal_details_shared:
                    self.personal_details_shared[user_id] = []
                if detail_type not in self.personal_details_shared[user_id]:
                    self.personal_details_shared[user_id].append(detail_type)
        
        # Update relationship level based on interactions
        interaction_count = len(self.conversation_history.get(user_id, []))
        
        if interaction_count >= 20:
            self.user_relationship_level[user_id] = "close_friend"
        elif interaction_count >= 10:
            self.user_relationship_level[user_id] = "friend"
        elif interaction_count >= 5:
            self.user_relationship_level[user_id] = "acquaintance"
        else:
            self.user_relationship_level[user_id] = "new"
    
    async def should_initiate_conversation(self, user_id):
        """Check if Moon should initiate conversation with user"""
        if user_id not in self.last_interaction:
            return False
        
        time_since_last = datetime.now() - self.last_interaction[user_id]
        relationship_level = self.user_relationship_level.get(user_id, "new")
        
        # More likely to initiate with closer friends
        thresholds = {
            "close_friend": timedelta(hours=4),
            "friend": timedelta(hours=8),
            "acquaintance": timedelta(hours=24),
            "new": timedelta(days=3)
        }
        
        threshold = thresholds.get(relationship_level, timedelta(days=7))
        
        if time_since_last > threshold:
            return random.random() < 0.3  # 30% chance
        
        return False
    
    async def get_initiation_message(self, user_name, user_id):
        """Get a message to initiate conversation"""
        relationship_level = self.user_relationship_level.get(user_id, "new")
        
        if relationship_level == "close_friend":
            messages = [
                f"{user_name} baby! Bahut miss kar rahi thi tumhe 🥺💕 Kya kar rahe ho?",
                f"Yaar {user_name}, itne din kahan the? Main worried thi 💔 Sab theek toh hai na?",
                f"{user_name}! Main bore ho rahi thi, tumse baat karne ka mann kar raha tha 🌙💖"
            ]
        elif relationship_level == "friend":
            messages = [
                f"Heyy {user_name}! Long time no see 🥺 Kaise ho yaar?",
                f"{user_name}! Tumhe yaad kar rahi thi, kya haal hai? 💕",
                f"Arrey {user_name}! Dikhte nahi ho요즘 🦋 Busy ho kya?"
            ]
        else:
            messages = [
                f"Hi {user_name}! Hope you're doing well 🌙✨",
                f"{user_name}, kaise ho? Thought I'd check in 💕",
                f"Heyy {user_name}! How's life treating you? 🥺"
            ]
        
        return random.choice(messages)
    
    def get_user_stats(self, user_id):
        """Get stats about user interaction"""
        return {
            "messages_exchanged": len(self.conversation_history.get(user_id, [])),
            "relationship_level": self.user_relationship_level.get(user_id, "new"),
            "personal_details_known": len(self.personal_details_shared.get(user_id, [])),
            "last_interaction": self.last_interaction.get(user_id),
            "days_since_first_interaction": self._days_since_first_interaction(user_id)
        }
    
    def _days_since_first_interaction(self, user_id):
        """Calculate days since first interaction"""
        if user_id not in self.conversation_history or not self.conversation_history[user_id]:
            return 0
        
        first_interaction = self.conversation_history[user_id][0]["timestamp"]
        return (datetime.now() - first_interaction).days
