"""
Embed utility functions for the Dynasty Tracker Discord Bot.
Handles creation of various embed messages.
"""
import discord

def create_status_embed(storage, dynasties):
    """
    Create an embed showing the status of the specified dynasties.
    
    Args:
        storage: The DynastyStorage instance
        dynasties: List of dynasty names to include
    
    Returns:
        discord.Embed: The formatted status embed
    """
    embed = discord.Embed(
        title="Dynasty Advancement Status",
        description="Current advancement status for each dynasty:",
        color=discord.Color.blue()
    )
    
    for dynasty in dynasties:
        status = storage.get_dynasty_status(dynasty)
        
        if not status:
            continue
        
        # Format the status as a list with emoji indicators
        status_lines = []
        for user, ready in status.items():
            emoji = "✅" if ready else "⏳"
            status_lines.append(f"{emoji} {user}")
        
        # Add the field for this dynasty
        embed.add_field(
            name=dynasty,
            value="\n".join(status_lines) or "No users tracked",
            inline=True
        )
    
    return embed

def create_success_embed(title, description):
    """
    Create a success embed with the given title and description.
    
    Args:
        title: The embed title
        description: The embed description
    
    Returns:
        discord.Embed: The formatted success embed
    """
    return discord.Embed(
        title=title,
        description=description,
        color=discord.Color.green()
    )

def create_error_embed(title, description):
    """
    Create an error embed with the given title and description.
    
    Args:
        title: The embed title
        description: The embed description
    
    Returns:
        discord.Embed: The formatted error embed
    """
    return discord.Embed(
        title=title,
        description=description,
        color=discord.Color.red()
    )

def create_reminder_embed(not_ready_users):
    """
    Create a reminder embed for users who are not ready.
    
    Args:
        not_ready_users: Dictionary mapping dynasties to lists of users who aren't ready
    
    Returns:
        discord.Embed: The formatted reminder embed
    """
    embed = discord.Embed(
        title="Dynasty Advancement Reminder",
        description="The following users still need to mark as ready:",
        color=discord.Color.gold()
    )
    
    for dynasty, users in not_ready_users.items():
        if users:
            embed.add_field(
                name=dynasty,
                value=", ".join(users),
                inline=False
            )
    
    return embed
