"""
Reminders cog for the Dynasty Tracker Discord Bot.
This module handles scheduled reminders for users who haven't
marked their dynasties as ready.
"""
import discord
from discord.ext import commands, tasks
import logging
import datetime
import pytz
import asyncio

from config import DYNASTIES, USERS, TIMEZONE, REMINDER_DAY, REMINDER_HOUR, REMINDER_MINUTE
from utils.storage import DynastyStorage
from utils.embeds import create_status_embed

logger = logging.getLogger('dynasty_bot.reminders')

class Reminders(commands.Cog):
    """
    A cog for sending scheduled reminders about dynasty advancement.
    """
    def __init__(self, bot):
        self.bot = bot
        self.storage = DynastyStorage()
        self.reminder_task.start()
    
    def cog_unload(self):
        """Stop the reminder task when the cog is unloaded."""
        self.reminder_task.cancel()
    
    @tasks.loop(hours=1)
    async def reminder_task(self):
        """Check if reminders need to be sent every hour."""
        # Get the current time in the specified timezone
        tz = pytz.timezone(TIMEZONE)
        now = datetime.datetime.now(tz)
        
        # Check if it's time to send reminders (Saturday at 9:00 AM Central)
        if now.weekday() == REMINDER_DAY and now.hour == REMINDER_HOUR and now.minute < 60:
            logger.info("Sending weekly reminders")
            await self.send_reminders()
    
    @reminder_task.before_loop
    async def before_reminder_task(self):
        """Wait until the bot is ready before starting the task."""
        await self.bot.wait_until_ready()
    
    async def send_reminders(self):
        """Send reminder messages to users who haven't marked as ready."""
        # Find users who aren't ready for each dynasty
        not_ready_users = {}
        for dynasty in DYNASTIES:
            not_ready = [user for user in USERS if not self.storage.is_ready(user, dynasty)]
            if not_ready:
                not_ready_users[dynasty] = not_ready
        
        if not not_ready_users:
            # Everyone is ready, no need to send reminders
            return
        
        # Create reminder embed
        embed = discord.Embed(
            title="Weekly Dynasty Advancement Reminder",
            description="It's time to advance your dynasties! The following users still need to mark as ready:",
            color=discord.Color.gold()
        )
        
        for dynasty, users in not_ready_users.items():
            # Find mentions for each user
            mentions = []
            for user_name in users:
                for guild in self.bot.guilds:
                    member = discord.utils.find(lambda m: m.name == user_name, guild.members)
                    if member:
                        mentions.append(member.mention)
                        break
            
            if mentions:
                embed.add_field(
                    name=f"{dynasty}",
                    value=f"Waiting for: {', '.join(mentions)}",
                    inline=False
                )
        
        # Send reminder to all channels in all guilds
        for guild in self.bot.guilds:
            for channel in guild.text_channels:
                try:
                    await channel.send(embed=embed)
                    # Only send to one channel per guild
                    break
                except discord.Forbidden:
                    continue
                except Exception as e:
                    logger.error(f"Error sending reminder to {channel.name}: {e}")

async def setup(bot):
    """Add the cog to the bot."""
    await bot.add_cog(Reminders(bot))
