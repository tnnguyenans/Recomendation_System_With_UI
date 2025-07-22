#!/usr/bin/env python3
"""
Unit tests for BaseModel serialization and datetime handling.

This test suite validates the proper serialization/deserialization of
BaseModel instances, with particular focus on datetime field handling.
"""
import unittest
import os
import sys
from datetime import datetime, timezone
import json
from typing import Optional, Dict, Any
from unittest.mock import patch, MagicMock
from pydantic import ConfigDict

# Add project root to path so we can import modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from models.base_model import BaseModel


class TestBaseModelSerialization(unittest.TestCase):
    """Test cases for BaseModel serialization capabilities.
    
    Focuses on datetime handling in the save method and JSON serialization.
    """
    
    def setUp(self):
        """Set up test environment before each test case."""
        # Create a concrete subclass of BaseModel for testing
        class TestModel(BaseModel):
            _table_name = "test_table"
            
            id: Optional[int] = None
            name: Optional[str] = None
            created_at: datetime = datetime.now(timezone.utc)
            updated_at: Optional[datetime] = None
            date_field: Optional[datetime] = None
            
            model_config = ConfigDict(arbitrary_types_allowed=True)
                
        self.TestModel = TestModel
        self.test_datetime = datetime(2025, 7, 22, 12, 0, 0, tzinfo=timezone.utc)
        
        # Create a test instance
        self.model = self.TestModel(
            id=1,
            name="Test",
            created_at=self.test_datetime,
            updated_at=self.test_datetime,
            date_field=None
        )
    
    @patch('utils.db_manager.DatabaseManager')
    def test_datetime_serialization(self, mock_db_manager):
        """Test that datetime fields are correctly serialized when saving."""
        # Setup the mock for database connection
        mock_instance = MagicMock()
        mock_db_manager.return_value = mock_instance
        mock_client = MagicMock()
        mock_instance.client = mock_client
        
        # Setup the mock for database operations with chained method calls
        mock_execute = MagicMock()
        
        # Since the model has ID=1, it will use update() instead of insert()
        mock_eq = MagicMock()
        mock_eq.execute = MagicMock(return_value=mock_execute)
        
        mock_update = MagicMock()
        mock_update.eq = MagicMock(return_value=mock_eq)
        
        mock_table_instance = MagicMock()
        mock_table_instance.update = MagicMock(return_value=mock_update)
        
        mock_client.table = MagicMock(return_value=mock_table_instance)
        
        # Execute the save method
        self.model.save()
        
        # Get the data that would be sent to the database
        args, _ = mock_table_instance.update.call_args
        serialized_data = args[0]
        
        # Verify datetime fields are serialized as strings
        self.assertTrue(isinstance(serialized_data['created_at'], str))
        self.assertTrue(isinstance(serialized_data['updated_at'], str))
        self.assertEqual(serialized_data['date_field'], None)  # None should remain None
        
        # Verify the datetime format is ISO 8601
        expected_dt_str = self.test_datetime.isoformat()
        self.assertEqual(serialized_data['created_at'], expected_dt_str)
        self.assertEqual(serialized_data['updated_at'], expected_dt_str)
    
    def test_dict_representation(self):
        """Test that the model can be properly converted to a dictionary."""
        model_dict = self.model.model_dump()
        
        # Check all fields are present
        self.assertEqual(model_dict['id'], 1)
        self.assertEqual(model_dict['name'], "Test")
        self.assertTrue(isinstance(model_dict['created_at'], datetime))
        self.assertTrue(isinstance(model_dict['updated_at'], datetime))
        self.assertIsNone(model_dict['date_field'])
        
    def test_json_serialization(self):
        """Test that the model can be serialized to JSON."""
        # Convert to dict and then serialize
        model_dict = self.model.model_dump()
        
        # This should raise an error without our custom serialization
        with self.assertRaises(TypeError):
            json.dumps(model_dict)
            
        # Now with our custom serializer
        from models.base_model import DateTimeEncoder
        json_str = json.dumps(model_dict, cls=DateTimeEncoder)
        
        # Deserialize and check
        deserialized = json.loads(json_str)
        self.assertEqual(deserialized['id'], 1)
        self.assertEqual(deserialized['name'], "Test")
        self.assertTrue(isinstance(deserialized['created_at'], str))
        self.assertTrue(isinstance(deserialized['updated_at'], str))
        self.assertIsNone(deserialized['date_field'])


if __name__ == '__main__':
    unittest.main()
