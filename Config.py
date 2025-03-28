"""
Configuration settings for the Dynasty Tracker Discord Bot.
"""
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Bot command prefix
PREFIX = os.getenv('COMMAND_PREFIX', '$')

# Initial cogs/extensions to load
INITIAL_EXTENSIONS = [
    'cogs.dynasty_tracker',
    'cogs.reminders'
]

# Dynasty information
DYNASTIES = [
    'ADHNN',
    'ADHOC',
    'ADTBB',
    'ADTBS'
]

# Users to track
USERS = [
    'Samsonite000',
    'chaseisntonfire',
    'Nmatt73'
]

# Default data file path
DATA_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data', 'dynasties.json')

# Time zone for reminders (Central Time)
TIMEZONE = 'US/Central'

# The day and time for weekly reminders (Saturday 9:00 AM Central)
REMINDER_DAY = 5  # Saturday (0 is Monday, 6 is Sunday)
REMINDER_HOUR = 9  # 9 AM
REMINDER_MINUTE = 0  # 0 minutes
