"""
Authentication Utilities Module.

This module provides authentication and security functions for the recommendation system.
"""
import logging
import hashlib
import os
import secrets
from typing import Tuple, Optional, Dict, Any, TYPE_CHECKING
from .config import PASSWORD_HASH_ALGORITHM, PASSWORD_SALT_LENGTH, PASSWORD_HASH_ITERATIONS

# Type hints for better IDE support without creating circular imports
if TYPE_CHECKING:
    from models.user_model import UserModel

logger = logging.getLogger(__name__)


class AuthenticationManager:
    """
    Authentication manager for user registration and login.
    
    Handles secure password hashing and verification.
    Implements the Singleton pattern to ensure only one instance exists.
    """
    
    _instance = None
    
    def __new__(cls):
        """
        Prevent direct instantiation to enforce the Singleton pattern.
        
        Raises:
            Exception: When attempting to create an instance directly
        """
        raise Exception("AuthenticationManager cannot be instantiated directly. Use class methods instead.")
        
    
    @staticmethod
    def hash_password(password: str) -> str:
        """
        Hash a password using PBKDF2 with a random salt.
        
        Args:
            password: The password to hash
            
        Returns:
            The hashed password string in the format: algorithm$iterations$salt$hash
        """
        logger.debug("Hashing password")
        
        try:
            # Generate a random salt
            salt = secrets.token_hex(PASSWORD_SALT_LENGTH)
            
            # Hash the password using PBKDF2
            password_hash = hashlib.pbkdf2_hmac(
                'sha256',
                password.encode('utf-8'),
                salt.encode('utf-8'),
                PASSWORD_HASH_ITERATIONS
            ).hex()
            
            # Combine algorithm, iterations, salt, and hash
            hashed_password = f"{PASSWORD_HASH_ALGORITHM}${PASSWORD_HASH_ITERATIONS}${salt}${password_hash}"
            
            return hashed_password
        except Exception as e:
            logger.error(f"Error hashing password: {str(e)}")
            raise
    
    @staticmethod
    def verify_password(stored_password: str, provided_password: str) -> bool:
        """
        Verify a password against a stored hash.
        
        Args:
            stored_password: The stored password hash
            provided_password: The password to verify
            
        Returns:
            True if the password matches, False otherwise
        """
        logger.debug("Verifying password")
        
        try:
            # Parse the stored hash
            algorithm, iterations_str, salt, stored_hash = stored_password.split('$')
            iterations = int(iterations_str)
            
            # Hash the provided password using the same salt and iterations
            computed_hash = hashlib.pbkdf2_hmac(
                'sha256',
                provided_password.encode('utf-8'),
                salt.encode('utf-8'),
                iterations
            ).hex()
            
            # Compare the computed hash with the stored hash
            return computed_hash == stored_hash
        except Exception as e:
            logger.error(f"Error verifying password: {str(e)}")
            return False
    
    @classmethod
    def register_user(cls, username: str, email: str, password: str, 
                    first_name: Optional[str] = None, 
                    last_name: Optional[str] = None) -> Tuple[bool, str, Optional[Any]]:
        """
        Register a new user.
        
        Args:
            username: The username for the new user
            email: The email for the new user
            password: The password for the new user
            first_name: The first name of the user (optional)
            last_name: The last name of the user (optional)
            
        Returns:
            A tuple containing:
            - Success flag
            - Message
            - User model if successful, None otherwise
        """
        logger.info(f"Registering new user with username '{username}' and email '{email}'")
        
        try:
            # Import here to avoid circular imports
            from models.user_model import UserModel
            
            # Check if username already exists
            existing_user = UserModel.find_by_username(username)
            if existing_user:
                logger.warning(f"Username '{username}' already exists")
                return False, "Username already exists", None
                
            # Check if email already exists
            existing_user = UserModel.find_by_email(email)
            if existing_user:
                logger.warning(f"Email '{email}' already exists")
                return False, "Email already exists", None
                
            # Hash the password
            password_hash = cls.hash_password(password)
            
            # Create the user (UserModel already imported above)
            user = UserModel(
                username=username,
                email=email,
                password_hash=password_hash,
                first_name=first_name,
                last_name=last_name
            )
            
            # Save the user to the database
            user.save()
            
            logger.info(f"User '{username}' registered successfully with ID {user.id}")
            return True, "Registration successful", user
        except Exception as e:
            logger.error(f"Error registering user: {str(e)}")
            return False, f"Registration failed: {str(e)}", None
    
    @classmethod
    def login_user(cls, username_or_email: str, password: str) -> Tuple[bool, str, Optional[Any]]:
        """
        Login a user.
        
        Args:
            username_or_email: The username or email of the user
            password: The password of the user
            
        Returns:
            A tuple containing:
            - Success flag
            - Message
            - User model if successful, None otherwise
        """
        logger.info(f"Attempting login for '{username_or_email}'")
        
        try:
            # Import here to avoid circular imports
            from models.user_model import UserModel
            
            # Check if input is an email
            if '@' in username_or_email:
                user = UserModel.find_by_email(username_or_email)
            else:
                user = UserModel.find_by_username(username_or_email)
                
            # Check if user exists
            if not user:
                logger.warning(f"User '{username_or_email}' not found")
                return False, "Invalid username/email or password", None
                
            # Verify password
            if not cls.verify_password(user.password_hash, password):
                logger.warning(f"Invalid password for user '{username_or_email}'")
                return False, "Invalid username/email or password", None
                
            # Update last login timestamp
            user.update_last_login()
            
            logger.info(f"User '{username_or_email}' logged in successfully")
            return True, "Login successful", user
        except Exception as e:
            logger.error(f"Error logging in: {str(e)}")
            return False, f"Login failed: {str(e)}", None
