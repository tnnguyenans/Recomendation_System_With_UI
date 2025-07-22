"""
Observer Pattern Module.

This module implements the Observer design pattern for tracking user behavior and system events.
"""
import logging
from abc import ABC, abstractmethod
from typing import List, Dict, Any, Set
import datetime

logger = logging.getLogger(__name__)


class Observer(ABC):
    """
    Abstract Observer class for the Observer design pattern.
    
    Defines the interface that all concrete observers must implement.
    """
    
    @abstractmethod
    def update(self, subject: 'Subject', event_type: str, data: Dict[str, Any]) -> None:
        """
        Update method called by subjects when they change state.
        
        Args:
            subject: The subject that triggered the update
            event_type: The type of event that occurred
            data: Additional data about the event
        """
        pass


class Subject(ABC):
    """
    Abstract Subject class for the Observer design pattern.
    
    Defines the interface that all concrete subjects must implement.
    """
    
    def __init__(self):
        """Initialize the subject with an empty set of observers."""
        self._observers: Set[Observer] = set()
        logger.debug(f"Initialized {self.__class__.__name__}")
    
    def attach(self, observer: Observer) -> None:
        """
        Attach an observer to the subject.
        
        Args:
            observer: The observer to attach
        """
        self._observers.add(observer)
        logger.debug(f"Observer {observer.__class__.__name__} attached to {self.__class__.__name__}")
    
    def detach(self, observer: Observer) -> None:
        """
        Detach an observer from the subject.
        
        Args:
            observer: The observer to detach
        """
        if observer in self._observers:
            self._observers.remove(observer)
            logger.debug(f"Observer {observer.__class__.__name__} detached from {self.__class__.__name__}")
    
    def notify(self, event_type: str, data: Dict[str, Any]) -> None:
        """
        Notify all observers of a state change.
        
        Args:
            event_type: The type of event that occurred
            data: Additional data about the event
        """
        logger.debug(f"Notifying observers of event '{event_type}'")
        
        for observer in self._observers:
            observer.update(self, event_type, data)


class UserActivityObserver(Observer):
    """
    Concrete observer that tracks user activity for analytics purposes.
    
    Implements the Observer interface to track various user interactions.
    """
    
    def __init__(self):
        """Initialize the observer with empty activity logs."""
        self._activities: List[Dict[str, Any]] = []
        logger.info("Initialized UserActivityObserver")
    
    def update(self, subject: Subject, event_type: str, data: Dict[str, Any]) -> None:
        """
        Update method called when user activity occurs.
        
        Args:
            subject: The subject that triggered the update
            event_type: The type of event that occurred
            data: Additional data about the event
        """
        # Add timestamp to the activity data
        activity = {
            "timestamp": datetime.datetime.utcnow(),
            "event_type": event_type,
            **data
        }
        
        # Add activity to the log
        self._activities.append(activity)
        
        # Log the activity
        logger.info(f"User activity: {event_type} - User ID: {data.get('user_id', 'unknown')}")
        
        # Additional processing based on event type
        if event_type == "rating_created":
            self._process_rating_event(data)
        elif event_type == "recommendation_clicked":
            self._process_recommendation_click(data)
        elif event_type == "user_login":
            self._process_user_login(data)
    
    def _process_rating_event(self, data: Dict[str, Any]) -> None:
        """
        Process a rating event.
        
        Args:
            data: Data about the rating event
        """
        user_id = data.get("user_id")
        item_id = data.get("item_id")
        rating = data.get("rating_value")
        
        if user_id and item_id and rating is not None:
            logger.debug(f"User {user_id} rated item {item_id} with {rating}")
            
            # Additional processing could be done here, such as:
            # - Updating recommendation models
            # - Triggering re-training of recommendation algorithms
            # - Storing analytics data to a database
    
    def _process_recommendation_click(self, data: Dict[str, Any]) -> None:
        """
        Process a recommendation click event.
        
        Args:
            data: Data about the recommendation click event
        """
        user_id = data.get("user_id")
        item_id = data.get("item_id")
        recommendation_type = data.get("recommendation_type")
        
        if user_id and item_id:
            logger.debug(f"User {user_id} clicked on {recommendation_type} recommendation for item {item_id}")
            
            # Additional processing could be done here
    
    def _process_user_login(self, data: Dict[str, Any]) -> None:
        """
        Process a user login event.
        
        Args:
            data: Data about the user login event
        """
        user_id = data.get("user_id")
        
        if user_id:
            logger.debug(f"User {user_id} logged in")
            
            # Additional processing could be done here, such as:
            # - Updating last login timestamp
            # - Tracking session information
    
    def get_user_activities(self, user_id: int, limit: int = 100) -> List[Dict[str, Any]]:
        """
        Get recent activities for a specific user.
        
        Args:
            user_id: The ID of the user
            limit: Maximum number of activities to return
            
        Returns:
            List of user activities, most recent first
        """
        user_activities = [
            activity for activity in self._activities
            if activity.get("user_id") == user_id
        ]
        
        # Sort by timestamp in descending order and limit the results
        sorted_activities = sorted(
            user_activities,
            key=lambda a: a["timestamp"],
            reverse=True
        )[:limit]
        
        return sorted_activities
    
    def get_event_count(self, event_type: str) -> int:
        """
        Get the count of a specific event type.
        
        Args:
            event_type: The type of event to count
            
        Returns:
            Count of events of the specified type
        """
        return sum(1 for activity in self._activities if activity["event_type"] == event_type)
    
    def clear_activities(self) -> None:
        """Clear all stored activities."""
        self._activities = []
        logger.info("Cleared all user activities")
