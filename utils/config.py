"""
Configuration Module.

This module provides configuration settings for the recommendation system.
"""
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Supabase configuration
SUPABASE_URL = os.getenv('SUPABASE_URL', '')
SUPABASE_KEY = os.getenv('SUPABASE_KEY', '')

# Application settings
APP_TITLE = "Smart Recommendation Engine"
APP_DESCRIPTION = "A sophisticated recommendation application with multiple algorithm strategies"
APP_VERSION = "1.0.0"

# UI settings
THEME_COLOR = "#FF4B4B"
DEFAULT_AVATAR = "https://www.gravatar.com/avatar/00000000000000000000000000000000?d=mp&f=y"

# Recommendation settings
DEFAULT_RECOMMENDATION_COUNT = 10
DEFAULT_RECOMMENDATION_STRATEGY = "hybrid"
AVAILABLE_STRATEGIES = {
    "collaborative": "Collaborative Filtering",
    "content-based": "Content-Based Filtering",
    "hybrid": "Hybrid Filtering"
}

# Password security
PASSWORD_MIN_LENGTH = 8
PASSWORD_HASH_ALGORITHM = "pbkdf2_sha256"
PASSWORD_SALT_LENGTH = 32
PASSWORD_HASH_ITERATIONS = 100000
