"""
Rating Model Module.

This module defines the Rating data model with validation and database operations.
Ratings represent user interactions with items and are the foundation for collaborative filtering.
"""
import logging
from typing import Optional, ClassVar, Dict, Any
from datetime import datetime
from pydantic import validator, Field, model_validator
from .base_model import BaseModel

logger = logging.getLogger(__name__)


class RatingModel(BaseModel):
    """
    Rating model representing user evaluations of items.
    
    Contains rating information and context for recommendation algorithms.
    """
    _table_name: ClassVar[str] = "ratings"
    
    user_id: int
    item_id: int
    value: int = Field(..., ge=1, le=5)
    context: Optional[Dict[str, Any]] = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = None
    
    @validator('value')
    def validate_rating(cls, v):
        """Validate that rating value is between 1 and 5."""
        if v < 1 or v > 5:
            msg = f"Rating value must be between 1 and 5, got {v}"
            logger.error(f"Rating validation failed: {msg}")
            raise ValueError(msg)
        return v
    
    @model_validator(mode='after')
    def validate_user_item_combination(self):
        """Validate that user_id and item_id are provided."""
        user_id = self.user_id
        item_id = self.item_id
        
        if user_id is None or item_id is None:
            msg = "Both user_id and item_id must be provided"
            logger.error(f"Rating validation failed: {msg}")
            raise ValueError(msg)
        return self
    
    @classmethod
    def find_by_user(cls, user_id: int) -> list['RatingModel']:
        """
        Find all ratings by a specific user.
        
        Args:
            user_id: The ID of the user
            
        Returns:
            List of ratings by the user
        """
        logger.info(f"Finding ratings for user {user_id}")
        try:
            return cls.find_by(user_id=user_id)
        except Exception as e:
            logger.error(f"Error finding ratings by user: {str(e)}")
            raise
    
    @classmethod
    def find_by_item(cls, item_id: int) -> list['RatingModel']:
        """
        Find all ratings for a specific item.
        
        Args:
            item_id: The ID of the item
            
        Returns:
            List of ratings for the item
        """
        logger.info(f"Finding ratings for item {item_id}")
        try:
            return cls.find_by(item_id=item_id)
        except Exception as e:
            logger.error(f"Error finding ratings by item: {str(e)}")
            raise
    
    @classmethod
    def find_by_user_and_item(cls, user_id: int, item_id: int) -> Optional['RatingModel']:
        """
        Find a rating by a specific user for a specific item.
        
        Args:
            user_id: The ID of the user
            item_id: The ID of the item
            
        Returns:
            The rating or None if not found
        """
        logger.info(f"Finding rating by user {user_id} for item {item_id}")
        try:
            ratings = cls.find_by(user_id=user_id, item_id=item_id)
            return ratings[0] if ratings else None
        except Exception as e:
            logger.error(f"Error finding rating by user and item: {str(e)}")
            raise
    
    @classmethod
    def get_average_rating_for_item(cls, item_id: int) -> float:
        """
        Calculate the average rating for an item.
        
        Args:
            item_id: The ID of the item
            
        Returns:
            The average rating value
        """
        logger.info(f"Calculating average rating for item {item_id}")
        try:
            ratings = cls.find_by_item(item_id)
            
            if not ratings:
                logger.debug(f"No ratings found for item {item_id}")
                return 0.0
                
            total = sum(r.value for r in ratings)
            average = total / len(ratings)
            
            logger.debug(f"Average rating for item {item_id} is {average:.2f}")
            return average
        except Exception as e:
            logger.error(f"Error calculating average rating: {str(e)}")
            raise
    
    @classmethod
    def build_user_item_matrix(cls) -> tuple[list[int], list[int], list[list[float]]]:
        """
        Build a user-item rating matrix for collaborative filtering.
        
        Returns:
            A tuple containing:
            - List of user IDs
            - List of item IDs
            - 2D matrix of ratings where matrix[i][j] is the rating of user i for item j
        """
        logger.info("Building user-item rating matrix")
        try:
            ratings = cls.find_all()
            
            # Extract unique user and item IDs
            user_ids = sorted(set(r.user_id for r in ratings))
            item_ids = sorted(set(r.item_id for r in ratings))
            
            # Create a user-to-index and item-to-index mapping
            user_to_index = {user_id: i for i, user_id in enumerate(user_ids)}
            item_to_index = {item_id: j for j, item_id in enumerate(item_ids)}
            
            # Initialize the matrix with zeros
            matrix = [[0.0 for _ in range(len(item_ids))] for _ in range(len(user_ids))]
            
            # Fill in the matrix with ratings
            for rating in ratings:
                user_idx = user_to_index[rating.user_id]
                item_idx = item_to_index[rating.item_id]
                matrix[user_idx][item_idx] = rating.value
                
            logger.debug(f"Built user-item matrix of shape {len(user_ids)}x{len(item_ids)}")
            return user_ids, item_ids, matrix
        except Exception as e:
            logger.error(f"Error building user-item matrix: {str(e)}")
            raise
