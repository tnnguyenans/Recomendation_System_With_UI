#!/usr/bin/env python3
"""
Unit tests for UserModel password handling and validation.

This test suite validates the password hashing, validation, and
circular import resolution in the UserModel class.
"""
import unittest
import os
import sys
from unittest.mock import patch, MagicMock

# Add project root to path so we can import modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from models.user_model import UserModel


class TestUserModel(unittest.TestCase):
    """Test cases for UserModel functionality.
    
    Tests password handling, validation, and model creation.
    """
    
    def setUp(self):
        """Set up test environment before each test case."""
        self.user_data = {
            'username': 'testuser',
            'email': 'test@example.com',
            'password': 'SecurePass123',
            'first_name': 'Test',
            'last_name': 'User'
        }
    
    def test_password_validation(self):
        """Test that plain password is correctly hashed during validation."""
        # Create a user with a plain password
        user = UserModel(**self.user_data)
        
        # Check that password_hash was created
        self.assertIsNotNone(user.password_hash)
        self.assertTrue(len(user.password_hash) > 20)  # Should be a long hash
        self.assertNotEqual(user.password_hash, 'SecurePass123')  # Should not be plain text
        
    def test_password_hash_preserved(self):
        """Test that existing password_hash is not overwritten."""
        # Create a user with a pre-hashed password
        hashed_data = self.user_data.copy()
        hashed_data['password_hash'] = 'existing_hash_value'
        del hashed_data['password']  # Remove plain password
        
        user = UserModel(**hashed_data)
        
        # Check that the existing hash was preserved
        self.assertEqual(user.password_hash, 'existing_hash_value')
    
    def test_password_not_stored(self):
        """Test that plain password is not stored in the model."""
        # Create a user with a plain password
        user = UserModel(**self.user_data)
        
        # The password should be None after initialization
        # as it's transient and only used for hashing
        self.assertIsNone(user.password)
    
    @patch('utils.auth.AuthenticationManager')
    def test_lazy_import_usage(self, mock_auth_manager):
        """Test that AuthenticationManager is lazily imported."""
        # Setup the mock
        mock_auth_manager.hash_password.return_value = 'mocked_hash_value'
        
        # Create a user which should trigger the lazy import
        user_data = self.user_data.copy()
        user = UserModel(**user_data)
        
        # Verify the mock was called
        mock_auth_manager.hash_password.assert_called_once_with('SecurePass123')
        self.assertEqual(user.password_hash, 'mocked_hash_value')
    
    @patch('models.base_model.BaseModel._get_db')
    def test_save_method(self, mock_get_db):
        """Test that saving a UserModel serializes correctly."""
        # Setup the mock database client
        mock_client = MagicMock()
        mock_get_db.return_value = mock_client
        
        # Setup the mock response chain
        mock_execute = MagicMock()
        mock_execute.data = [{'id': 1}]
        
        mock_eq = MagicMock()
        mock_eq.execute = MagicMock(return_value=mock_execute)
        
        mock_update = MagicMock()
        mock_update.eq = MagicMock(return_value=mock_eq)
        
        mock_table_instance = MagicMock()
        mock_table_instance.update = MagicMock(return_value=mock_update)
        mock_table_instance.insert = MagicMock()
        mock_table_instance.insert.execute = MagicMock(return_value=mock_execute)
        
        mock_client.table = MagicMock(return_value=mock_table_instance)
        
        # Create and save a user
        user = UserModel(**self.user_data)
        user.save()
        
        # Get the data that would be sent to the database
        # Since the model has an ID (from UserModel(**self.user_data)),
        # it will use the update path instead of insert
        args, _ = mock_table_instance.update.call_args
        serialized_data = args[0]
        
        # Verify no plain password in serialized data
        self.assertNotIn('password', serialized_data)
        self.assertIn('password_hash', serialized_data)
        
    @patch('models.user_model.UserModel.find_by_id')
    @patch('models.base_model.BaseModel._get_db')
    def test_find_by_username(self, mock_get_db, mock_find_by_id):
        """Test finding user by username."""
        # Setup the mock
        mock_user = MagicMock(username='testuser')
        mock_find_by_id.return_value = mock_user
        
        # Setup the mock database client
        mock_client = MagicMock()
        mock_get_db.return_value = mock_client
        
        # Setup the mock database response with all required fields
        mock_execute = MagicMock()
        mock_execute.data = [{
            'id': 1,
            'username': 'testuser',
            'email': 'test@example.com',
            'password_hash': 'hashed_password',
            'created_at': datetime.now().isoformat(),
            'is_active': True
        }]
        
        mock_eq = MagicMock()
        mock_eq.execute = MagicMock(return_value=mock_execute)
        
        mock_select = MagicMock()
        mock_select.eq = MagicMock(return_value=mock_eq)
        
        mock_table = MagicMock()
        mock_table.select = MagicMock(return_value=mock_select)
        
        mock_client.table = MagicMock(return_value=mock_table)
        
        # Call the method
        result = UserModel.find_by_username('testuser')
        
        # Verify the result
        self.assertEqual(result, mock_user)


if __name__ == '__main__':
    unittest.main()
