"""
Main entry point for the Dynasty Tracker Discord Bot.
This file initializes and runs the bot.
"""
import os
import logging
import discord
from flask import Flask
from threading import Thread

app = Flask(__name__)

@app.route("/")
def home():
    return "Bot is running!"

def run():
    app.run(host="0.0.0.0", port=8080)

def keep_alive():
    server = Thread(target=run)
    server.start()

from dotenv import load_dotenv

from bot import DynastyBot

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('dynasty_bot')

# Load environment variables
load_dotenv()

def main():
    """Main function to start the bot"""
    # Get the bot token from environment variables
    token = os.getenv('DISCORD_TOKEN')
    
    if not token:
        logger.error("No Discord token found. Please add it to your .env file.")
        return
    
    # Initialize and run the bot
    try:
        bot = DynastyBot()
        logger.info("Starting Dynasty Tracker Bot...")
        keep_alive()
        bot.run(token)
    except discord.errors.PrivilegedIntentsRequired:
        logger.error("ERROR: Privileged Intents are required but not enabled in the Discord Developer Portal.")
        logger.error("Please go to https://discord.com/developers/applications/")
        logger.error("Select your bot application, go to the Bot tab, and enable:")
        logger.error("  - MESSAGE CONTENT INTENT")
        logger.error("  - SERVER MEMBERS INTENT")
        logger.error("Then restart the bot.")
    except discord.errors.LoginFailure:
        logger.error("ERROR: Invalid Discord token. Please check your DISCORD_TOKEN in the .env file.")
    except Exception as e:
        logger.error(f"ERROR: An unexpected error occurred: {e}")

if __name__ == "__main__":
    main()

from threading import Thread

# Function to run Flask server in a separate thread
def run_flask():
    keep_alive()

# Start Flask in a new thread, so it doesn’t block the bot
Thread(target=run_flask).start()

# Start the Discord bot
bot.run(TOKEN)
