"""
Base Model Module.

This module defines the base model class that all data models will inherit from.
It implements the Active Record pattern for database operations.
"""
import logging
import json
from datetime import datetime
from typing import Dict, List, Any, Optional, Type, TypeVar, Generic, ClassVar
from pydantic import BaseModel as PydanticBaseModel

logger = logging.getLogger(__name__)

# Custom JSON encoder for handling datetime objects
class DateTimeEncoder(json.JSONEncoder):
    """
    Custom JSON encoder that serializes datetime objects to ISO format strings.
    Follows the Single Responsibility Principle by handling only datetime serialization.
    """
    def default(self, obj):
        if isinstance(obj, datetime):
            return obj.isoformat()
        return super().default(obj)

T = TypeVar('T', bound='BaseModel')


class BaseModel(PydanticBaseModel):
    """
    Base model implementing Active Record pattern with Supabase integration.
    
    All data models in the application inherit from this class.
    """
    
    # Class variables to be overridden by subclasses
    _table_name: ClassVar[str] = ""
    id: Optional[int] = None
    
    class Config:
        """Pydantic configuration."""
        arbitrary_types_allowed = True
    
    @classmethod
    def _get_db(cls) -> Any:
        """
        Get the database connection.
        
        Returns:
            The database client
        """
        # Import inside method to avoid circular imports
        from utils.db_manager import DatabaseManager
        return DatabaseManager().client
    
    @classmethod
    def find_by_id(cls: Type[T], item_id: int) -> Optional[T]:
        """
        Find an item by its ID.
        
        Args:
            item_id: The ID of the item to find
            
        Returns:
            The found item or None if not found
        """
        logger.info(f"Finding {cls.__name__} with ID {item_id}")
        try:
            response = cls._get_db().table(cls._table_name).select("*").eq("id", item_id).execute()
            if response.data and len(response.data) > 0:
                logger.debug(f"Found {cls.__name__} with ID {item_id}")
                return cls(**response.data[0])
            logger.warning(f"No {cls.__name__} found with ID {item_id}")
            return None
        except Exception as e:
            logger.error(f"Error finding {cls.__name__} with ID {item_id}: {str(e)}")
            raise
    
    @classmethod
    def find_all(cls: Type[T]) -> List[T]:
        """
        Find all items in the table.
        
        Returns:
            A list of all items
        """
        logger.info(f"Finding all {cls.__name__} records")
        try:
            response = cls._get_db().table(cls._table_name).select("*").execute()
            items = [cls(**item) for item in response.data]
            logger.debug(f"Found {len(items)} {cls.__name__} records")
            return items
        except Exception as e:
            logger.error(f"Error finding all {cls.__name__} records: {str(e)}")
            raise
    
    @classmethod
    def find_by(cls: Type[T], **criteria) -> List[T]:
        """
        Find items matching the given criteria.
        
        Args:
            **criteria: Field-value pairs to match against
            
        Returns:
            A list of matching items
        """
        logger.info(f"Finding {cls.__name__} records by criteria: {criteria}")
        try:
            query = cls._get_db().table(cls._table_name).select("*")
            
            # Apply each criterion to the query
            for field, value in criteria.items():
                query = query.eq(field, value)
                
            response = query.execute()
            items = [cls(**item) for item in response.data]
            logger.debug(f"Found {len(items)} {cls.__name__} records matching criteria")
            return items
        except Exception as e:
            logger.error(f"Error finding {cls.__name__} records by criteria: {str(e)}")
            raise
    
    def save(self) -> 'BaseModel':
        """
        Save the current model instance to the database.
        
        If id is None, creates a new record, otherwise updates the existing one.
        This method handles proper serialization of datetime objects for database compatibility.
        
        Returns:
            The saved model instance with updated ID if created
        """
        # Get model data excluding ID for new records
        data = self.model_dump(exclude={"id"} if self.id is None else {})
        
        try:
            # Prepare data for the database
            data = self._prepare_data_for_db()
            
            # Execute database operation
            db = self._get_db()
            if self.id:
                # Update existing record
                logger.info(f"Updating {self.__class__.__name__} with ID {self.id}")
                result = None
                try:
                    result = db.table(self._table_name).update(data).eq("id", self.id).execute()
                except Exception as field_error:
                    # Check if error is about missing column
                    error_msg = str(field_error)
                    if "Could not find" in error_msg and "column" in error_msg and "in the schema cache" in error_msg:
                        # Extract the field name from error message
                        import re
                        match = re.search(r"Could not find the '(.+?)' column", error_msg)
                        if match:
                            field_name = match.group(1)
                            logger.warning(f"Field '{field_name}' does not exist in database schema for {self.__class__.__name__}")
                            
                            # Remove the field from data and try again
                            if field_name in data:
                                data.pop(field_name)
                                logger.info(f"Retrying update without field '{field_name}'")
                                result = db.table(self._table_name).update(data).eq("id", self.id).execute()
                        else:
                            raise
                    else:
                        raise
            else:
                # Insert new record
                logger.info(f"Inserting new {self.__class__.__name__}")
                result = None
                try:
                    result = db.table(self._table_name).insert(data).execute()
                except Exception as field_error:
                    # Check if error is about missing column
                    error_msg = str(field_error)
                    if "Could not find" in error_msg and "column" in error_msg and "in the schema cache" in error_msg:
                        # Extract the field name from error message
                        import re
                        match = re.search(r"Could not find the '(.+?)' column", error_msg)
                        if match:
                            field_name = match.group(1)
                            logger.warning(f"Field '{field_name}' does not exist in database schema for {self.__class__.__name__}")
                            
                            # Remove the field from data and try again
                            if field_name in data:
                                data.pop(field_name)
                                logger.info(f"Retrying insert without field '{field_name}'")
                                result = db.table(self._table_name).insert(data).execute()
                        else:
                            raise
                    else:
                        raise
                
                # Update the model ID with the newly inserted ID
                if result and hasattr(result, 'data') and result.data and len(result.data) > 0:
                    self.id = result.data[0].get("id")
                
            return self
        except Exception as e:
            logger.error(f"Error saving {self.__class__.__name__}: {str(e)}")
            raise
    
    def _prepare_data_for_db(self, data: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Prepare data for database storage by handling special types like datetime.
        
        Args:
            data: Dictionary containing model data (if None, will use model_dump)
            
        Returns:
            Data dictionary with all values serialized for database storage
        """
        # If no data provided, get it from the model
        if data is None:
            # Exclude ID for new records
            exclude_fields = {"id"} if self.id is None else set()
            data = self.model_dump(exclude=exclude_fields)
        else:
            # Make a copy to avoid modifying the input
            data = {**data}
        
        # Process each field for serialization
        result = {}
        for key, value in data.items():
            # Skip fields that start with underscore (private fields)
            if key.startswith('_'):
                continue
                
            # Handle datetime objects (convert to ISO format string)
            if isinstance(value, datetime):
                result[key] = value.isoformat()
            # Handle nested dictionaries
            elif isinstance(value, dict):
                result[key] = self._prepare_data_for_db(value)
            # Handle lists with potential datetime objects
            elif isinstance(value, list):
                result[key] = [item.isoformat() if isinstance(item, datetime) else item for item in value]
            else:
                result[key] = value
                
        return result
    
    def delete(self) -> bool:
        """
        Delete the current model instance from the database.
        
        Returns:
            True if deletion was successful, False otherwise
        """
        if self.id is None:
            logger.warning("Cannot delete unsaved model instance")
            return False
            
        logger.info(f"Deleting {self.__class__.__name__} with ID {self.id}")
        try:
            self._get_db().table(self._table_name).delete().eq("id", self.id).execute()
            logger.debug(f"Deleted {self.__class__.__name__} with ID {self.id}")
            self.id = None
            return True
        except Exception as e:
            logger.error(f"Error deleting {self.__class__.__name__} with ID {self.id}: {str(e)}")
            raise
