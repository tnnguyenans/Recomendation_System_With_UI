"""
Collaborative Filtering Strategy Module.

This module implements the collaborative filtering recommendation algorithm using the Strategy pattern.
"""
import logging
import numpy as np
from typing import List, Dict, Any, Tuple, Optional
from models.rating_model import RatingModel
from models.item_model import ItemModel
from models.user_model import UserModel
from .recommendation_strategy import BaseRecommendationStrategy

logger = logging.getLogger(__name__)


class CollaborativeFilteringStrategy(BaseRecommendationStrategy):
    """
    Collaborative filtering recommendation strategy.
    
    Implements user-based collaborative filtering where recommendations are based
    on similar users' preferences.
    """
    
    def __init__(self, similarity_method: str = "cosine"):
        """
        Initialize collaborative filtering strategy.
        
        Args:
            similarity_method: Method to calculate user similarity ("cosine", "pearson", or "jaccard")
        """
        super().__init__()
        self._similarity_method = similarity_method
        self._user_ids = []
        self._item_ids = []
        self._ratings_matrix = []
        self._user_similarity_matrix = None
        logger.info(f"Initialized CollaborativeFilteringStrategy with {similarity_method} similarity")
    
    def train(self, data: Any = None) -> None:
        """
        Train the collaborative filtering algorithm with user-item ratings.
        
        Args:
            data: Optional pre-loaded rating data. If None, data will be loaded from the database.
        """
        logger.info("Training collaborative filtering model")
        try:
            # Load ratings data
            if data is None:
                self._user_ids, self._item_ids, self._ratings_matrix = RatingModel.build_user_item_matrix()
            else:
                self._user_ids, self._item_ids, self._ratings_matrix = data
            
            # Convert to numpy arrays for efficient computation
            ratings_array = np.array(self._ratings_matrix)
            
            # Calculate user similarity matrix
            self._user_similarity_matrix = self._calculate_similarity_matrix(ratings_array)
            
            self._is_trained = True
            logger.info(f"Collaborative filtering model trained with {len(self._user_ids)} users and {len(self._item_ids)} items")
        except Exception as e:
            logger.error(f"Error training collaborative filtering model: {str(e)}")
            raise
    
    def _calculate_similarity_matrix(self, ratings_matrix: np.ndarray) -> np.ndarray:
        """
        Calculate similarity matrix between all users.
        
        Args:
            ratings_matrix: 2D numpy array of user-item ratings
            
        Returns:
            2D numpy array of user similarities
        """
        logger.debug(f"Calculating user similarity matrix using {self._similarity_method} method")
        
        # Get the number of users
        n_users = ratings_matrix.shape[0]
        
        # Initialize similarity matrix
        similarity_matrix = np.zeros((n_users, n_users))
        
        # Calculate similarity between each pair of users
        for i in range(n_users):
            for j in range(i, n_users):
                if i == j:
                    # A user is perfectly similar to themselves
                    similarity_matrix[i, j] = 1.0
                else:
                    # Calculate similarity between users i and j
                    similarity = self._calculate_user_similarity(
                        ratings_matrix[i], ratings_matrix[j]
                    )
                    # Similarity is symmetric
                    similarity_matrix[i, j] = similarity
                    similarity_matrix[j, i] = similarity
        
        return similarity_matrix
    
    def _calculate_user_similarity(self, user1_ratings: np.ndarray, user2_ratings: np.ndarray) -> float:
        """
        Calculate similarity between two users based on their ratings.
        
        Args:
            user1_ratings: Ratings vector for the first user
            user2_ratings: Ratings vector for the second user
            
        Returns:
            Similarity score between 0 and 1
        """
        # Get indices where both users have rated items
        mask = np.logical_and(user1_ratings > 0, user2_ratings > 0)
        
        # If they have no items in common, return 0
        if not np.any(mask):
            return 0.0
        
        # Extract ratings for common items
        user1_common = user1_ratings[mask]
        user2_common = user2_ratings[mask]
        
        # Calculate similarity based on the specified method
        if self._similarity_method == "cosine":
            return self._cosine_similarity(user1_common, user2_common)
        elif self._similarity_method == "pearson":
            return self._pearson_similarity(user1_common, user2_common)
        elif self._similarity_method == "jaccard":
            return self._jaccard_similarity(user1_ratings > 0, user2_ratings > 0)
        else:
            logger.warning(f"Unknown similarity method: {self._similarity_method}, using cosine similarity")
            return self._cosine_similarity(user1_common, user2_common)
    
    def _cosine_similarity(self, v1: np.ndarray, v2: np.ndarray) -> float:
        """
        Calculate cosine similarity between two vectors.
        
        Args:
            v1: First vector
            v2: Second vector
            
        Returns:
            Cosine similarity between the vectors
        """
        # Reason: Handle edge cases to avoid division by zero
        if np.all(v1 == 0) or np.all(v2 == 0):
            return 0.0
            
        # Calculate dot product and magnitudes
        dot_product = np.dot(v1, v2)
        magnitude_v1 = np.sqrt(np.sum(v1 ** 2))
        magnitude_v2 = np.sqrt(np.sum(v2 ** 2))
        
        # Calculate cosine similarity
        similarity = dot_product / (magnitude_v1 * magnitude_v2)
        
        # Ensure the result is between 0 and 1
        return max(0.0, min(similarity, 1.0))
    
    def _pearson_similarity(self, v1: np.ndarray, v2: np.ndarray) -> float:
        """
        Calculate Pearson correlation coefficient between two vectors.
        
        Args:
            v1: First vector
            v2: Second vector
            
        Returns:
            Pearson correlation between the vectors
        """
        # Reason: Handle edge cases where variance is zero
        if len(v1) < 2 or np.std(v1) == 0 or np.std(v2) == 0:
            return 0.0
            
        # Calculate means
        v1_mean = np.mean(v1)
        v2_mean = np.mean(v2)
        
        # Calculate numerator (covariance)
        numerator = np.sum((v1 - v1_mean) * (v2 - v2_mean))
        
        # Calculate denominator (product of standard deviations)
        denominator = np.sqrt(np.sum((v1 - v1_mean) ** 2) * np.sum((v2 - v2_mean) ** 2))
        
        # Avoid division by zero
        if denominator == 0:
            return 0.0
            
        # Calculate correlation
        correlation = numerator / denominator
        
        # Convert from [-1, 1] to [0, 1] range
        return (correlation + 1) / 2
    
    def _jaccard_similarity(self, v1: np.ndarray, v2: np.ndarray) -> float:
        """
        Calculate Jaccard similarity between two binary vectors.
        
        Args:
            v1: First binary vector
            v2: Second binary vector
            
        Returns:
            Jaccard similarity between the vectors
        """
        # Calculate intersection and union
        intersection = np.sum(np.logical_and(v1, v2))
        union = np.sum(np.logical_or(v1, v2))
        
        # Avoid division by zero
        if union == 0:
            return 0.0
            
        # Calculate Jaccard similarity
        return intersection / union
    
    def _get_user_index(self, user_id: int) -> Optional[int]:
        """
        Get the index of a user in the ratings matrix.
        
        Args:
            user_id: The ID of the user
            
        Returns:
            The index of the user or None if not found
        """
        try:
            return self._user_ids.index(user_id)
        except ValueError:
            logger.warning(f"User ID {user_id} not found in training data")
            return None
    
    def _get_item_index(self, item_id: int) -> Optional[int]:
        """
        Get the index of an item in the ratings matrix.
        
        Args:
            item_id: The ID of the item
            
        Returns:
            The index of the item or None if not found
        """
        try:
            return self._item_ids.index(item_id)
        except ValueError:
            logger.warning(f"Item ID {item_id} not found in training data")
            return None
    
    def recommend(self, user_id: int, n: int = 10, **kwargs) -> List[Dict[str, Any]]:
        """
        Generate recommendations for a specific user using collaborative filtering.
        
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
            # Get the user index
            user_idx = self._get_user_index(user_id)
            
            # Handle new users not in the training data
            if user_idx is None:
                logger.warning(f"User {user_id} not in training data, using fallback recommendations")
                return self._fallback_recommendations(n)
            
            # Get the user's ratings and user similarities
            user_ratings = np.array(self._ratings_matrix[user_idx])
            user_similarities = self._user_similarity_matrix[user_idx]
            
            # Calculate predicted ratings for all items
            predicted_ratings = {}
            
            # Iterate through all items
            for item_idx, item_id in enumerate(self._item_ids):
                # Skip items the user has already rated
                if user_ratings[item_idx] > 0:
                    continue
                
                # Calculate weighted sum of other users' ratings
                weighted_ratings = 0.0
                similarity_sum = 0.0
                
                # Consider ratings from other users
                for other_user_idx, similarity in enumerate(user_similarities):
                    # Skip the current user or users with zero similarity
                    if other_user_idx == user_idx or similarity <= 0:
                        continue
                    
                    # Get the other user's rating for this item
                    other_rating = self._ratings_matrix[other_user_idx][item_idx]
                    
                    # Skip if the other user hasn't rated this item
                    if other_rating == 0:
                        continue
                    
                    # Add weighted rating
                    weighted_ratings += similarity * other_rating
                    similarity_sum += similarity
                
                # Calculate predicted rating if we have any data
                if similarity_sum > 0:
                    predicted_ratings[item_id] = weighted_ratings / similarity_sum
            
            # Filter already rated items and sort by predicted rating
            filtered_ratings = self.filter_already_rated(user_id, predicted_ratings)
            sorted_items = sorted(
                filtered_ratings.items(), key=lambda x: x[1], reverse=True
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
                        "recommendation_type": "collaborative"
                    })
            
            logger.info(f"Generated {len(recommendations)} collaborative filtering recommendations for user {user_id}")
            return recommendations
        except Exception as e:
            logger.error(f"Error generating recommendations: {str(e)}")
            raise
    
    def _fallback_recommendations(self, n: int = 10) -> List[Dict[str, Any]]:
        """
        Generate fallback recommendations for new users.
        
        Args:
            n: The number of recommendations to generate
            
        Returns:
            A list of dictionaries containing recommended item details
        """
        logger.info(f"Generating fallback recommendations")
        
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
            # Get user and item indices
            user_idx = self._get_user_index(user_id)
            item_idx = self._get_item_index(item_id)
            
            if user_idx is None or item_idx is None:
                return "This item was recommended based on its overall popularity."
                
            # Get similar users who liked this item
            similar_users = []
            for other_user_idx, similarity in enumerate(self._user_similarity_matrix[user_idx]):
                # Skip the current user or users with low similarity
                if other_user_idx == user_idx or similarity < 0.5:
                    continue
                
                # Check if the other user rated this item highly
                if self._ratings_matrix[other_user_idx][item_idx] >= 4.0:
                    # Get the actual user ID
                    other_user_id = self._user_ids[other_user_idx]
                    user = UserModel.find_by_id(other_user_id)
                    if user:
                        similar_users.append((user, similarity))
            
            # Sort by similarity
            similar_users.sort(key=lambda x: x[1], reverse=True)
            
            # Generate explanation
            if similar_users:
                # Get item details
                item = ItemModel.find_by_id(item_id)
                item_name = item.name if item else f"Item {item_id}"
                
                # Create explanation based on similar users
                if len(similar_users) == 1:
                    user = similar_users[0][0]
                    return f"{item_name} was recommended because a user with similar tastes gave it a high rating."
                else:
                    return f"{item_name} was recommended because {len(similar_users)} users with similar tastes gave it high ratings."
            else:
                return "This item was recommended based on the ratings of users with similar preferences."
        except Exception as e:
            logger.error(f"Error generating explanation: {str(e)}")
            return "This recommendation is based on collaborative filtering techniques."
    
    def get_similarity(self, item_id1: int, item_id2: int) -> float:
        """
        Calculate the similarity between two items based on user ratings.
        
        Args:
            item_id1: The ID of the first item
            item_id2: The ID of the second item
            
        Returns:
            A similarity score between 0 and 1
        """
        logger.info(f"Calculating similarity between items {item_id1} and {item_id2}")
        self.check_trained()
        
        try:
            # Get item indices
            item_idx1 = self._get_item_index(item_id1)
            item_idx2 = self._get_item_index(item_id2)
            
            if item_idx1 is None or item_idx2 is None:
                return 0.0
                
            # Extract ratings for both items
            item1_ratings = np.array([self._ratings_matrix[u][item_idx1] for u in range(len(self._user_ids))])
            item2_ratings = np.array([self._ratings_matrix[u][item_idx2] for u in range(len(self._user_ids))])
            
            # Calculate similarity using the specified method
            if self._similarity_method == "cosine":
                return self._cosine_similarity(item1_ratings, item2_ratings)
            elif self._similarity_method == "pearson":
                return self._pearson_similarity(item1_ratings, item2_ratings)
            elif self._similarity_method == "jaccard":
                return self._jaccard_similarity(item1_ratings > 0, item2_ratings > 0)
            else:
                return self._cosine_similarity(item1_ratings, item2_ratings)
        except Exception as e:
            logger.error(f"Error calculating item similarity: {str(e)}")
            return 0.0
