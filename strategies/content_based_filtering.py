"""
Content-Based Filtering Strategy Module.

This module implements content-based filtering recommendation algorithm using the Strategy pattern.
"""
import logging
import numpy as np
from typing import List, Dict, Any, Optional
from models.item_model import ItemModel
from models.user_model import UserModel
from models.rating_model import RatingModel
from .recommendation_strategy import BaseRecommendationStrategy

logger = logging.getLogger(__name__)


class ContentBasedFilteringStrategy(BaseRecommendationStrategy):
    """
    Content-based filtering recommendation strategy.
    
    Implements a recommendation algorithm based on item features and user preferences.
    """
    
    def __init__(self):
        """Initialize the content-based filtering strategy."""
        super().__init__()
        self._item_features = {}  # Dict mapping item_id to feature vector
        self._user_profiles = {}  # Dict mapping user_id to preference vector
        logger.info("Initialized ContentBasedFilteringStrategy")
    
    def train(self, data: Any = None) -> None:
        """
        Train the content-based filtering algorithm with item features and user ratings.
        
        Args:
            data: Optional pre-loaded data. If None, data will be loaded from the database.
        """
        logger.info("Training content-based filtering model")
        try:
            # Extract item features
            self._extract_item_features()
            
            # Build user profiles
            self._build_user_profiles()
            
            self._is_trained = True
            logger.info(f"Content-based filtering model trained with {len(self._item_features)} items and {len(self._user_profiles)} user profiles")
        except Exception as e:
            logger.error(f"Error training content-based filtering model: {str(e)}")
            raise
    
    def _extract_item_features(self) -> None:
        """
        Extract feature vectors from all items in the database.
        
        This method loads items from the database and extracts their feature vectors.
        """
        logger.debug("Extracting item features")
        
        try:
            # Get all items
            items = ItemModel.find_all()
            
            # Extract feature vector for each item
            for item in items:
                # Get the feature vector
                feature_vector = item.get_feature_vector()
                
                # Store the feature vector
                if feature_vector:
                    self._item_features[item.id] = np.array(feature_vector)
                else:
                    logger.warning(f"No features found for item {item.id}")
            
            logger.debug(f"Extracted features for {len(self._item_features)} items")
        except Exception as e:
            logger.error(f"Error extracting item features: {str(e)}")
            raise
    
    def _build_user_profiles(self) -> None:
        """
        Build user preference profiles based on their ratings and item features.
        
        This method creates a preference vector for each user based on their ratings and
        the features of the items they have rated.
        """
        logger.debug("Building user profiles")
        
        try:
            # Get all users
            users = UserModel.find_all()
            
            # Build profile for each user
            for user in users:
                # Get user ratings
                ratings = RatingModel.find_by_user(user.id)
                
                if not ratings:
                    logger.debug(f"No ratings found for user {user.id}")
                    continue
                
                # Initialize profile
                profile = None
                total_weight = 0.0
                
                # Calculate weighted average of item features
                for rating in ratings:
                    item_id = rating.item_id
                    rating_value = rating.value
                    
                    # Skip if item features are not available
                    if item_id not in self._item_features:
                        continue
                    
                    # Get item features
                    item_features = self._item_features[item_id]
                    
                    # Weight by rating (shifted to be centered around 0)
                    weight = rating_value - 2.5
                    
                    # Skip neutral ratings
                    if abs(weight) < 0.5:
                        continue
                    
                    # Add weighted features to profile
                    if profile is None:
                        profile = weight * item_features
                    else:
                        profile += weight * item_features
                    
                    total_weight += abs(weight)
                
                # Normalize profile
                if profile is not None and total_weight > 0:
                    profile = profile / total_weight
                    self._user_profiles[user.id] = profile
                    logger.debug(f"Built profile for user {user.id} with {len(profile)} features")
            
            logger.debug(f"Built {len(self._user_profiles)} user profiles")
        except Exception as e:
            logger.error(f"Error building user profiles: {str(e)}")
            raise
    
    def _calculate_item_similarity(self, item_features: np.ndarray, profile: np.ndarray) -> float:
        """
        Calculate similarity between an item and a user profile.
        
        Args:
            item_features: Feature vector of the item
            profile: Preference vector of the user
            
        Returns:
            Similarity score between the item and user profile
        """
        # Reason: Use cosine similarity for comparing feature vectors
        # Cosine similarity works well for high-dimensional sparse data
        
        # Handle edge cases
        if np.all(item_features == 0) or np.all(profile == 0):
            return 0.0
            
        # Calculate cosine similarity
        dot_product = np.dot(item_features, profile)
        magnitude_item = np.sqrt(np.sum(item_features ** 2))
        magnitude_profile = np.sqrt(np.sum(profile ** 2))
        
        similarity = dot_product / (magnitude_item * magnitude_profile)
        
        # Ensure the result is between 0 and 1
        return max(0.0, min(similarity, 1.0))
    
    def _get_or_create_user_profile(self, user_id: int) -> Optional[np.ndarray]:
        """
        Get an existing user profile or create a new one if it doesn't exist.
        
        Args:
            user_id: The ID of the user
            
        Returns:
            The user's preference profile or None if it cannot be created
        """
        # Check if profile already exists
        if user_id in self._user_profiles:
            return self._user_profiles[user_id]
            
        logger.debug(f"Creating new profile for user {user_id}")
        
        try:
            # Get user ratings
            ratings = RatingModel.find_by_user(user_id)
            
            if not ratings:
                logger.warning(f"No ratings found for user {user_id}")
                return None
            
            # Initialize profile
            profile = None
            total_weight = 0.0
            
            # Calculate weighted average of item features
            for rating in ratings:
                item_id = rating.item_id
                rating_value = rating.value
                
                # Skip if item features are not available
                if item_id not in self._item_features:
                    continue
                
                # Get item features
                item_features = self._item_features[item_id]
                
                # Weight by rating (shifted to be centered around 0)
                weight = rating_value - 2.5
                
                # Skip neutral ratings
                if abs(weight) < 0.5:
                    continue
                
                # Add weighted features to profile
                if profile is None:
                    profile = weight * item_features
                else:
                    profile += weight * item_features
                
                total_weight += abs(weight)
            
            # Normalize profile
            if profile is not None and total_weight > 0:
                profile = profile / total_weight
                # Cache the profile for future use
                self._user_profiles[user_id] = profile
                return profile
            
            return None
        except Exception as e:
            logger.error(f"Error creating user profile: {str(e)}")
            return None
    
    def recommend(self, user_id: int, n: int = 10, **kwargs) -> List[Dict[str, Any]]:
        """
        Generate recommendations for a specific user using content-based filtering.
        
        Args:
            user_id: The ID of the user to generate recommendations for
            n: The number of recommendations to generate
            **kwargs: Additional parameters
            
        Returns:
            A list of dictionaries containing recommended item details
        """
        logger.info(f"Generating recommendations for user {user_id}")
        self.check_trained()
        
        try:
            # Get user profile
            profile = self._get_or_create_user_profile(user_id)
            
            # Handle users with no profile
            if profile is None:
                logger.warning(f"No profile available for user {user_id}, using fallback recommendations")
                return self._fallback_recommendations(n)
            
            # Calculate similarity scores for all items
            item_scores = {}
            for item_id, item_features in self._item_features.items():
                similarity = self._calculate_item_similarity(item_features, profile)
                item_scores[item_id] = similarity
            
            # Filter already rated items
            filtered_scores = self.filter_already_rated(user_id, item_scores)
            
            # Sort by similarity score
            sorted_items = sorted(
                filtered_scores.items(), key=lambda x: x[1], reverse=True
            )[:n]
            
            # Get item details for recommendations
            recommendations = []
            for item_id, score in sorted_items:
                item = ItemModel.find_by_id(item_id)
                if item:
                    recommendations.append({
                        "item_id": item_id,
                        "name": item.name,
                        "description": item.description,
                        "category": item.category,
                        "score": score,
                        "recommendation_type": "content-based"
                    })
            
            logger.info(f"Generated {len(recommendations)} content-based recommendations for user {user_id}")
            return recommendations
        except Exception as e:
            logger.error(f"Error generating recommendations: {str(e)}")
            raise
    
    def _fallback_recommendations(self, n: int = 10) -> List[Dict[str, Any]]:
        """
        Generate fallback recommendations based on item popularity.
        
        Args:
            n: The number of recommendations to generate
            
        Returns:
            A list of dictionaries containing recommended item details
        """
        logger.info("Generating fallback recommendations")
        
        try:
            # Use popular items as fallback
            items = ItemModel.find_all()
            
            # Sort by popularity score
            sorted_items = sorted(
                items, key=lambda item: item.popularity_score, reverse=True
            )[:n]
            
            recommendations = []
            for item in sorted_items:
                recommendations.append({
                    "item_id": item.id,
                    "name": item.name,
                    "description": item.description,
                    "category": item.category,
                    "score": item.popularity_score / 5.0,  # Normalize to 0-1
                    "recommendation_type": "popular"
                })
            
            logger.info(f"Generated {len(recommendations)} fallback recommendations")
            return recommendations
        except Exception as e:
            logger.error(f"Error generating fallback recommendations: {str(e)}")
            raise
    
    def explain(self, user_id: int, item_id: int) -> str:
        """
        Generate an explanation for why an item was recommended to a user.
        
        Args:
            user_id: The ID of the user
            item_id: The ID of the recommended item
            
        Returns:
            A human-readable explanation string
        """
        logger.info(f"Generating explanation for user {user_id}, item {item_id}")
        self.check_trained()
        
        try:
            # Get item details
            item = ItemModel.find_by_id(item_id)
            if not item:
                return f"Item {item_id} not found in the database."
            
            # Get user profile
            profile = self._get_or_create_user_profile(user_id)
            if profile is None:
                return f"{item.name} was recommended because it's popular among our users."
            
            # Get user's highest rated items
            user_ratings = RatingModel.find_by_user(user_id)
            high_rated_items = [r.item_id for r in user_ratings if r.value >= 4.0]
            
            # Find items with similar features
            similar_items = []
            for rated_item_id in high_rated_items:
                if rated_item_id in self._item_features and item_id in self._item_features:
                    similarity = self._calculate_item_similarity(
                        self._item_features[rated_item_id], 
                        self._item_features[item_id]
                    )
                    if similarity >= 0.7:  # Highly similar
                        rated_item = ItemModel.find_by_id(rated_item_id)
                        if rated_item:
                            similar_items.append(rated_item.name)
            
            # Generate explanation based on similar items or features
            if similar_items:
                if len(similar_items) == 1:
                    return f"{item.name} was recommended because you liked {similar_items[0]}, which has similar features."
                elif len(similar_items) <= 3:
                    items_str = ", ".join(similar_items[:-1]) + " and " + similar_items[-1]
                    return f"{item.name} was recommended because you liked {items_str}, which have similar features."
                else:
                    return f"{item.name} was recommended because it has similar features to several items you've liked in the past."
            
            # Feature-based explanation
            top_features = item.features.get("top_features", [])
            if top_features and len(top_features) > 0:
                features_str = ", ".join(top_features[:3])
                return f"{item.name} was recommended because your profile shows interest in items with {features_str}."
                
            # Fallback explanation
            return f"{item.name} was recommended based on its features matching your preferences."
        except Exception as e:
            logger.error(f"Error generating explanation: {str(e)}")
            return "This recommendation is based on content-based filtering techniques."
    
    def get_similarity(self, item_id1: int, item_id2: int) -> float:
        """
        Calculate the similarity between two items based on their features.
        
        Args:
            item_id1: The ID of the first item
            item_id2: The ID of the second item
            
        Returns:
            A similarity score between 0 and 1
        """
        logger.info(f"Calculating similarity between items {item_id1} and {item_id2}")
        self.check_trained()
        
        try:
            # Check if both items have features
            if item_id1 not in self._item_features or item_id2 not in self._item_features:
                return 0.0
                
            # Get item features
            features1 = self._item_features[item_id1]
            features2 = self._item_features[item_id2]
            
            # Calculate cosine similarity
            return self._calculate_item_similarity(features1, features2)
        except Exception as e:
            logger.error(f"Error calculating item similarity: {str(e)}")
            return 0.0
