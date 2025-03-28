"""
Dynasty tracking cog for the Dynasty Tracker Discord Bot.
This module handles tracking which users are ready to advance
in each dynasty and provides commands to check and reset status.
"""
import discord
from discord.ext import commands
import logging
import asyncio

from config import DYNASTIES, USERS
from utils.storage import DynastyStorage
from utils.embeds import create_status_embed, create_success_embed, create_error_embed

logger = logging.getLogger('dynasty_bot.dynasty_tracker')

class DynastyTracker(commands.Cog):
    """
    A cog for tracking dynasty advancement status.
    """
    def __init__(self, bot):
        self.bot = bot
        self.storage = DynastyStorage()
    
    @commands.Cog.listener()
    async def on_message(self, message):
        """Listen for ready messages in the chat."""
        # Don't process messages from the bot itself
        if message.author == self.bot.user:
            return
        
        # Only process messages in guilds (not DMs)
        if not message.guild:
            return
        
        # Check if the message might be a "ready" message
        content = message.content.upper()
        
        for dynasty in DYNASTIES:
            # Look for messages like "ADHNN READY" or "READY ADHNN"
            if dynasty in content and "READY" in content:
                user = message.author.name
                logger.info(f"Ready message detected from {user} for {dynasty}")
                
                # Check if the user is one of the tracked users by simple partial matching
                matched = False
                for tracked_user in USERS:
                    if tracked_user.upper() in user.upper():
                        await self.mark_ready(message, tracked_user, dynasty)
                        matched = True
                        break
                
                if not matched:
                    logger.warning(f"User not matched: {user} tried to mark ready for {dynasty}")
    
    async def mark_ready(self, message, user, dynasty):
        """Mark a user as ready for a specific dynasty and check if all users are ready."""
        # Update the ready status
        self.storage.set_ready(user, dynasty, True)
        
        # Create embed response
        embed = create_success_embed(
            title=f"🔥 {user} Ready for {dynasty} 🔥",
            description=f"🔥 {user} is now ready to advance in {dynasty}! 🔥"
        )
        
        # Send confirmation and delete the original message
        await message.channel.send(embed=embed)
        try:
            await message.delete()
        except discord.errors.Forbidden:
            logger.warning("Could not delete message: Missing permissions")
        except discord.errors.NotFound:
            logger.warning("Could not delete message: Message not found")
        
        # Check if all users are ready for this dynasty
        all_ready = all(self.storage.is_ready(user, dynasty) for user in USERS)
        if all_ready:
            # Everyone is ready, reset the dynasty and notify
            await self.auto_reset_dynasty(message.channel, dynasty)
    
    async def auto_reset_dynasty(self, channel, dynasty):
        """Reset a dynasty and notify everyone that it's time to advance."""
        # Reset the dynasty
        for user in USERS:
            self.storage.set_ready(user, dynasty, False)
        
        # Create the notification embed
        embed = create_success_embed(
            title=f"{dynasty} Ready to Advance!",
            description="All users are ready to advance!\n\n"
        )
        
        # Add mentions for all users
        mentions = ""
        for user_name in USERS:
            # Find the user in the guild
            for guild in self.bot.guilds:
                member = discord.utils.find(lambda m: user_name.upper() in m.name.upper(), guild.members)
                if member:
                    mentions += f"{member.mention} "
                    logger.info(f"Found member {member.name} for user {user_name}")
                    break
        
        # Send the notification with mentions
        await channel.send(content=mentions, embed=embed)
    
    @commands.command(name="status")
    async def status(self, ctx, dynasty=None):
        """
        Check the ready status of a dynasty or all dynasties.
        
        Usage:
        !status [dynasty]
        
        If dynasty is not specified, displays all dynasties.
        """
        if dynasty:
            # Check if the dynasty exists
            dynasty = dynasty.upper()
            if dynasty not in DYNASTIES:
                embed = create_error_embed(
                    title="Dynasty Not Found",
                    description=f"Dynasty '{dynasty}' not found. Available dynasties: {', '.join(DYNASTIES)}"
                )
                await ctx.send(embed=embed)
                return
            
            # Create status embed for the specific dynasty
            embed = create_status_embed(self.storage, [dynasty])
        else:
            # Create status embed for all dynasties
            embed = create_status_embed(self.storage, DYNASTIES)
        
        await ctx.send(embed=embed)
    
    @commands.command(name="notify")
    async def notify(self, ctx, dynasty=None):
        """
        Notify users who haven't marked as ready yet.
        
        Usage:
        !notify [dynasty]
        
        If dynasty is not specified, checks all dynasties.
        """
        # Get the dynasties to check
        dynasties_to_check = [dynasty.upper()] if dynasty else DYNASTIES
        
        if dynasty and dynasty.upper() not in DYNASTIES:
            embed = create_error_embed(
                title="Dynasty Not Found",
                description=f"Dynasty '{dynasty}' not found. Available dynasties: {', '.join(DYNASTIES)}"
            )
            await ctx.send(embed=embed)
            return
        
        # Create a list of users to notify for each dynasty
        notifications = {}
        for d in dynasties_to_check:
            not_ready = [user for user in USERS if not self.storage.is_ready(user, d)]
            if not_ready:
                notifications[d] = not_ready
        
        if not notifications:
            embed = create_success_embed(
                title="All Caught Up!",
                description="Everyone is ready for all dynasties!"
            )
            await ctx.send(embed=embed)
            return
        
        # Create a notification message
        embed = discord.Embed(
            title="Dynasty Advancement Reminder",
            description="The following users still need to mark as ready:",
            color=discord.Color.gold()
        )
        
        for d, users in notifications.items():
            # Find mentions for the users
            mentions = []
            for user_name in users:
                # Find the user in the guild
                for guild in self.bot.guilds:
                    member = discord.utils.find(lambda m: user_name.upper() in m.name.upper(), guild.members)
                    if member:
                        mentions.append(member.mention)
                        break
            
            if mentions:
                embed.add_field(
                    name=f"{d}",
                    value=f"Waiting for: {', '.join(mentions)}",
                    inline=False
                )
        
        await ctx.send(embed=embed)
    
    @commands.command(name="reset")
    async def reset(self, ctx, dynasty=None):
        """
        Reset the ready status for a dynasty or all dynasties.
        
        Usage:
        !reset [dynasty]
        
        If dynasty is not specified, resets all dynasties.
        """
        if dynasty:
            # Reset a specific dynasty
            dynasty = dynasty.upper()
            if dynasty not in DYNASTIES:
                embed = create_error_embed(
                    title="Dynasty Not Found",
                    description=f"Dynasty '{dynasty}' not found. Available dynasties: {', '.join(DYNASTIES)}"
                )
                await ctx.send(embed=embed)
                return
            
            # Reset the dynasty
            for user in USERS:
                self.storage.set_ready(user, dynasty, False)
            
            embed = create_success_embed(
                title=f"{dynasty} Reset",
                description=f"Ready status for {dynasty} has been reset."
            )
        else:
            # Reset all dynasties
            for d in DYNASTIES:
                for user in USERS:
                    self.storage.set_ready(user, d, False)
            
            embed = create_success_embed(
                title="All Dynasties Reset",
                description="Ready status for all dynasties has been reset."
            )
        
        await ctx.send(embed=embed)
    
    @commands.command(name="dynasty_help")
    async def dynasty_help_command(self, ctx):
        """
        Display help information for the dynasty tracker bot.
        
        Usage:
        !dynasty_help
        """
        prefix = self.bot.command_prefix
        
        embed = discord.Embed(
            title="Dynasty Tracker Bot Help",
            description="Here are the available commands:",
            color=discord.Color.blue()
        )
        
        embed.add_field(
            name=f"{prefix}status [dynasty]",
            value="Check the ready status of a dynasty or all dynasties.",
            inline=False
        )
        
        embed.add_field(
            name=f"{prefix}notify [dynasty]",
            value="Notify users who haven't marked as ready yet.",
            inline=False
        )
        
        embed.add_field(
            name=f"{prefix}reset [dynasty]",
            value="Reset the ready status for a dynasty or all dynasties.",
            inline=False
        )
        
        embed.add_field(
            name=f"{prefix}dynasty_help",
            value="Display this help message.",
            inline=False
        )
        
        embed.add_field(
            name="Marking Ready",
            value="Simply type '[Dynasty] ready' in the channel to mark yourself as ready.\nExample: 'ADHNN ready'",
            inline=False
        )
        
        embed.set_footer(text=f"Use {prefix} before each command. Example: {prefix}status")
        
        await ctx.send(embed=embed)

async def setup(bot):
    """Add the cog to the bot."""
    await bot.add_cog(DynastyTracker(bot))
