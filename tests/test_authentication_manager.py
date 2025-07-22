#!/usr/bin/env python3
"""
Unit tests for AuthenticationManager class.

This test suite validates the password hashing, user registration, and
login functionality in the AuthenticationManager class.
"""
import unittest
import os
import sys
import logging
from unittest.mock import patch, MagicMock
import hashlib

# Add project root to path so we can import modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.auth import AuthenticationManager


class TestAuthenticationManager(unittest.TestCase):
    """Test cases for AuthenticationManager functionality.
    
    Verifies proper implementation of the Singleton design pattern and
    secure password handling using PBKDF2 with salt.
    """
    
    def setUp(self):
        """Set up test environment before each test case."""
        # Suppress logging during tests
        logging.disable(logging.CRITICAL)
        
        self.test_username = "testuser"
        self.test_email = "test@example.com"
        self.test_password = "SecurePass123"
        self.test_first_name = "Test"
        self.test_last_name = "User"
    
    def tearDown(self):
        """Clean up after each test case."""
        # Re-enable logging
        logging.disable(logging.NOTSET)
    
    def test_singleton_pattern(self):
        """Test that AuthenticationManager follows the Singleton pattern."""
        # The AuthenticationManager class should not be instantiable
        with self.assertRaises(Exception):
            AuthenticationManager()
    
    def test_password_hashing(self):
        """Test that passwords are securely hashed."""
        # Hash a password
        password_hash = AuthenticationManager.hash_password(self.test_password)
        
        # Check that the hash is not the plain password
        self.assertNotEqual(password_hash, self.test_password)
        self.assertTrue(len(password_hash) > 20)  # Should be a long hash
        
        # Check that repeated hashing of the same password yields different hashes (due to salt)
        another_hash = AuthenticationManager.hash_password(self.test_password)
        self.assertNotEqual(password_hash, another_hash)
    
    def test_password_verification(self):
        """Test that password verification works correctly."""
        # Hash a password
        password_hash = AuthenticationManager.hash_password(self.test_password)
        
        # Verify correct password
        self.assertTrue(AuthenticationManager.verify_password(password_hash, self.test_password))
        
        # Verify incorrect password fails
        self.assertFalse(AuthenticationManager.verify_password(password_hash, "WrongPassword"))
    
    @patch('models.user_model.UserModel')
    def test_register_user(self, mock_user_model):
        """Test user registration with lazy import of UserModel."""
        # Setup mocks
        mock_user = MagicMock()
        mock_user.id = 1
        mock_user_model.find_by_username.return_value = None
        mock_user_model.find_by_email.return_value = None
        mock_user_model.return_value = mock_user
        
        # Register a new user
        success, message, user = AuthenticationManager.register_user(
            self.test_username, self.test_email, self.test_password,
            self.test_first_name, self.test_last_name
        )
        
        # Verify results
        self.assertTrue(success)
        self.assertEqual(message, "Registration successful")
        self.assertEqual(user, mock_user)
        
        # Verify UserModel was called correctly
        mock_user_model.assert_called_once()
        args = mock_user_model.call_args.kwargs
        self.assertEqual(args['username'], self.test_username)
        self.assertEqual(args['email'], self.test_email)
        self.assertEqual(args['first_name'], self.test_first_name)
        self.assertEqual(args['last_name'], self.test_last_name)
        self.assertIn('password_hash', args)
        
        # Verify the user was saved
        mock_user.save.assert_called_once()
    
    @patch('models.user_model.UserModel')
    def test_register_existing_username(self, mock_user_model):
        """Test registration fails with existing username."""
        # Setup mocks for existing username
        mock_user_model.find_by_username.return_value = MagicMock()
        
        # Attempt to register
        success, message, user = AuthenticationManager.register_user(
            self.test_username, self.test_email, self.test_password
        )
        
        # Verify registration failed
        self.assertFalse(success)
        self.assertEqual(message, "Username already exists")
        self.assertIsNone(user)
        
        # Verify no user was created or saved
        mock_user_model.assert_not_called()
    
    @patch('models.user_model.UserModel')
    def test_login_user_by_username(self, mock_user_model):
        """Test user login by username."""
        # Setup mock user with correct password hash
        mock_user = MagicMock()
        mock_user.password_hash = AuthenticationManager.hash_password(self.test_password)
        mock_user_model.find_by_username.return_value = mock_user
        mock_user_model.find_by_email.return_value = None
        
        # Attempt login
        success, message, user = AuthenticationManager.login_user(self.test_username, self.test_password)
        
        # Verify login successful
        self.assertTrue(success)
        self.assertEqual(message, "Login successful")
        self.assertEqual(user, mock_user)
        
        # Verify last login was updated
        mock_user.update_last_login.assert_called_once()
    
    @patch('models.user_model.UserModel')
    def test_login_user_by_email(self, mock_user_model):
        """Test user login by email."""
        # Setup mock user with correct password hash
        mock_user = MagicMock()
        mock_user.password_hash = AuthenticationManager.hash_password(self.test_password)
        mock_user_model.find_by_email.return_value = mock_user
        
        # Attempt login
        success, message, user = AuthenticationManager.login_user(self.test_email, self.test_password)
        
        # Verify login successful
        self.assertTrue(success)
        self.assertEqual(message, "Login successful")
        self.assertEqual(user, mock_user)
    
    @patch('models.user_model.UserModel')
    def test_login_invalid_credentials(self, mock_user_model):
        """Test login fails with invalid credentials."""
        # Setup mock user with correct password hash
        mock_user = MagicMock()
        mock_user.password_hash = AuthenticationManager.hash_password(self.test_password)
        mock_user_model.find_by_username.return_value = mock_user
        
        # Attempt login with wrong password
        success, message, user = AuthenticationManager.login_user(self.test_username, "WrongPassword")
        
        # Verify login failed
        self.assertFalse(success)
        self.assertEqual(message, "Invalid username/email or password")
        self.assertIsNone(user)
        
        # Verify last login was not updated
        mock_user.update_last_login.assert_not_called()


if __name__ == '__main__':
    unittest.main()
