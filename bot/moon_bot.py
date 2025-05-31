"""
Main Moon Discord Bot class
"""

import discord
from discord.ext import commands
from discord import app_commands
import logging
import random
import asyncio
from bot.personality import MoonPersonality
from bot.conversation_handler import ConversationHandler
from bot.image_handler import ImageHandler
# Removed TEST_GUILD_ID from import
from config import BOT_PREFIX, PICTURE_REQUESTS, EMOTIONAL_TRIGGERS

logger = logging.getLogger(__name__)


class MoonBot(commands.Bot):
    """Moon - A GenZ Hinglish girlfriend personality Discord bot"""

    def __init__(self):
        # Set up intents
        intents = discord.Intents.default()
        intents.message_content = True
        intents.members = True

        super().__init__(command_prefix=BOT_PREFIX,
                         intents=intents,
                         help_command=None,
                         case_insensitive=True)

        # Initialize components
        self.personality = MoonPersonality()
        self.conversation_handler = ConversationHandler(self.personality)
        self.image_handler = ImageHandler()

        # User conversation tracking
        self.user_conversations = {}

        # Channel activation tracking
        self.active_channels = set()

        # Track processed message IDs to prevent on_message from firing twice
        self._processed_ids = set()

        # Track which messages we've already replied to
        self._responded_ids = set()

    async def setup_hook(self) -> None:
        """
        Called before the bot connects to Discord.
        This is the ideal place to sync application commands globally.
        """
        logger.info("Running setup_hook to sync slash commands globally...")
        try:
            # This will perform a global sync of slash commands.
            # It can take several minutes to an hour for commands to appear in Discord.
            synced = await self.tree.sync()
            logger.info(f"Synced {len(synced)} global slash commands.")

        except Exception as e:
            logger.error(f"Failed to sync slash commands: {e}")

    async def on_ready(self):
        """Called when bot is ready"""
        logger.info(f'{self.user} has logged in! 🌙💕')
        logger.info(f'Bot is in {len(self.guilds)} servers')

        # Set bot status
        activity = discord.Activity(type=discord.ActivityType.listening,
                                    name="tumhare dil ki baat 💕")
        await self.change_presence(activity=activity)

        # Send a cute startup message to the first available text channel
        await self.send_startup_message()

    async def send_startup_message(self):
        """Send a cute startup message once the bot comes online."""
        try:
            for guild in self.guilds:
                for channel in guild.text_channels:
                    if channel.permissions_for(guild.me).send_messages:
                        startup_msg = await self.personality.get_startup_message(
                        )
                        await channel.send(startup_msg)
                        return
        except Exception as e:
            logger.error(f"Could not send startup message: {e}")

    async def on_message(self, message):
        """Main on_message handler; avoids double-sends by using _processed_ids."""
        # 1) Ignore the bot’s own messages
        if message.author == self.user:
            return

        # 2) Prevent processing the same message twice
        if message.id in self._processed_ids:
            return
        self._processed_ids.add(message.id)
        # Keep only last 500 IDs to avoid unbounded growth
        if len(self._processed_ids) > 1000:
            recent = list(self._processed_ids)[-500:]
            self._processed_ids = set(recent)

        logger.info(
            f"Received message from {message.author}: {message.content[:50]}..."
        )

        # 3) Check if this message starts with our command prefix → treat as a command
        if message.content.startswith(
                tuple(self.command_prefix if isinstance(
                    self.command_prefix, (list,
                                          tuple)) else [self.command_prefix])):
            await self.process_commands(message)
            return

        # 4) Otherwise, handle as natural conversation
        await self.handle_natural_conversation(message)

    async def handle_natural_conversation(self, message):
        """Handle normal, free-text conversation; ensures exactly one send per message."""
        try:
            # If we've already replied to this message ID, skip entirely.
            if message.id in self._responded_ids:
                return

            user_id = message.author.id
            content = message.content.lower()

            # Decide if Moon should respond
            is_mentioned = (self.user
                            and self.user.mentioned_in(message)) or isinstance(
                                message.channel, discord.DMChannel)
            is_reply = (
                message.reference and message.reference.message_id in getattr(
                    self, 'recent_messages', set())
            )  # Note: `recent_messages` is not an instance attribute here. It might be a placeholder or intended to be tracked elsewhere.
            is_active_channel = message.channel.id in self.active_channels
            contains_moon = 'moon' in content
            should_respond = (is_mentioned or is_reply or contains_moon
                              or is_active_channel or random.random() < 0.3)
            if not should_respond:
                return

            # Show typing indicator
            async with message.channel.typing():
                # (1) Picture request?
                if any(trigger in content for trigger in PICTURE_REQUESTS):
                    await self.send_picture_response(message)
                    return

                # (2) Emotional support?
                if any(trigger in content for trigger in EMOTIONAL_TRIGGERS):
                    response = await self.conversation_handler.get_emotional_support_response(
                        message.content, message.author.display_name)
                    await self.send_response(message, response)
                    return

                # (3) Regular conversation
                response = await self.conversation_handler.get_response(
                    message.content, message.author.display_name, user_id)
                await self.send_response(message, response)

                # Track conversation count
                self.user_conversations[user_id] = self.user_conversations.get(
                    user_id, 0) + 1

        except Exception as e:
            logger.error(f"Error in natural conversation: {e}")

    async def send_picture_response(self, message):
        """Send a picture + cute text."""
        try:
            # If we've already replied to this message ID, skip.
            if message.id in self._responded_ids:
                return

            image_url = await self.image_handler.get_trendy_girl_image()
            pic_response = await self.personality.get_picture_response(
                message.author.display_name)

            if image_url:
                embed = discord.Embed(
                    description=pic_response,
                    color=0xFF69B4  # Hot pink
                )
                embed.set_image(url=image_url)
                await message.channel.send(embed=embed)
            else:
                fallback = await self.personality.get_no_image_response()
                await message.channel.send(fallback)

            # Mark this message as “already replied to”
            self._responded_ids.add(message.id)

        except Exception as e:
            logger.error(f"Error sending picture response: {e}")
            fallback = "Arrey yaar, abhi meri pics ready nahi hai 🥺 Thoda wait karo na... 💕 {user}"
            await message.channel.send(fallback)
            self._responded_ids.add(message.id)

    async def send_response(self, message, response):
        """Wraps typing delays & optional reaction before a send."""
        try:
            # If we've already replied to this message ID, skip.
            if message.id in self._responded_ids:
                return

            # Simulate “typing…” based on response length
            typing_time = min(len(response) * 0.05, 3.0)
            await asyncio.sleep(random.uniform(1.0, typing_time))

            # Occasionally react before replying
            if random.random() < 0.3:
                reactions = ['💕', '🥺', '💖', '🌙', '✨', '🦋', '💜']
                await message.add_reaction(random.choice(reactions))

            await message.channel.send(response)

            # Mark this message as “already replied to”
            self._responded_ids.add(message.id)

        except Exception as e:
            logger.error(f"Error sending response: {e}")

    # --- Prefix Commands ---

    @commands.command(name='moon', aliases=['m'])
    async def moon_command(self, ctx, *, message: str = ""):
        """Direct command to talk to Moon."""
        if not message:
            greeting = await self.personality.get_greeting(
                ctx.author.display_name)
            await ctx.send(greeting)
            return

        async with ctx.typing():
            response = await self.conversation_handler.get_response(
                message, ctx.author.display_name, ctx.author.id)
            await ctx.send(response)

    @commands.command(name='pic', aliases=['photo', 'selfie'])
    async def pic_command(self, ctx):
        """Get Moon’s picture via command."""
        await self.send_picture_response(ctx.message)

    @commands.command(name='mood')
    async def mood_command(self, ctx):
        """Check Moon’s current mood."""
        mood_response = await self.personality.get_mood_response()
        await ctx.send(mood_response)

    @commands.command(name='date', aliases=['relationship'])
    async def date_command(self, ctx):
        """Talk about dating/relationships."""
        async with ctx.typing():
            dating_response = await self.personality.get_dating_response(
                ctx.author.display_name)
            await ctx.send(dating_response)

    async def on_command_error(self, ctx, error):
        """Handle command errors gracefully."""
        if isinstance(error, commands.CommandNotFound):
            # Let unknown messages fall back to natural conversation
            return

        logger.error(f"Command error: {error}")
        error_responses = [
            "Arrey yaar, kuch toh gadbad hai 🥺 Try karte raho na...",
            "Oops! Mujhse kuch mistake ho gayi 😅 Phir se try karo please 💕",
            "Haww, main confuse ho gayi 🤯 Thoda aaram se batao na..."
        ]
        await ctx.send(random.choice(error_responses))

    # --- Slash Commands ---

    @app_commands.command(name="talk",
                          description="Talk to Moon - your virtual girlfriend")
    @app_commands.describe(message="What do you want to say to Moon?")
    async def talk_slash(self,
                         interaction: discord.Interaction,
                         message: str = None):
        """Slash command to talk to Moon."""
        await interaction.response.defer()

        if not message:
            greeting = await self.personality.get_greeting(
                interaction.user.display_name)
            await interaction.followup.send(greeting)
            return

        response = await self.conversation_handler.get_response(
            message, interaction.user.display_name, interaction.user.id)
        await interaction.followup.send(response)

    @app_commands.command(name="pic", description="Get Moon's cute picture")
    async def pic_slash(self, interaction: discord.Interaction):
        """Slash command to get Moon's picture."""
        await interaction.response.defer()

        try:
            image_url = await self.image_handler.get_trendy_girl_image()
            pic_response = await self.personality.get_picture_response(
                interaction.user.display_name)

            if image_url:
                embed = discord.Embed(description=pic_response, color=0xFF69B4)
                embed.set_image(url=image_url)
                await interaction.followup.send(embed=embed)
            else:
                fallback = await self.personality.get_no_image_response()
                await interaction.followup.send(fallback)

        except Exception as e:
            logger.error(f"Error in pic slash command: {e}")
            fallback = "Arrey yaar, abhi meri pics ready nahi hai 🥺 Thoda wait karo na... 💕"
            await interaction.followup.send(fallback)

    @app_commands.command(name="mood", description="Check Moon's current mood")
    async def mood_slash(self, interaction: discord.Interaction):
        """Slash command to check Moon's mood."""
        await interaction.response.defer()
        mood_response = await self.personality.get_mood_response()
        await interaction.followup.send(mood_response)

    @app_commands.command(
        name="date", description="Talk to Moon about dating and relationships")
    async def date_slash(self, interaction: discord.Interaction):
        """Slash command about dating/relationships."""
        await interaction.response.defer()
        dating_response = await self.personality.get_dating_response(
            interaction.user.display_name)
        await interaction.followup.send(dating_response)

    @app_commands.command(name="support",
                          description="Get emotional support from Moon")
    @app_commands.describe(feelings="Tell Moon how you're feeling")
    async def support_slash(self, interaction: discord.Interaction,
                            feelings: str):
        """Slash command for emotional support."""
        await interaction.response.defer()
        support_response = await self.conversation_handler.get_emotional_support_response(
            feelings, interaction.user.display_name)
        await interaction.followup.send(support_response)

    @app_commands.command(name="stats",
                          description="See your relationship stats with Moon")
    async def stats_slash(self, interaction: discord.Interaction):
        """Slash command to see user stats."""
        await interaction.response.defer()

        stats = self.conversation_handler.get_user_stats(interaction.user.id)
        embed = discord.Embed(
            title=f"{interaction.user.display_name}'s Stats with Moon 🌙💕",
            color=0xFF69B4)

        embed.add_field(name="Messages Exchanged",
                        value=f"{stats['messages_exchanged']} messages",
                        inline=True)
        embed.add_field(name="Relationship Level",
                        value=stats['relationship_level'].replace('_',
                                                                  ' ').title(),
                        inline=True)
        embed.add_field(name="Days Since First Chat",
                        value=f"{stats['days_since_first_interaction']} days",
                        inline=True)

        relationship_emojis = {
            "new": "🌱",
            "acquaintance": "🌸",
            "friend": "💕",
            "close_friend": "💖"
        }
        emoji = relationship_emojis.get(stats['relationship_level'], "💝")
        embed.description = f"{emoji} Moon feels {stats['relationship_level'].replace('_', ' ')} with you!"

        await interaction.followup.send(embed=embed)

    @app_commands.command(
        name="activate",
        description="Activate Moon to respond to all messages in this channel")
    async def activate_slash(self, interaction: discord.Interaction):
        """Slash command to activate bot in current channel."""
        await interaction.response.defer()

        channel_id = interaction.channel.id
        if channel_id in self.active_channels:
            await interaction.followup.send(
                "Arrey yaar, main already active hu yahan 😏💕 Ready to chat with everyone!"
            )
        else:
            self.active_channels.add(channel_id)
            await interaction.followup.send(
                "Heyy everyone! 🌙✨ Moon is now active in this channel! Main har message ka reply karungi, so get ready for some fun conversations baby 😘💖"
            )

    @app_commands.command(
        name="deactivate",
        description="Deactivate Moon from responding to all messages")
    async def deactivate_slash(self, interaction: discord.Interaction):
        """Slash command to deactivate bot in current channel."""
        await interaction.response.defer()

        channel_id = interaction.channel.id
        if channel_id in self.active_channels:
            self.active_channels.remove(channel_id)
            await interaction.followup.send(
                "Okay baby, main ab selective responses karungi 🥺 Mention karna ya commands use karna if you want to talk 💕"
            )
        else:
            await interaction.followup.send(
                "Main already selective response mode mein hu yaar 😊 Use /activate to make me respond to everything!"
            )
