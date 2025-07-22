"""
Database Schema Manager Module.

This module provides functionality for tracking and managing database schema status.
"""
import logging
import os
from typing import Dict, List, Any, Optional, Set
from .db_manager import DatabaseManager

logger = logging.getLogger(__name__)


class DatabaseSchemaManager:
    """
    Singleton class for managing database schema status and providing information
    about field compatibility between models and database tables.
    """
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(DatabaseSchemaManager, cls).__new__(cls)
            cls._instance._initialize()
        return cls._instance
    
    def _initialize(self):
        """Initialize the schema manager."""
        self.db = DatabaseManager().client
        self._table_columns = {}
        self._missing_fields = {}
        
    def refresh_schema_cache(self) -> Dict[str, List[str]]:
        """
        Refresh the schema cache by querying the database for all tables and columns.
        
        Returns:
            Dictionary mapping table names to lists of column names
        """
        try:
            logger.info("Refreshing database schema cache")
            # This is the most compatible way to get schema info from Supabase
            # Get schema for all tables
            tables_info = {}
            
            # Get information about all tables in the public schema
            # Note: This uses PostgreSQL system tables through the REST API
            response = self.db.table("information_schema.columns") \
                .select("table_name,column_name") \
                .eq("table_schema", "public") \
                .execute()
            
            if hasattr(response, 'data'):
                # Process the response into our table_columns cache
                for column_info in response.data:
                    table_name = column_info.get('table_name')
                    column_name = column_info.get('column_name')
                    
                    if table_name not in tables_info:
                        tables_info[table_name] = []
                    
                    tables_info[table_name].append(column_name)
                
                self._table_columns = tables_info
                logger.info(f"Schema cache refreshed, found {len(tables_info)} tables")
                return tables_info
            else:
                logger.error("Failed to get schema information from database")
                return {}
        except Exception as e:
            logger.error(f"Error refreshing schema cache: {str(e)}")
            return {}
    
    def get_table_columns(self, table_name: str) -> List[str]:
        """
        Get all column names for a specific table.
        
        Args:
            table_name: Name of the table
            
        Returns:
            List of column names
        """
        # Refresh cache if this table isn't in our cache yet
        if not self._table_columns or table_name not in self._table_columns:
            self.refresh_schema_cache()
        
        return self._table_columns.get(table_name, [])
    
    def register_missing_field(self, table_name: str, field_name: str):
        """
        Register a missing field for a table, used for tracking schema mismatches.
        
        Args:
            table_name: Name of the table
            field_name: Name of the missing field
        """
        if table_name not in self._missing_fields:
            self._missing_fields[table_name] = set()
            
        self._missing_fields[table_name].add(field_name)
        logger.info(f"Registered missing field: {field_name} in table {table_name}")
    
    def get_missing_fields(self, table_name: Optional[str] = None) -> Dict[str, Set[str]]:
        """
        Get all missing fields, optionally filtered by table name.
        
        Args:
            table_name: Optional table name to filter by
            
        Returns:
            Dictionary mapping table names to sets of missing field names
        """
        if table_name:
            return {table_name: self._missing_fields.get(table_name, set())}
        return self._missing_fields
    
    def generate_migration_sql(self, table_name: Optional[str] = None) -> Dict[str, str]:
        """
        Generate SQL statements to add missing fields to tables.
        
        Args:
            table_name: Optional table name to generate SQL for
            
        Returns:
            Dictionary mapping table names to SQL statements
        """
        migrations = {}
        missing_fields = self.get_missing_fields(table_name)
        
        for tbl, fields in missing_fields.items():
            if not fields:
                continue
                
            sql_parts = [f"-- Add missing columns to {tbl} table"]
            for field in sorted(fields):
                # Default to TEXT for missing fields since we don't know the desired type
                sql_parts.append(f"ALTER TABLE {tbl} ADD COLUMN IF NOT EXISTS {field} TEXT;")
                
            migrations[tbl] = "\n".join(sql_parts)
            
        return migrations
    
    def check_field_exists(self, table_name: str, field_name: str) -> bool:
        """
        Check if a field exists in a table.
        
        Args:
            table_name: Name of the table
            field_name: Name of the field
            
        Returns:
            True if the field exists, False otherwise
        """
        columns = self.get_table_columns(table_name)
        return field_name in columns
