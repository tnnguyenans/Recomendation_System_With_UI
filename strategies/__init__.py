"""
Strategies Package.

This package contains all the recommendation algorithm strategies using the Strategy design pattern.
"""
from .recommendation_strategy import RecommendationStrategy, BaseRecommendationStrategy
from .collaborative_filtering import CollaborativeFilteringStrategy
from .content_based_filtering import ContentBasedFilteringStrategy
from .hybrid_filtering import HybridFilteringStrategy

__all__ = [
    'RecommendationStrategy',
    'BaseRecommendationStrategy',
    'CollaborativeFilteringStrategy', 
    'ContentBasedFilteringStrategy',
    'HybridFilteringStrategy'
]
