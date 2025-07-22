"""
Hybrid Filtering Strategy Module.

This module implements a hybrid recommendation algorithm that combines multiple strategies.
"""
import logging
from typing import List, Dict, Any, Tuple
from .recommendation_strategy import BaseRecommendationStrategy
from .collaborative_filtering import CollaborativeFilteringStrategy
from .content_based_filtering import ContentBasedFilteringStrategy
from models.item_model import ItemModel

logger = logging.getLogger(__name__)


class HybridFilteringStrategy(BaseRecommendationStrategy):
    """
    Hybrid filtering recommendation strategy.
    
    Combines multiple recommendation strategies (collaborative and content-based)
    to provide more accurate and diverse recommendations.
    """
    
    def __init__(self, strategies: List[Tuple[BaseRecommendationStrategy, float]] = None):
        """
        Initialize the hybrid filtering strategy.
        
        Args:
            strategies: List of tuples containing (strategy, weight) pairs
                        If None, default strategies will be created
        """
        super().__init__()
        
        # Use provided strategies or create default ones
        if strategies:
            self._strategies = strategies
        else:
            self._strategies = [
                (CollaborativeFilteringStrategy(), 0.6),
                (ContentBasedFilteringStrategy(), 0.4)
            ]
            
        logger.info(f"Initialized HybridFilteringStrategy with {len(self._strategies)} strategies")
    
    def train(self, data: Any = None) -> None:
        """
        Train all underlying recommendation strategies.
        
        Args:
            data: Optional pre-loaded data. If None, data will be loaded from the database.
        """
        logger.info("Training hybrid filtering model")
        
        try:
            # Train each strategy
            for strategy, _ in self._strategies:
                if not strategy.is_trained:
                    strategy.train(data)
            
            self._is_trained = True
            logger.info("Hybrid filtering model trained successfully")
        except Exception as e:
            logger.error(f"Error training hybrid filtering model: {str(e)}")
            raise
    
    def recommend(self, user_id: int, n: int = 10, **kwargs) -> List[Dict[str, Any]]:
        """
        Generate recommendations using a hybrid approach.
        
        Args:
            user_id: The ID of the user to generate recommendations for
            n: The number of recommendations to generate
            **kwargs: Additional parameters
            
        Returns:
            A list of dictionaries containing recommended item details
        """
        logger.info(f"Generating hybrid recommendations for user {user_id}")
        self.check_trained()
        
        try:
            # Get recommendation weights parameter or use strategy weights
            weights = kwargs.get("weights", [weight for _, weight in self._strategies])
            
            # Normalize weights if necessary
            weight_sum = sum(weights)
            if weight_sum != 1.0:
                weights = [w / weight_sum for w in weights]
            
            # Get recommendations from each strategy
            all_recommendations = {}
            strategy_names = []
            
            for i, (strategy, _) in enumerate(self._strategies):
                # Get recommendations from this strategy
                strategy_recs = strategy.recommend(user_id, n=n*2, **kwargs)  # Get more recommendations for diversity
                strategy_name = strategy.__class__.__name__
                strategy_names.append(strategy_name)
                
                # Store recommendation scores by item ID
                for rec in strategy_recs:
                    item_id = rec["item_id"]
                    
                    # Initialize if this is the first strategy to recommend this item
                    if item_id not in all_recommendations:
                        all_recommendations[item_id] = {
                            "item_id": item_id,
                            "name": rec["name"],
                            "description": rec.get("description"),
                            "category": rec.get("category"),
                            "scores": [0.0] * len(self._strategies),
                            "recommendation_types": []
                        }
                    
                    # Store the score from this strategy
                    all_recommendations[item_id]["scores"][i] = rec["score"]
                    
                    # Add recommendation type if not already present
                    rec_type = rec.get("recommendation_type", strategy_name)
                    if rec_type not in all_recommendations[item_id]["recommendation_types"]:
                        all_recommendations[item_id]["recommendation_types"].append(rec_type)
            
            # Calculate weighted scores
            for item_id, rec in all_recommendations.items():
                weighted_score = sum(s * w for s, w in zip(rec["scores"], weights))
                rec["score"] = weighted_score
                rec["recommendation_type"] = "hybrid"
            
            # Sort by weighted score and take top n
            sorted_recommendations = sorted(
                all_recommendations.values(), 
                key=lambda x: x["score"],
                reverse=True
            )[:n]
            
            logger.info(f"Generated {len(sorted_recommendations)} hybrid recommendations for user {user_id}")
            return sorted_recommendations
        except Exception as e:
            logger.error(f"Error generating hybrid recommendations: {str(e)}")
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
        logger.info(f"Generating hybrid explanation for user {user_id}, item {item_id}")
        self.check_trained()
        
        try:
            # Get item details
            item = ItemModel.find_by_id(item_id)
            item_name = item.name if item else f"Item {item_id}"
            
            # Collect explanations from each strategy
            explanations = []
            scores = []
            
            for strategy, weight in self._strategies:
                try:
                    # Get explanation from this strategy
                    explanation = strategy.explain(user_id, item_id)
                    
                    # Skip generic explanations
                    if explanation and "based on" not in explanation.lower():
                        explanations.append(explanation)
                    
                    # Try to get a recommendation score
                    strategy_recs = strategy.recommend(user_id, n=100)
                    for rec in strategy_recs:
                        if rec["item_id"] == item_id:
                            scores.append((rec["score"], weight))
                            break
                except Exception:
                    # Skip if a strategy fails
                    pass
            
            # If we have specific explanations, use the best one
            if explanations:
                return explanations[0]
            
            # If we have scores, explain based on the highest weighted score
            if scores:
                best_strategy_index = max(range(len(scores)), key=lambda i: scores[i][0] * scores[i][1])
                strategy_name = self._strategies[best_strategy_index][0].__class__.__name__.replace("Strategy", "")
                
                if "Collaborative" in strategy_name:
                    return f"{item_name} was recommended because users with similar preferences have enjoyed it."
                elif "Content" in strategy_name:
                    return f"{item_name} was recommended because its features match your preferences."
            
            # Default explanation
            return f"{item_name} was recommended using a combination of collaborative and content-based filtering techniques."
        except Exception as e:
            logger.error(f"Error generating hybrid explanation: {str(e)}")
            return "This recommendation is based on a combination of different recommendation techniques."
    
    def get_similarity(self, item_id1: int, item_id2: int) -> float:
        """
        Calculate the similarity between two items using multiple strategies.
        
        Args:
            item_id1: The ID of the first item
            item_id2: The ID of the second item
            
        Returns:
            A weighted similarity score between 0 and 1
        """
        logger.info(f"Calculating hybrid similarity between items {item_id1} and {item_id2}")
        self.check_trained()
        
        try:
            # Get similarity from each strategy
            similarities = []
            
            for strategy, weight in self._strategies:
                try:
                    similarity = strategy.get_similarity(item_id1, item_id2)
                    similarities.append((similarity, weight))
                except Exception:
                    # Skip if a strategy fails
                    pass
            
            # If no strategy could calculate similarity, return 0
            if not similarities:
                return 0.0
                
            # Calculate weighted average
            total_similarity = sum(sim * weight for sim, weight in similarities)
            total_weight = sum(weight for _, weight in similarities)
            
            if total_weight == 0:
                return 0.0
                
            return total_similarity / total_weight
        except Exception as e:
            logger.error(f"Error calculating hybrid item similarity: {str(e)}")
            return 0.0
