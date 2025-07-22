"""
Recommendation Factory Module.

This module implements the Factory pattern for creating recommendation strategies.
"""
import logging
from typing import Dict, Any, Type, Optional
from strategies.recommendation_strategy import RecommendationStrategy
from strategies.collaborative_filtering import CollaborativeFilteringStrategy
from strategies.content_based_filtering import ContentBasedFilteringStrategy
from strategies.hybrid_filtering import HybridFilteringStrategy

logger = logging.getLogger(__name__)


class RecommendationFactory:
    """
    Factory class for creating recommendation strategies.
    
    Implements the Factory design pattern to decouple the creation of recommendation
    strategies from their usage.
    """
    
    # Map of strategy type names to their classes
    _strategies: Dict[str, Type[RecommendationStrategy]] = {
        "collaborative": CollaborativeFilteringStrategy,
        "content-based": ContentBasedFilteringStrategy,
        "hybrid": HybridFilteringStrategy
    }
    
    @classmethod
    def create_strategy(cls, strategy_type: str, **kwargs) -> Optional[RecommendationStrategy]:
        """
        Create a recommendation strategy of the specified type.
        
        Args:
            strategy_type: The type of strategy to create
            **kwargs: Additional parameters to pass to the strategy constructor
            
        Returns:
            A new instance of the specified strategy type
            
        Raises:
            ValueError: If the strategy type is unknown
        """
        logger.info(f"Creating recommendation strategy of type '{strategy_type}'")
        
        try:
            if strategy_type not in cls._strategies:
                valid_types = ", ".join(cls._strategies.keys())
                msg = f"Unknown strategy type: {strategy_type}. Valid types: {valid_types}"
                logger.error(msg)
                raise ValueError(msg)
                
            # Get the strategy class
            strategy_class = cls._strategies[strategy_type]
            
            # Create and return the strategy instance
            strategy = strategy_class(**kwargs)
            logger.debug(f"Created {strategy.__class__.__name__}")
            return strategy
        except Exception as e:
            logger.error(f"Error creating strategy: {str(e)}")
            raise
    
    @classmethod
    def register_strategy(cls, name: str, strategy_class: Type[RecommendationStrategy]) -> None:
        """
        Register a new strategy type.
        
        Args:
            name: The name to associate with the strategy type
            strategy_class: The strategy class to register
            
        Raises:
            ValueError: If the strategy name is already registered
        """
        logger.info(f"Registering strategy type '{name}'")
        
        if name in cls._strategies:
            msg = f"Strategy type '{name}' is already registered"
            logger.error(msg)
            raise ValueError(msg)
            
        cls._strategies[name] = strategy_class
        logger.debug(f"Registered strategy type '{name}' as {strategy_class.__name__}")
    
    @classmethod
    def get_available_strategies(cls) -> Dict[str, str]:
        """
        Get a dictionary of available strategy types and their descriptions.
        
        Returns:
            A dictionary mapping strategy names to their descriptions
        """
        return {
            "collaborative": "Recommends items based on similar users' preferences",
            "content-based": "Recommends items based on item features and user preferences",
            "hybrid": "Combines multiple recommendation approaches for better results"
        }
