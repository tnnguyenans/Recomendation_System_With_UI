"""
Database Manager Module.

This module implements the Singleton Pattern for managing database connections.
"""
import os
import logging
from typing import Optional
from dotenv import load_dotenv
from supabase import create_client, Client

# Configure logging
logging.basicConfig(
    level=os.getenv("LOG_LEVEL", "INFO"),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    filename=os.getenv("LOG_FILE", "app.log"),
    filemode="a"
)
logger = logging.getLogger(__name__)


class DatabaseManager:
    """
    Singleton class for managing Supabase database connections.
    
    This class ensures only one database connection is created and reused
    throughout the application.
    """
    _instance: Optional["DatabaseManager"] = None
    _client: Optional[Client] = None
    
    def __new__(cls) -> "DatabaseManager":
        """Create or return the singleton instance of DatabaseManager."""
        if cls._instance is None:
            logger.info("Creating new DatabaseManager instance")
            cls._instance = super(DatabaseManager, cls).__new__(cls)
            cls._instance._initialize()
        return cls._instance
    
    def _initialize(self) -> None:
        """Initialize the Supabase client connection."""
        try:
            # Load environment variables
            load_dotenv()
            
            # Get Supabase credentials
            supabase_url = os.getenv("SUPABASE_URL")
            supabase_key = os.getenv("SUPABASE_KEY")
            
            if not supabase_url or not supabase_key:
                logger.error("Supabase credentials not found in environment variables")
                raise ValueError(
                    "Missing Supabase credentials. Please set SUPABASE_URL and SUPABASE_KEY."
                )
            
            # Initialize Supabase client
            self._client = create_client(supabase_url, supabase_key)
            logger.info("Supabase client initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize Supabase client: {str(e)}")
            raise
    
    @property
    def client(self) -> Client:
        """Get the Supabase client instance."""
        if self._client is None:
            logger.error("Attempting to access uninitialized Supabase client")
            raise RuntimeError("Supabase client is not initialized")
        return self._client
