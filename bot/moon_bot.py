"""
Main Moon Discord Bot class
"""

import discord
from discord.ext import commands
import logging
import random
import asyncio
from bot.personality import MoonPersonality
from bot.conversation_handler import ConversationHandler
from bot.image_handler import ImageHandler
from config import BOT_PREFIX, PICTURE_REQUESTS, EMOTIONAL_TRIGGERS

logger = logging.getLogger(__name__)

class MoonBot(commands.Bot):
    """Moon - A GenZ Hinglish girlfriend personality Discord bot"""
    
    def __init__(self):
        # Set up intents
        intents = discord.Intents.default()
        intents.message_content = True
        intents.members = True
        
        super().__init__(
            command_prefix=BOT_PREFIX,
            intents=intents,
            help_command=None,
            case_insensitive=True
        )
        
        # Initialize components
        self.personality = MoonPersonality()
        self.conversation_handler = ConversationHandler(self.personality)
        self.image_handler = ImageHandler()
        
        # User conversation tracking
        self.user_conversations = {}
        self.last_message_time = {}
    
    async def on_ready(self):
        """Called when bot is ready"""
        logger.info(f'{self.user} has logged in! 🌙💕')
        logger.info(f'Bot is in {len(self.guilds)} servers')
        
        # Set bot status
        activity = discord.Activity(
            type=discord.ActivityType.listening,
            name="tumhare dil ki baat 💕"
        )
        await self.change_presence(activity=activity)
        
        # Send a cute startup message to bot owner if possible
        await self.send_startup_message()
    
    async def send_startup_message(self):
        """Send a cute startup message"""
        try:
            # Try to send to the first available text channel
            for guild in self.guilds:
                for channel in guild.text_channels:
                    if channel.permissions_for(guild.me).send_messages:
                        startup_msg = await self.personality.get_startup_message()
                        await channel.send(startup_msg)
                        return
        except Exception as e:
            logger.error(f"Could not send startup message: {e}")
    
    async def on_message(self, message):
        """Handle incoming messages"""
        # Ignore bot's own messages
        if message.author == self.user:
            return
        
        # Process commands first
        await self.process_commands(message)
        
        # Handle natural conversation
        await self.handle_natural_conversation(message)
    
    async def handle_natural_conversation(self, message):
        """Handle natural conversation without explicit commands"""
        try:
            user_id = message.author.id
            content = message.content.lower()
            
            # Check if Moon is mentioned or DM
            is_mentioned = self.user.mentioned_in(message) or isinstance(message.channel, discord.DMChannel)
            is_reply = message.reference and message.reference.message_id in getattr(self, 'recent_messages', set())
            should_respond = is_mentioned or is_reply or random.random() < 0.3  # 30% chance to respond randomly
            
            if not should_respond:
                return
            
            # Show typing indicator
            async with message.channel.typing():
                # Check for picture requests
                if any(trigger in content for trigger in PICTURE_REQUESTS):
                    await self.send_picture_response(message)
                    return
                
                # Check for emotional support needs
                if any(trigger in content for trigger in EMOTIONAL_TRIGGERS):
                    response = await self.conversation_handler.get_emotional_support_response(
                        message.content, message.author.display_name
                    )
                    await self.send_response(message, response)
                    return
                
                # Regular conversation
                response = await self.conversation_handler.get_response(
                    message.content, 
                    message.author.display_name,
                    user_id
                )
                await self.send_response(message, response)
                
                # Track conversation
                self.user_conversations[user_id] = self.user_conversations.get(user_id, 0) + 1
                
                # Occasionally ask questions like a girlfriend
                if random.random() < 0.2:  # 20% chance
                    await asyncio.sleep(random.uniform(2, 5))
                    question = await self.personality.get_girlfriend_question(message.author.display_name)
                    await message.channel.send(question)
        
        except Exception as e:
            logger.error(f"Error in natural conversation: {e}")
    
    async def send_picture_response(self, message):
        """Send a picture response with cute message"""
        try:
            # Get image URL
            image_url = await self.image_handler.get_trendy_girl_image()
            
            # Get cute response
            pic_response = await self.personality.get_picture_response(message.author.display_name)
            
            if image_url:
                embed = discord.Embed(
                    description=pic_response,
                    color=0xFF69B4  # Hot pink
                )
                embed.set_image(url=image_url)
                await message.channel.send(embed=embed)
            else:
                # Fallback if no image found
                fallback_response = await self.personality.get_no_image_response()
                await message.channel.send(fallback_response)
        
        except Exception as e:
            logger.error(f"Error sending picture response: {e}")
            fallback = "Arrey yaar, abhi meri pics ready nahi hai 🥺 Thoda wait karo na... 💕"
            await message.channel.send(fallback)
    
    async def send_response(self, message, response):
        """Send response with random delays to seem more human"""
        try:
            # Add typing delay based on message length
            typing_time = min(len(response) * 0.05, 3.0)  # Max 3 seconds
            await asyncio.sleep(random.uniform(1.0, typing_time))
            
            # Occasionally react before responding
            if random.random() < 0.3:
                reactions = ['💕', '🥺', '💖', '🌙', '✨', '🦋', '💜']
                await message.add_reaction(random.choice(reactions))
            
            await message.channel.send(response)
        
        except Exception as e:
            logger.error(f"Error sending response: {e}")
    
    @commands.command(name='moon', aliases=['m'])
    async def moon_command(self, ctx, *, message: str = None):
        """Direct command to talk to Moon"""
        if not message:
            greeting = await self.personality.get_greeting(ctx.author.display_name)
            await ctx.send(greeting)
            return
        
        async with ctx.typing():
            response = await self.conversation_handler.get_response(
                message, 
                ctx.author.display_name,
                ctx.author.id
            )
            await ctx.send(response)
    
    @commands.command(name='pic', aliases=['photo', 'selfie'])
    async def pic_command(self, ctx):
        """Get Moon's picture"""
        await self.send_picture_response(ctx.message)
    
    @commands.command(name='mood')
    async def mood_command(self, ctx):
        """Check Moon's current mood"""
        mood_response = await self.personality.get_mood_response()
        await ctx.send(mood_response)
    
    @commands.command(name='date', aliases=['relationship'])
    async def date_command(self, ctx):
        """Talk about dating/relationships"""
        async with ctx.typing():
            dating_response = await self.personality.get_dating_response(ctx.author.display_name)
            await ctx.send(dating_response)
    
    async def on_command_error(self, ctx, error):
        """Handle command errors gracefully"""
        if isinstance(error, commands.CommandNotFound):
            # Don't respond to unknown commands, let natural conversation handle it
            return
        
        logger.error(f"Command error: {error}")
        
        # Send a cute error message
        error_responses = [
            "Arrey yaar, kuch toh gadbad hai 🥺 Try karte raho na...",
            "Oops! Mujhse kuch mistake ho gayi 😅 Phir se try karo please 💕",
            "Haww, main confuse ho gayi 🤯 Thoda aaram se batao na..."
        ]
        await ctx.send(random.choice(error_responses))
