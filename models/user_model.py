"""
User Model Module.

This module defines the User data model with validation and database operations.
"""
import logging
from typing import Optional, List, Dict, Any, ClassVar, Union
from datetime import datetime
from pydantic import validator, EmailStr, Field, model_validator
from .base_model import BaseModel
# Avoid circular import with lazy import of AuthenticationManager

logger = logging.getLogger(__name__)


class UserModel(BaseModel):
    """
    User model representing system users.
    
    Contains user profile information and preferences.
    """
    _table_name: ClassVar[str] = "users"
    
    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr
    password_hash: str
    password: Optional[str] = Field(None, exclude=True)  # Not stored in DB, just for validation
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    last_login: Optional[datetime] = None
    preferences: Dict[str, Any] = Field(default_factory=dict)
    is_active: bool = True
    profile_image: Optional[str] = None  # Stores the path or base64 encoded image data
    
    @validator('username')
    def username_must_be_valid(cls, v):
        """Validate that username contains only valid characters."""
        import re
        if not re.match(r'^[a-zA-Z0-9_-]+$', v):
            msg = "Username must contain only alphanumeric characters, underscores, or hyphens"
            logger.error(f"Username validation failed: {msg}")
            raise ValueError(msg)
        return v
        
    @model_validator(mode='before')
    @classmethod
    def process_password(cls, data):
        """Process plain password into password_hash if provided."""
        # Convert to dict if not already (handles both dict and model input)
        if not isinstance(data, dict):
            data = data.model_dump()
            
        # If plain password is provided, hash it and set password_hash
        if data.get('password') and not data.get('password_hash'):
            try:
                # Import here to avoid circular imports
                from utils.auth import AuthenticationManager
                data['password_hash'] = AuthenticationManager.hash_password(data['password'])
                logger.debug("Password hashed successfully")
                # Clear the password field for security reasons
                data['password'] = None
            except Exception as e:
                logger.error(f"Failed to hash password: {str(e)}")
                raise ValueError("Failed to process password") from e
                
        return data
    
    @classmethod
    def find_by_email(cls, email: str) -> Optional['UserModel']:
        """
        Find a user by their email address.
        
        Args:
            email: The email address to search for
            
        Returns:
            The user with the given email or None if not found
        """
        logger.info(f"Finding user with email {email}")
        try:
            users = cls.find_by(email=email)
            return users[0] if users else None
        except Exception as e:
            logger.error(f"Error finding user by email: {str(e)}")
            raise
    
    @classmethod
    def find_by_username(cls, username: str) -> Optional['UserModel']:
        """
        Find a user by their username.
        
        Args:
            username: The username to search for
            
        Returns:
            The user with the given username or None if not found
        """
        logger.info(f"Finding user with username {username}")
        try:
            users = cls.find_by(username=username)
            return users[0] if users else None
        except Exception as e:
            logger.error(f"Error finding user by username: {str(e)}")
            raise
    
    def update_preferences(self, preferences: Dict[str, Any]) -> None:
        """Update user preferences."""
        self.preferences = preferences
        self.save()

    def update_profile_image(self, image_data: str) -> bool:
        """
        Update user's profile image.
        
        Args:
            image_data: Base64 encoded image data with mime type prefix
            
        Returns:
            True if successful, False otherwise
        """
        try:
            logger.info(f"Updating profile image for user {self.id}")
            self.profile_image = image_data
            self.save()
            return True
        except Exception as e:
            logger.error(f"Error updating user preferences: {str(e)}")
            raise
    
    def update_last_login(self) -> 'UserModel':
        """
        Update the last login timestamp to current time.
        
        Returns:
            Updated user instance
        """
        logger.info(f"Updating last login for user {self.id}")
        try:
            self.last_login = datetime.utcnow()
            return self.save()
        except Exception as e:
            logger.error(f"Error updating last login: {str(e)}")
            raise
