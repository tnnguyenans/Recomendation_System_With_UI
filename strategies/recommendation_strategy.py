"""
Recommendation Strategy Module.

This module defines the interface and base classes for recommendation algorithms using the Strategy pattern.
"""
import logging
from abc import ABC, abstractmethod
from typing import List, Dict, Any

logger = logging.getLogger(__name__)


class RecommendationStrategy(ABC):
    """
    Abstract base class for recommendation algorithms.
    
    This interface defines the contract that all recommendation strategies must implement.
    Follows the Strategy design pattern to make algorithms interchangeable.
    """
    
    @abstractmethod
    def train(self, data: Any) -> None:
        """
        Train the recommendation algorithm with the given data.
        
        Args:
            data: Training data specific to the algorithm
        """
        pass
    
    @abstractmethod
    def recommend(self, user_id: int, n: int = 10, **kwargs) -> List[Dict[str, Any]]:
        """
        Generate recommendations for a specific user.
        
        Args:
            user_id: The ID of the user to generate recommendations for
            n: The number of recommendations to generate
            **kwargs: Additional parameters specific to the algorithm
            
        Returns:
            A list of dictionaries containing recommended item details
        """
        pass
    
    @abstractmethod
    def explain(self, user_id: int, item_id: int) -> str:
        """
        Generate an explanation for why an item was recommended to a user.
        
        Args:
            user_id: The ID of the user
            item_id: The ID of the recommended item
            
        Returns:
            A human-readable explanation string
        """
        pass
    
    @abstractmethod
    def get_similarity(self, item_id1: int, item_id2: int) -> float:
        """
        Calculate the similarity between two items.
        
        Args:
            item_id1: The ID of the first item
            item_id2: The ID of the second item
            
        Returns:
            A similarity score between 0 and 1
        """
        pass


class BaseRecommendationStrategy(RecommendationStrategy):
    """
    Base implementation of the recommendation strategy with common functionality.
    
    Implements common methods and utilities that specific strategies can inherit.
    """
    
    def __init__(self):
        """Initialize the strategy with default values."""
        self._is_trained = False
        self._training_data = None
        logger.info(f"Initialized {self.__class__.__name__}")
    
    def check_trained(self):
        """
        Check if the strategy has been trained.
        
        Raises:
            RuntimeError: If the strategy has not been trained
        """
        if not self._is_trained:
            msg = f"{self.__class__.__name__} has not been trained"
            logger.error(msg)
            raise RuntimeError(msg)
    
    @property
    def is_trained(self) -> bool:
        """
        Check if the strategy has been trained.
        
        Returns:
            True if the strategy has been trained, False otherwise
        """
        return self._is_trained
    
    def normalize_scores(self, scores: Dict[int, float]) -> Dict[int, float]:
        """
        Normalize recommendation scores to be between 0 and 1.
        
        Args:
            scores: Dictionary mapping item IDs to raw scores
            
        Returns:
            Dictionary mapping item IDs to normalized scores
        """
        if not scores:
            return {}
            
        min_score = min(scores.values())
        max_score = max(scores.values())
        
        # Avoid division by zero if all scores are the same
        if max_score == min_score:
            return {item_id: 1.0 for item_id in scores}
            
        # Normalize scores
        return {
            item_id: (score - min_score) / (max_score - min_score)
            for item_id, score in scores.items()
        }
    
    def filter_already_rated(self, user_id: int, item_scores: Dict[int, float]) -> Dict[int, float]:
        """
        Remove items the user has already rated from recommendations.
        
        Args:
            user_id: The ID of the user
            item_scores: Dictionary mapping item IDs to scores
            
        Returns:
            Dictionary with already rated items removed
        """
        from models.rating_model import RatingModel
        
        # Get items the user has already rated
        user_ratings = RatingModel.find_by_user(user_id)
        rated_item_ids = {rating.item_id for rating in user_ratings}
        
        # Remove rated items
        return {
            item_id: score
            for item_id, score in item_scores.items()
            if item_id not in rated_item_ids
        }
