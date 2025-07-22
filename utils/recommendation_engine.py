"""
Recommendation Engine Module.

This module implements the core recommendation engine that orchestrates the recommendation process.
"""
import logging
from typing import List, Dict, Any, Optional, Union
import random
from models.user_model import UserModel
from models.item_model import ItemModel
from models.rating_model import RatingModel
from strategies.recommendation_strategy import RecommendationStrategy
from .recommendation_factory import RecommendationFactory

logger = logging.getLogger(__name__)


class RecommendationEngine:
    """
    Core recommendation engine that orchestrates the recommendation process.
    
    This class is responsible for managing recommendation strategies, processing user inputs,
    and generating recommendations. It follows the Template Method pattern for common workflows.
    """
    
    def __init__(self, default_strategy: str = "hybrid"):
        """
        Initialize the recommendation engine.
        
        Args:
            default_strategy: The default recommendation strategy type to use
        """
        self._strategies = {}
        self._default_strategy_type = default_strategy
        self._default_strategy = None
        logger.info(f"Initialized RecommendationEngine with default strategy '{default_strategy}'")
    
    def initialize(self) -> None:
        """
        Initialize the recommendation engine and load default strategy.
        
        This method must be called before using the engine for recommendations.
        """
        logger.info("Initializing recommendation engine")
        
        try:
            # Create and train the default strategy
            self._default_strategy = self.get_strategy(self._default_strategy_type)
            
            if not self._default_strategy.is_trained:
                self._default_strategy.train()
                
            logger.info("Recommendation engine initialized successfully")
        except Exception as e:
            logger.error(f"Error initializing recommendation engine: {str(e)}")
            raise
    
    def get_strategy(self, strategy_type: str, **kwargs) -> RecommendationStrategy:
        """
        Get a recommendation strategy of the specified type.
        
        If a strategy of this type has already been created, return the existing instance.
        Otherwise, create a new instance.
        
        Args:
            strategy_type: The type of strategy to get
            **kwargs: Additional parameters to pass to the strategy constructor if creating new
            
        Returns:
            An instance of the specified strategy type
        """
        logger.debug(f"Getting recommendation strategy of type '{strategy_type}'")
        
        # Return existing strategy if available
        if strategy_type in self._strategies:
            return self._strategies[strategy_type]
            
        # Create new strategy
        strategy = RecommendationFactory.create_strategy(strategy_type, **kwargs)
        
        # Train the strategy
        if not strategy.is_trained:
            strategy.train()
            
        # Cache the strategy
        self._strategies[strategy_type] = strategy
        
        return strategy
    
    def recommend(
        self, 
        user_id: int, 
        strategy_type: Optional[str] = None,
        n: int = 10,
        filters: Optional[Dict[str, Any]] = None,
        **kwargs
    ) -> List[Dict[str, Any]]:
        """
        Generate recommendations for a user.
        
        Args:
            user_id: The ID of the user to generate recommendations for
            strategy_type: The type of strategy to use (default: use default strategy)
            n: The number of recommendations to generate
            filters: Optional dictionary of filters to apply to recommendations
            **kwargs: Additional parameters to pass to the strategy
            
        Returns:
            A list of dictionaries containing recommended item details
        """
        logger.info(f"Generating recommendations for user {user_id}")
        
        try:
            # Check if user exists
            user = UserModel.find_by_id(user_id)
            if not user:
                logger.warning(f"User {user_id} not found")
                return []
                
            # Get the strategy to use
            strategy = (
                self.get_strategy(strategy_type) 
                if strategy_type 
                else self._default_strategy
            )
            
            if not strategy:
                logger.error("No strategy available")
                return []
                
            # Generate recommendations
            recommendations = strategy.recommend(user_id, n=n, **kwargs)
            
            # Apply filters if specified
            if filters:
                recommendations = self._apply_filters(recommendations, filters)
                
            # Post-process recommendations (e.g., add additional information)
            recommendations = self._post_process_recommendations(recommendations)
            
            logger.info(f"Generated {len(recommendations)} recommendations for user {user_id}")
            return recommendations
        except Exception as e:
            logger.error(f"Error generating recommendations: {str(e)}")
            raise
    
    def _apply_filters(
        self, 
        recommendations: List[Dict[str, Any]], 
        filters: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """
        Apply filters to recommendations.
        
        Args:
            recommendations: The recommendations to filter
            filters: Dictionary of filters to apply
            
        Returns:
            Filtered recommendations
        """
        logger.debug(f"Applying filters: {filters}")
        filtered_recs = recommendations
        
        # Filter by category
        if "category" in filters:
            categories = filters["category"]
            if isinstance(categories, str):
                categories = [categories]
                
            filtered_recs = [
                rec for rec in filtered_recs 
                if "category" in rec and rec["category"] in categories
            ]
            
        # Filter by minimum score
        if "min_score" in filters and isinstance(filters["min_score"], (int, float)):
            min_score = float(filters["min_score"])
            filtered_recs = [
                rec for rec in filtered_recs 
                if "score" in rec and rec["score"] >= min_score
            ]
            
        # Add more filters as needed
            
        logger.debug(f"Filtered recommendations from {len(recommendations)} to {len(filtered_recs)}")
        return filtered_recs
    
    def _post_process_recommendations(
        self, 
        recommendations: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        Post-process recommendations to add additional information or formatting.
        
        Args:
            recommendations: The recommendations to post-process
            
        Returns:
            Post-processed recommendations
        """
        processed_recs = []
        
        for rec in recommendations:
            # Add any additional information or formatting
            processed_rec = rec.copy()
            
            # Ensure all recommendations have consistent fields
            processed_rec.setdefault("score", 0.0)
            processed_rec.setdefault("recommendation_type", "unknown")
            
            # Format the score as a percentage
            processed_rec["score_percent"] = f"{processed_rec['score'] * 100:.1f}%"
            
            processed_recs.append(processed_rec)
            
        return processed_recs
    
    def explain_recommendation(
        self, 
        user_id: int, 
        item_id: int,
        strategy_type: Optional[str] = None
    ) -> str:
        """
        Generate an explanation for why an item was recommended to a user.
        
        Args:
            user_id: The ID of the user
            item_id: The ID of the recommended item
            strategy_type: The type of strategy to use for explanation
            
        Returns:
            A human-readable explanation string
        """
        logger.info(f"Explaining recommendation of item {item_id} to user {user_id}")
        
        try:
            # Get the strategy to use
            strategy = (
                self.get_strategy(strategy_type) 
                if strategy_type 
                else self._default_strategy
            )
            
            if not strategy:
                logger.error("No strategy available")
                return "Unable to explain this recommendation."
                
            # Get explanation from the strategy
            explanation = strategy.explain(user_id, item_id)
            
            logger.info(f"Generated explanation for user {user_id}, item {item_id}")
            return explanation
        except Exception as e:
            logger.error(f"Error explaining recommendation: {str(e)}")
            return "Unable to generate an explanation for this recommendation."
    
    def update_item_popularity(self, item_id: int) -> None:
        """
        Update the popularity score of an item based on ratings.
        
        Args:
            item_id: The ID of the item to update
        """
        logger.info(f"Updating popularity score for item {item_id}")
        
        try:
            # Get the average rating for the item
            avg_rating = RatingModel.get_average_rating_for_item(item_id)
            
            # Get the number of ratings
            ratings = RatingModel.find_by_item(item_id)
            num_ratings = len(ratings)
            
            # Calculate popularity score (weighted combination of average rating and number of ratings)
            # This is a simple formula that can be customized
            if num_ratings == 0:
                popularity = 0.0
            else:
                # Normalize number of ratings using a log scale to avoid large numbers dominating
                norm_num_ratings = min(1.0, 0.1 * (1 + num_ratings) / 2)
                
                # Combine average rating and number of ratings
                popularity = (0.7 * avg_rating / 5.0) + (0.3 * norm_num_ratings)
                
                # Ensure score is between 0 and 1
                popularity = max(0.0, min(1.0, popularity))
                
            # Update the item's popularity score
            item = ItemModel.find_by_id(item_id)
            if item:
                item.update_popularity(popularity * 5.0)  # Scale back to 0-5 range
                
            logger.info(f"Updated popularity score for item {item_id} to {popularity * 5.0:.2f}")
        except Exception as e:
            logger.error(f"Error updating item popularity: {str(e)}")
            raise
    
    def get_similar_items(
        self, 
        item_id: int, 
        n: int = 5,
        strategy_type: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Get items similar to the specified item.
        
        Args:
            item_id: The ID of the item to find similar items for
            n: The number of similar items to return
            strategy_type: The type of strategy to use for finding similar items
            
        Returns:
            A list of dictionaries containing similar item details
        """
        logger.info(f"Finding items similar to item {item_id}")
        
        try:
            # Get the strategy to use
            strategy = (
                self.get_strategy(strategy_type) 
                if strategy_type 
                else self._default_strategy
            )
            
            if not strategy:
                logger.error("No strategy available")
                return []
                
            # Get all items
            items = ItemModel.find_all()
            
            # Calculate similarity for each item
            similarities = []
            for item in items:
                # Skip the same item
                if item.id == item_id:
                    continue
                    
                # Calculate similarity
                similarity = strategy.get_similarity(item_id, item.id)
                
                # Add to list if similarity is positive
                if similarity > 0:
                    similarities.append((item, similarity))
            
            # Sort by similarity and take top n
            similar_items = sorted(similarities, key=lambda x: x[1], reverse=True)[:n]
            
            # Format results
            results = []
            for item, similarity in similar_items:
                results.append({
                    "item_id": item.id,
                    "name": item.name,
                    "description": item.description,
                    "category": item.category,
                    "similarity": similarity,
                    "similarity_percent": f"{similarity * 100:.1f}%"
                })
                
            logger.info(f"Found {len(results)} items similar to item {item_id}")
            return results
        except Exception as e:
            logger.error(f"Error finding similar items: {str(e)}")
            raise
    
    def get_diverse_recommendations(
        self, 
        user_id: int,
        n: int = 10,
        diversity_factor: float = 0.3,
        **kwargs
    ) -> List[Dict[str, Any]]:
        """
        Generate diverse recommendations for a user.
        
        This method aims to provide a more diverse set of recommendations by
        balancing relevance with diversity.
        
        Args:
            user_id: The ID of the user to generate recommendations for
            n: The number of recommendations to generate
            diversity_factor: How much to prioritize diversity (0.0 to 1.0)
            **kwargs: Additional parameters
            
        Returns:
            A list of dictionaries containing recommended item details
        """
        logger.info(f"Generating diverse recommendations for user {user_id}")
        
        try:
            # Get more recommendations than needed to allow for diversification
            recommendations = self.recommend(user_id, n=n*3, **kwargs)
            
            if len(recommendations) <= n:
                return recommendations
                
            # Initialize selected recommendations with the highest-scored item
            selected = [recommendations[0]]
            recommendations = recommendations[1:]
            
            # Select the remaining items
            for _ in range(min(n - 1, len(recommendations))):
                # Calculate diversity score for each remaining item
                diversity_scores = []
                
                for i, rec in enumerate(recommendations):
                    # Calculate average similarity to already selected items
                    avg_similarity = 0.0
                    for selected_rec in selected:
                        # Use the default strategy for similarity calculation
                        similarity = self._default_strategy.get_similarity(
                            rec["item_id"], 
                            selected_rec["item_id"]
                        )
                        avg_similarity += similarity
                        
                    if selected:
                        avg_similarity /= len(selected)
                        
                    # Calculate diversity score (inverse of similarity)
                    diversity = 1.0 - avg_similarity
                    
                    # Calculate combined score (weighted average of recommendation score and diversity)
                    combined_score = (
                        (1.0 - diversity_factor) * rec["score"] + 
                        diversity_factor * diversity
                    )
                    
                    diversity_scores.append((i, combined_score))
                
                # Select the item with the highest combined score
                if diversity_scores:
                    best_index, _ = max(diversity_scores, key=lambda x: x[1])
                    selected.append(recommendations[best_index])
                    recommendations.pop(best_index)
                else:
                    break
            
            logger.info(f"Generated {len(selected)} diverse recommendations for user {user_id}")
            return selected
        except Exception as e:
            logger.error(f"Error generating diverse recommendations: {str(e)}")
            raise
