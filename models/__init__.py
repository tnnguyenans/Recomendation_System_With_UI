"""
Models Package.

This package contains all the data models used in the recommendation system.
"""
from .base_model import BaseModel
from .user_model import UserModel
from .item_model import ItemModel
from .rating_model import RatingModel

__all__ = ['BaseModel', 'UserModel', 'ItemModel', 'RatingModel']
