"""
UI Components Module.

This module provides reusable UI components for the Streamlit interface.
"""
import logging
import streamlit as st
from typing import Dict, Any, List, Callable, Optional
from utils.config import THEME_COLOR, DEFAULT_AVATAR
from models.user_model import UserModel
from models.item_model import ItemModel

logger = logging.getLogger(__name__)


def show_header(title: str, subtitle: Optional[str] = None) -> None:
    """
    Display a header with title and optional subtitle.
    
    Args:
        title: The main title text
        subtitle: Optional subtitle text
    """
    st.markdown(f"<h1 style='color:{THEME_COLOR}'>{title}</h1>", unsafe_allow_html=True)
    
    if subtitle:
        st.markdown(f"<h3>{subtitle}</h3>", unsafe_allow_html=True)
    
    st.markdown("---")


def show_user_profile(user: UserModel) -> None:
    """
    Display user profile information.
    
    Args:
        user: The user model to display
    """
    col1, col2 = st.columns([1, 3])
    
    with col1:
        # Display user profile image if available, otherwise use default avatar
        image_to_display = user.profile_image if user.profile_image else DEFAULT_AVATAR
        st.image(image_to_display, width=100)
        
    with col2:
        st.markdown(f"### {user.username}")
        
        if user.first_name or user.last_name:
            name = f"{user.first_name or ''} {user.last_name or ''}".strip()
            st.markdown(f"**Name:** {name}")
            
        st.markdown(f"**Email:** {user.email}")
        
        if user.last_login:
            last_login_str = user.last_login.strftime('%Y-%m-%d %H:%M') if user.last_login else "Never"
            st.markdown(f"**Last Login:** {last_login_str}")
        
        created_at_str = user.created_at.strftime('%Y-%m-%d') if user.created_at else "Unknown"
        st.markdown(f"**Member Since:** {created_at_str}")


def show_recommendation_card(item: Dict[str, Any], 
                           on_click: Optional[Callable] = None,
                           on_rate: Optional[Callable] = None) -> None:
    """
    Display a recommendation card for an item.
    
    Args:
        item: Dictionary containing item details
        on_click: Optional callback when the item is clicked
        on_rate: Optional callback when the item is rated
    """
    # Create a card with shadow and border
    st.markdown("""
    <style>
    .item-card {
        padding: 1.5rem;
        border-radius: 0.5rem;
        background-color: white;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        margin-bottom: 1rem;
    }
    </style>
    """, unsafe_allow_html=True)
    
    with st.container():
        st.markdown('<div class="item-card">', unsafe_allow_html=True)
        
        # Item name and category
        st.markdown(f"### {item['name']}")
        st.markdown(f"**Category:** {item['category']}")
        
        # Description (if available)
        if item.get('description'):
            st.markdown(f"**Description:** {item['description']}")
        
        # Score and recommendation type
        col1, col2 = st.columns(2)
        with col1:
            if 'score_percent' in item:
                st.markdown(f"**Match:** {item['score_percent']}")
            elif 'score' in item:
                st.markdown(f"**Match:** {item['score'] * 100:.1f}%")
        
        with col2:
            if 'recommendation_type' in item:
                st.markdown(f"**Type:** {item['recommendation_type'].title()}")
        
        # Buttons for interaction
        button_col1, button_col2 = st.columns(2)
        
        with button_col1:
            if on_click and st.button("View Details", key=f"view_{item['item_id']}"):
                on_click(item['item_id'])
        
        with button_col2:
            if on_rate:
                rating = st.select_slider(
                    "Rate this item",
                    options=[1, 2, 3, 4, 5],
                    value=3,
                    key=f"rate_{item['item_id']}"
                )
                if st.button("Submit Rating", key=f"submit_{item['item_id']}"):
                    on_rate(item['item_id'], rating)
        
        st.markdown('</div>', unsafe_allow_html=True)


def show_item_details(item: ItemModel) -> None:
    """
    Display detailed information about an item.
    
    Args:
        item: The item to display details for
    """
    st.markdown(f"## {item.name}")
    st.markdown(f"**Category:** {item.category}")
    
    if item.description:
        st.markdown("### Description")
        st.markdown(item.description)
    
    st.markdown("### Features")
    
    # Display features as a table
    if item.features:
        feature_data = []
        for key, value in item.features.items():
            if isinstance(value, (int, float, str, bool)):
                feature_data.append({"Feature": key, "Value": value})
        
        if feature_data:
            st.table(feature_data)
        else:
            st.markdown("No feature details available")
    else:
        st.markdown("No features available")
    
    # Display metadata
    if item.metadata:
        st.markdown("### Additional Information")
        
        meta_data = []
        for key, value in item.metadata.items():
            if isinstance(value, (int, float, str, bool)):
                meta_data.append({"Attribute": key, "Value": value})
        
        if meta_data:
            st.table(meta_data)


def show_sidebar_navigation(user: Optional[UserModel] = None) -> str:
    """
    Display sidebar navigation menu.
    
    Args:
        user: Optional user model for personalized navigation
        
    Returns:
        The selected navigation page
    """
    st.sidebar.markdown(f"## Navigation")
    
    # Default pages
    pages = ["Home"]
    
    # Pages available when logged in
    if user:
        pages.extend([
            "Recommendations", 
            "Browse Items", 
            "My Ratings",
            "Profile"
        ])
    else:
        pages.extend(["Login", "Register"])
    
    # Add admin pages if user has admin privileges
    if user and user.preferences.get("is_admin", False):
        pages.append("Admin")
    
    # Create a radio button for page selection
    selected_page = st.sidebar.radio("Go to", pages)
    
    # Show logout button if logged in
    if user:
        if st.sidebar.button("Logout"):
            st.session_state.pop("user_id", None)
            st.rerun()
    
    return selected_page


def show_filter_sidebar(categories: List[str]) -> Dict[str, Any]:
    """
    Display sidebar filters for recommendations.
    
    Args:
        categories: List of available categories
        
    Returns:
        Dictionary of selected filter values
    """
    st.sidebar.markdown("## Filters")
    
    filters = {}
    
    # Category filter (multi-select)
    selected_categories = st.sidebar.multiselect(
        "Categories",
        categories,
        default=None
    )
    if selected_categories:
        filters["category"] = selected_categories
    
    # Recommendation strategy
    strategy = st.sidebar.selectbox(
        "Recommendation Strategy",
        ["hybrid", "collaborative", "content-based"]
    )
    filters["strategy"] = strategy
    
    # Number of recommendations
    count = st.sidebar.slider(
        "Number of Recommendations",
        min_value=5,
        max_value=20,
        value=10,
        step=5
    )
    filters["count"] = count
    
    # Diversity setting
    diversity = st.sidebar.slider(
        "Diversity Factor",
        min_value=0.0,
        max_value=1.0,
        value=0.3,
        step=0.1,
        help="Higher values prioritize diversity over relevance"
    )
    filters["diversity"] = diversity
    
    return filters


def show_error(message: str) -> None:
    """
    Display an error message.
    
    Args:
        message: The error message to display
    """
    st.error(message)


def show_success(message: str) -> None:
    """
    Display a success message.
    
    Args:
        message: The success message to display
    """
    st.success(message)


def show_info(message: str) -> None:
    """
    Display an info message.
    
    Args:
        message: The info message to display
    """
    st.info(message)
