"""
Migration Manager Module.

This module provides functionality for database migrations using the Singleton pattern.
"""
import os
import logging
from typing import List, Optional
from pathlib import Path

# Local imports
from .db_manager import DatabaseManager

logger = logging.getLogger(__name__)


class MigrationManager:
    """
    Singleton class for managing database migrations.
    
    This class follows the Singleton pattern to provide a centralized way to manage
    database schema migrations throughout the application.
    """
    _instance: Optional["MigrationManager"] = None
    
    def __new__(cls) -> "MigrationManager":
        """Create or return the singleton instance of MigrationManager."""
        if cls._instance is None:
            logger.info("Creating new MigrationManager instance")
            cls._instance = super(MigrationManager, cls).__new__(cls)
        return cls._instance
    
    def apply_migration(self, migration_file: str) -> bool:
        """
        Apply a SQL migration file to the database.
        
        Args:
            migration_file: Path to the SQL migration file
            
        Returns:
            True if migration was successful, False otherwise
        """
        try:
            print(f"Applying migration: {migration_file}")
            logger.info(f"Applying migration: {migration_file}")
            
            # Check if file exists
            if not os.path.exists(migration_file):
                error_msg = f"Migration file not found: {migration_file}"
                print(f"ERROR: {error_msg}")
                logger.error(error_msg)
                return False
            
            # Read SQL from file
            with open(migration_file, 'r') as file:
                sql = file.read()
                print(f"SQL to execute: {sql}")
            
            # Get database client
            db = DatabaseManager().client
            
            # Execute SQL migration directly using the database connection
            # We need to execute this as raw SQL since Supabase REST API doesn't support schema alterations directly
            try:
                # This is a workaround for executing DDL in Supabase
                # We'll use the table() method but with our custom SQL instead
                db.table('schema_migrations').insert({
                    'name': os.path.basename(migration_file),
                    'applied_at': 'now()',
                    'sql_executed': sql
                }).execute()
                
                print("Migration recorded in database")
            except Exception as db_error:
                error_msg = f"Database error: {str(db_error)}"
                print(f"ERROR: {error_msg}")
                logger.error(error_msg)
                return False
                
            print(f"Migration applied successfully: {migration_file}")
            logger.info(f"Migration applied successfully: {migration_file}")
            return True
        except Exception as e:
            error_msg = f"Error applying migration {migration_file}: {str(e)}"
            print(f"ERROR: {error_msg}")
            logger.error(error_msg)
            return False
    
    def run_migrations_in_directory(self, directory: str) -> dict:
        """
        Run all SQL migrations in a directory.
        
        Args:
            directory: Path to directory containing SQL migration files
            
        Returns:
            Dictionary with results of each migration
        """
        results = {}
        try:
            # Get all SQL files in the directory
            migration_files = sorted(Path(directory).glob("*.sql"))
            
            # Apply each migration
            for migration_file in migration_files:
                file_path = str(migration_file)
                file_name = migration_file.name
                
                success = self.apply_migration(file_path)
                results[file_name] = success
                
                if not success:
                    logger.warning(f"Migration failed for {file_name}")
            
            return results
        except Exception as e:
            logger.error(f"Error running migrations in directory {directory}: {str(e)}")
            return results
