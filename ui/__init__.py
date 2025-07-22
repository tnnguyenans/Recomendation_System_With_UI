"""
UI Package.

This package contains the user interface components for the recommendation system.
"""
from .components import (
    show_header,
    show_user_profile,
    show_recommendation_card,
    show_item_details,
    show_sidebar_navigation,
    show_filter_sidebar,
    show_error,
    show_success,
    show_info
)
from .pages import (
    show_home_page,
    show_login_page,
    show_register_page,
    show_profile_page,
    show_recommendations_page,
    show_browse_items_page,
    show_my_ratings_page,
    show_admin_page,
    show_item_detail_page
)

__all__ = [
    'show_header',
    'show_user_profile',
    'show_recommendation_card',
    'show_item_details',
    'show_sidebar_navigation',
    'show_filter_sidebar',
    'show_error',
    'show_success',
    'show_info',
    'show_home_page',
    'show_login_page',
    'show_register_page',
    'show_profile_page',
    'show_recommendations_page',
    'show_browse_items_page',
    'show_my_ratings_page',
    'show_admin_page',
    'show_item_detail_page'
]
