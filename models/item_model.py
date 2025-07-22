"""
Item Model Module.

This module defines the Item data model with validation and database operations.
"""
import logging
from typing import Dict, List, Any, Optional, ClassVar
from datetime import datetime
from pydantic import validator, Field
from .base_model import BaseModel

logger = logging.getLogger(__name__)


class ItemModel(BaseModel):
    """
    Item model representing entities that can be recommended.
    
    Contains item information and features for content-based filtering.
    """
    _table_name: ClassVar[str] = "items"
    
    name: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = None
    category: str
    features: Dict[str, Any] = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)
    is_active: bool = True
    popularity_score: float = 0.0
    
    @validator('category')
    def category_must_be_valid(cls, v):
        """Validate that category is not empty."""
        if not v.strip():
            msg = "Category cannot be empty"
            logger.error(f"Category validation failed: {msg}")
            raise ValueError(msg)
        return v
    
    @validator('features')
    def features_must_have_required_keys(cls, v):
        """Validate that features contain required keys."""
        required_keys = []  # Define required feature keys if needed
        
        # Skip validation if no required keys are defined
        if not required_keys:
            return v
            
        missing_keys = [key for key in required_keys if key not in v]
        if missing_keys:
            msg = f"Features missing required keys: {', '.join(missing_keys)}"
            logger.error(f"Features validation failed: {msg}")
            raise ValueError(msg)
        return v
    
    @classmethod
    def find_by_category(cls, category: str) -> List['ItemModel']:
        """
        Find all items in a specific category.
        
        Args:
            category: The category to search for
            
        Returns:
            List of items in the given category
        """
        logger.info(f"Finding items in category {category}")
        try:
            return cls.find_by(category=category)
        except Exception as e:
            logger.error(f"Error finding items by category: {str(e)}")
            raise
    
    @classmethod
    def find_active(cls) -> List['ItemModel']:
        """
        Find all active items.
        
        Returns:
            List of active items
        """
        logger.info("Finding all active items")
        try:
            return cls.find_by(is_active=True)
        except Exception as e:
            logger.error(f"Error finding active items: {str(e)}")
            raise
    
    def update_features(self, new_features: Dict[str, Any]) -> 'ItemModel':
        """
        Update item features.
        
        Args:
            new_features: Dictionary of new feature values to merge
            
        Returns:
            Updated item instance
        """
        logger.info(f"Updating features for item {self.id}")
        try:
            # Merge new features with existing ones
            self.features = {**self.features, **new_features}
            self.updated_at = datetime.utcnow()
            return self.save()
        except Exception as e:
            logger.error(f"Error updating item features: {str(e)}")
            raise
    
    def update_popularity(self, score: float) -> 'ItemModel':
        """
        Update the item's popularity score.
        
        Args:
            score: New popularity score
            
        Returns:
            Updated item instance
        """
        logger.info(f"Updating popularity score for item {self.id}")
        try:
            self.popularity_score = score
            self.updated_at = datetime.utcnow()
            return self.save()
        except Exception as e:
            logger.error(f"Error updating item popularity: {str(e)}")
            raise
    
    def get_feature_vector(self) -> List[float]:
        """
        Convert item features to a numerical vector for algorithm processing.
        
        Returns:
            List of numerical feature values
        """
        logger.debug(f"Getting feature vector for item {self.id}")
        # This is a simplified implementation. In a real system, this would
        # convert categorical features to numerical, normalize values, etc.
        feature_vector = []
        
        # Extract numerical features or convert categorical to numerical
        for key, value in self.features.items():
            if isinstance(value, (int, float)):
                feature_vector.append(float(value))
                
        return feature_vector
