"""
Storage utilities for the Dynasty Tracker Discord Bot.
Handles persistence of dynasty advancement status.
"""
import os
import json
import logging
import threading
from threading import Lock

from config import DYNASTIES, USERS, DATA_PATH

logger = logging.getLogger('dynasty_bot.storage')

class DynastyStorage:
    """
    Handles storage and retrieval of dynasty advancement status.
    """
    _instance = None
    _initialized = False
    _lock = Lock()
    
    def __new__(cls):
        """Implement singleton pattern."""
        if cls._instance is None:
            cls._instance = super(DynastyStorage, cls).__new__(cls)
        return cls._instance
    
    def __init__(self):
        """Initialize the storage."""
        # Only initialize once
        if DynastyStorage._initialized:
            return
        
        self.data_path = DATA_PATH
        self.data = {}
        
        # Initialize the data structure if it doesn't exist
        if not os.path.exists(os.path.dirname(self.data_path)):
            os.makedirs(os.path.dirname(self.data_path))
        
        # Load data from file or create default data
        self._load_data()
        
        DynastyStorage._initialized = True
    
    def _load_data(self):
        """Load data from the JSON file or create default data."""
        try:
            if os.path.exists(self.data_path):
                with open(self.data_path, 'r') as f:
                    self.data = json.load(f)
                logger.info(f"Loaded data from {self.data_path}")
            else:
                self._create_default_data()
                self._save_data()
                logger.info(f"Created default data at {self.data_path}")
        except Exception as e:
            logger.error(f"Error loading data: {e}")
            self._create_default_data()
            self._save_data()
    
    def _create_default_data(self):
        """Create default data structure."""
        self.data = {}
        for dynasty in DYNASTIES:
            self.data[dynasty] = {}
            for user in USERS:
                self.data[dynasty][user] = False
    
    def _save_data(self):
        """Save data to the JSON file via background thread."""
        # Use the background method to avoid blocking the main thread
        save_thread = threading.Thread(target=self._save_data_background)
        save_thread.daemon = True
        save_thread.start()
    
    def is_ready(self, user, dynasty):
        """Check if a user is ready for a specific dynasty."""
        dynasty = dynasty.upper()
        
        # Ensure the dynasty and user exist in the data
        if dynasty not in self.data:
            logger.error(f"Dynasty {dynasty} not found in data")
            return False
        
        if user not in self.data[dynasty]:
            logger.error(f"User {user} not found in dynasty {dynasty} data")
            return False
        
        return self.data[dynasty][user]
    
    def set_ready(self, user, dynasty, ready=True):
        """Mark a user as ready or not ready for a specific dynasty."""
        dynasty = dynasty.upper()
        
        # Ensure the dynasty and user exist in the data
        if dynasty not in self.data:
            logger.error(f"Dynasty {dynasty} not found in data")
            return False
        
        if user not in self.data[dynasty]:
            logger.error(f"User {user} not found in dynasty {dynasty} data")
            return False
        
        # Update the ready status in memory (don't block to save)
        with self._lock:
            self.data[dynasty][user] = ready
        
        # Save via the _save_data method which is already non-blocking
        self._save_data()
        
        return True
        
    def _save_data_background(self):
        """Save data to the JSON file in a background thread."""
        try:
            with self._lock:
                data_copy = self.data.copy()
                
            # Save the data outside the lock to avoid blocking
            with open(self.data_path, 'w') as f:
                json.dump(data_copy, f, indent=4)
                
            logger.debug(f"Saved data to {self.data_path}")
        except Exception as e:
            logger.error(f"Error saving data: {e}")
    
    def get_dynasty_status(self, dynasty):
        """Get the ready status for all users in a specific dynasty."""
        dynasty = dynasty.upper()
        
        if dynasty not in self.data:
            logger.error(f"Dynasty {dynasty} not found in data")
            return {}
        
        return self.data[dynasty].copy()
    
    def get_all_statuses(self):
        """Get the ready status for all dynasties."""
        return self.data.copy()
