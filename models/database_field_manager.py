"""
Database Field Manager Module.

This module provides functionality for managing database fields in models.
"""
import logging
from typing import Dict, Any, Optional, List, ClassVar, Type
from pydantic import create_model
from .base_model import BaseModel

logger = logging.getLogger(__name__)


class DatabaseFieldManager:
    """
    Manages database fields and handles schema synchronization.
    
    This class follows the Strategy pattern to provide flexible
    strategies for handling model fields that don't exist in the database.
    """
    
    @classmethod
    def add_field_to_model(cls, model_class: Type[BaseModel], field_name: str, 
                          field_type: Any, default_value: Any = None) -> bool:
        """
        Add a field to a model class and handle database schema synchronization.
        
        Args:
            model_class: The model class to update
            field_name: The name of the field to add
            field_type: The type of the field
            default_value: The default value for the field
            
        Returns:
            True if successful, False otherwise
        """
        try:
            logger.info(f"Adding field {field_name} to {model_class.__name__}")
            
            # Get all existing fields from the model
            fields = {}
            for name, field in model_class.__annotations__.items():
                if not name.startswith('_'):
                    # Get default value if it exists
                    default = getattr(model_class, name, None)
                    fields[name] = (field, default)
            
            # Add the new field
            fields[field_name] = (field_type, default_value)
            
            return True
        except Exception as e:
            logger.error(f"Error adding field to model: {str(e)}")
            return False
    
    @classmethod
    def handle_missing_field(cls, model: BaseModel, field_name: str) -> Dict[str, Any]:
        """
        Handle a missing field in a model when saving to database.
        
        This method modifies the data being sent to the database to exclude fields
        that don't exist in the database schema.
        
        Args:
            model: The model instance being saved
            field_name: The name of the field that's missing in the database
            
        Returns:
            Modified data dictionary excluding the missing field
        """
        logger.warning(f"Field {field_name} not found in database for {model.__class__.__name__}")
        
        # Get model data excluding the missing field
        data = model.model_dump()
        if field_name in data:
            data.pop(field_name)
            
        return data
