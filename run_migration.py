"""
Migration Runner Script.

This script runs database migrations for the Smart Recommendation Engine.
"""
import logging
import os
import sys
from pathlib import Path

# Set up logging
logging.basicConfig(
    level=os.getenv("LOG_LEVEL", "INFO"),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    filename=os.getenv("LOG_FILE", "app.log"),
    filemode="a"
)
logger = logging.getLogger(__name__)

# Add the project root to Python path to enable imports
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from utils.migration_manager import MigrationManager


def run_specific_migration(file_path: str) -> bool:
    """
    Run a specific migration file.
    
    Args:
        file_path: Path to the migration file
        
    Returns:
        True if successful, False otherwise
    """
    migration_manager = MigrationManager()
    return migration_manager.apply_migration(file_path)


def run_all_migrations() -> dict:
    """
    Run all migrations in the migrations directory.
    
    Returns:
        Dictionary with results of each migration
    """
    migration_dir = project_root / "migrations"
    migration_manager = MigrationManager()
    return migration_manager.run_migrations_in_directory(str(migration_dir))


if __name__ == "__main__":
    # Check if specific migration file is provided
    if len(sys.argv) > 1:
        migration_file = sys.argv[1]
        print(f"Running specific migration: {migration_file}")
        success = run_specific_migration(migration_file)
        print(f"Migration {'successful' if success else 'failed'}")
    else:
        # Run all migrations in the directory
        print("Running all migrations...")
        results = run_all_migrations()
        
        # Print results
        success_count = sum(1 for success in results.values() if success)
        total_count = len(results)
        print(f"Completed {success_count}/{total_count} migrations successfully")
        
        # Print failed migrations
        failed = [name for name, success in results.items() if not success]
        if failed:
            print("Failed migrations:")
            for name in failed:
                print(f"  - {name}")
