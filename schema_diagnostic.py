"""
Schema Diagnostic Tool.

This script diagnoses database schema issues and generates reports
for the Smart Recommendation Engine project.
"""
import logging
import os
import sys
from pathlib import Path

# Set up logging
logging.basicConfig(
    level=os.getenv("LOG_LEVEL", "INFO"),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout),  # Log to console
        logging.FileHandler(os.getenv("LOG_FILE", "app.log"))  # Log to file
    ]
)
logger = logging.getLogger(__name__)

# Add the project root to Python path to enable imports
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from utils.schema_manager import DatabaseSchemaManager
from utils.db_manager import DatabaseManager


def check_schema_status():
    """Check the status of the database schema and print a report."""
    print("===== Database Schema Diagnostic Tool =====")
    print("Connecting to database...")
    
    # Initialize managers
    db_manager = DatabaseManager()
    schema_manager = DatabaseSchemaManager()
    
    print("Refreshing schema cache...")
    tables = schema_manager.refresh_schema_cache()
    
    print(f"Found {len(tables)} tables in the database.\n")
    
    # Print table structure
    print("===== Table Structure =====")
    for table_name, columns in tables.items():
        print(f"\nTable: {table_name}")
        print("Columns:")
        for col in sorted(columns):
            print(f"  - {col}")
    
    print("\n===== Missing Fields Report =====")
    missing_fields = schema_manager.get_missing_fields()
    if not missing_fields:
        print("No missing fields recorded. Run the application first to detect schema mismatches.")
    else:
        for table, fields in missing_fields.items():
            if not fields:
                continue
                
            print(f"\nTable: {table}")
            print("Missing Fields:")
            for field in sorted(fields):
                print(f"  - {field}")
    
    print("\n===== Generated Migration SQL =====")
    migrations = schema_manager.generate_migration_sql()
    if not migrations:
        print("No migrations needed.")
    else:
        for table, sql in migrations.items():
            print(f"\nFor table '{table}':")
            print(f"```sql\n{sql}\n```")
            
            # Save migration file
            migration_dir = project_root / "migrations"
            migration_dir.mkdir(exist_ok=True)
            
            filename = f"add_missing_fields_to_{table}.sql"
            migration_path = migration_dir / filename
            
            with open(migration_path, "w") as f:
                f.write(sql)
            
            print(f"Migration file saved to: {migration_path}")
    
    print("\n===== How to Apply Migrations =====")
    print("To apply these migrations in Supabase:")
    print("1. Log in to your Supabase project dashboard")
    print("2. Go to the SQL Editor")
    print("3. Copy and paste the SQL statements above")
    print("4. Click 'Run' to execute the migrations")
    print("5. Refresh the schema cache in your application")


if __name__ == "__main__":
    check_schema_status()
