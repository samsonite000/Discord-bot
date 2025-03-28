"""
The main bot class for the Dynasty Tracker Discord Bot.
"""
import os
import discord
from discord.ext import commands
import logging

from config import PREFIX, INITIAL_EXTENSIONS

logger = logging.getLogger('dynasty_bot')

class DynastyBot(commands.Bot):
    """
    Custom Discord Bot class for tracking dynasty advancement status.
    """
    def __init__(self):
        # Set up intents based on what's needed and available
        try:
            intents = discord.Intents.default()
            intents.message_content = True  # Allow the bot to read message content
            intents.members = True  # Allow access to server members
            
            super().__init__(command_prefix=PREFIX, intents=intents)
            logger.info("Bot initialized with all required intents")
        except discord.errors.PrivilegedIntentsRequired:
            # Fall back to basic intents if privileged ones aren't enabled
            logger.warning("Privileged intents not enabled in Discord Developer Portal. "
                          "Some features may not work properly.")
            logger.warning("Please enable 'MESSAGE CONTENT INTENT' and 'SERVER MEMBERS INTENT' "
                          "in the Discord Developer Portal for full functionality.")
            
            basic_intents = discord.Intents.default()
            super().__init__(command_prefix=PREFIX, intents=basic_intents)
        
        # Extensions will be loaded in setup_hook
    
    async def setup_hook(self):
        """Setup hook for the bot"""
        # Load extensions during setup
        await self.load_extensions()
        
    async def on_ready(self):
        """Event triggered when the bot is ready"""
        logger.info(f"Logged in as {self.user} (ID: {self.user.id})")
        logger.info(f"Connected to {len(self.guilds)} guilds")
        await self.change_presence(activity=discord.Game(name=f"{PREFIX}help"))
    
    async def on_command_error(self, ctx, error):
        """Global error handler for command errors"""
        if isinstance(error, commands.CommandNotFound):
            return
        
        if isinstance(error, commands.MissingRequiredArgument):
            await ctx.send(f"Missing required argument: {error.param.name}")
            return
        
        if isinstance(error, commands.BadArgument):
            await ctx.send(f"Bad argument: {error}")
            return
        
        # Log the error
        logger.error(f"Command error: {error}")
    
    async def load_extensions(self):
        """Load all extension cogs"""
        for extension in INITIAL_EXTENSIONS:
            try:
                await self.load_extension(extension)
                logger.info(f"Loaded extension: {extension}")
            except Exception as e:
                logger.error(f"Failed to load extension {extension}: {e}")
