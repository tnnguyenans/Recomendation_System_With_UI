"""
UI Pages Module.

This module provides page handlers for the Streamlit interface.
"""
import logging
import streamlit as st
from typing import Dict, Any, List, Optional
from models.user_model import UserModel
from models.item_model import ItemModel
from models.rating_model import RatingModel
from utils.recommendation_engine import RecommendationEngine
from utils.auth import AuthenticationManager
from utils.observer import UserActivityObserver
from utils.config import APP_TITLE, APP_DESCRIPTION, AVAILABLE_STRATEGIES
from .components import (
    show_header, show_user_profile, show_recommendation_card,
    show_item_details, show_filter_sidebar, show_error, show_success, show_info
)

logger = logging.getLogger(__name__)


def show_home_page() -> None:
    """Display the home page."""
    show_header(APP_TITLE, APP_DESCRIPTION)
    
    st.markdown("""
    ## Welcome to the Smart Recommendation Engine!
    
    This system uses advanced algorithms to provide personalized recommendations based on your preferences and behavior.
    
    ### Key Features:
    * Multiple recommendation strategies
    * Personalized recommendations
    * Item discovery and exploration
    * Rating and feedback system
    
    ### Available Recommendation Strategies:
    """)
    
    # Display available strategies
    for strategy_key, strategy_name in AVAILABLE_STRATEGIES.items():
        st.markdown(f"* **{strategy_name}**: {_get_strategy_description(strategy_key)}")
    
    # Show call to action
    if "user_id" not in st.session_state:
        st.markdown("### Get Started")
        col1, col2 = st.columns(2)
        with col1:
            if st.button("Login"):
                st.session_state["page"] = "Login"
                st.rerun()
        with col2:
            if st.button("Register"):
                st.session_state["page"] = "Register"
                st.rerun()


def show_login_page() -> None:
    """Display the login page."""
    show_header("Login", "Access your account")
    
    with st.form("login_form"):
        username_email = st.text_input("Username or Email")
        password = st.text_input("Password", type="password")
        
        submitted = st.form_submit_button("Login")
        
        if submitted:
            if not username_email or not password:
                show_error("Please fill in all fields")
            else:
                success, message, user = AuthenticationManager.login_user(username_email, password)
                
                if success and user:
                    # Store user ID in session state
                    st.session_state["user_id"] = user.id
                    
                    # Notify observers of login event
                    if "activity_observer" in st.session_state:
                        observer = st.session_state["activity_observer"]
                        observer.update(None, "user_login", {"user_id": user.id})
                    
                    # Redirect to recommendations page
                    show_success(message)
                    st.session_state["page"] = "Recommendations"
                    st.rerun()
                else:
                    show_error(message)
    
    # Link to registration page
    st.markdown("Don't have an account?")
    if st.button("Register here"):
        st.session_state["page"] = "Register"
        st.rerun()


def show_register_page() -> None:
    """Display the registration page."""
    show_header("Register", "Create a new account")
    
    with st.form("register_form"):
        username = st.text_input("Username")
        email = st.text_input("Email")
        password = st.text_input("Password", type="password")
        password_confirm = st.text_input("Confirm Password", type="password")
        
        col1, col2 = st.columns(2)
        with col1:
            first_name = st.text_input("First Name (Optional)")
        with col2:
            last_name = st.text_input("Last Name (Optional)")
        
        submitted = st.form_submit_button("Register")
        
        if submitted:
            if not username or not email or not password:
                show_error("Please fill in all required fields")
            elif password != password_confirm:
                show_error("Passwords do not match")
            else:
                success, message, user = AuthenticationManager.register_user(
                    username, email, password, first_name, last_name
                )
                
                if success and user:
                    # Store user ID in session state
                    st.session_state["user_id"] = user.id
                    
                    # Notify observers of registration event
                    if "activity_observer" in st.session_state:
                        observer = st.session_state["activity_observer"]
                        observer.update(None, "user_registered", {"user_id": user.id})
                    
                    # Redirect to recommendations page
                    show_success(message)
                    st.session_state["page"] = "Recommendations"
                    st.rerun()
                else:
                    show_error(message)
    
    # Link to login page
    st.markdown("Already have an account?")
    if st.button("Login here"):
        st.session_state["page"] = "Login"
        st.rerun()


def show_profile_page(user: UserModel) -> None:
    """
    Display the user profile page.
    
    Args:
        user: The current user
    """
    show_header("Profile", f"Welcome, {user.username}")
    
    # User profile information
    show_user_profile(user)
    
    st.markdown("---")
    
    # Profile Image Upload
    st.markdown("### Profile Image")
    
    with st.form("profile_image_form"):
        uploaded_image = st.file_uploader("Upload a profile image", type=["jpg", "jpeg", "png"])
        
        if st.form_submit_button("Upload Image"):
            if uploaded_image is not None:
                try:
                    # Read image as bytes
                    image_bytes = uploaded_image.read()
                    
                    # Convert to base64 for storage
                    import base64
                    encoded_image = base64.b64encode(image_bytes).decode()
                    
                    # Update user model with profile image data using the OOP method
                    image_data = f"data:image/{uploaded_image.type.split('/')[-1]};base64,{encoded_image}"
                    success = user.update_profile_image(image_data)
                    
                    if not success:
                        raise Exception("Failed to update profile image")
                    
                    # Log the update
                    logger.info(f"Updated profile image for user {user.id}")
                    show_success("Profile image updated successfully")
                except Exception as e:
                    logger.error(f"Error uploading profile image: {str(e)}")
                    show_error(f"Failed to upload image: {str(e)}")
            else:
                show_info("No image selected")
    
    st.markdown("---")
    
    # User preferences
    st.markdown("### Preferences")
    
    with st.form("preferences_form"):
        # Get current preferences or default values
        preferences = user.preferences or {}
        
        # Email notifications
        email_notifications = st.checkbox(
            "Email Notifications",
            value=preferences.get("email_notifications", True)
        )
        
        # Preferred recommendation strategy
        preferred_strategy = st.selectbox(
            "Preferred Recommendation Strategy",
            list(AVAILABLE_STRATEGIES.keys()),
            format_func=lambda x: AVAILABLE_STRATEGIES[x],
            index=list(AVAILABLE_STRATEGIES.keys()).index(
                preferences.get("preferred_strategy", "hybrid")
            )
        )
        
        # Save preferences
        if st.form_submit_button("Save Preferences"):
            # Update preferences
            updated_preferences = {
                **preferences,
                "email_notifications": email_notifications,
                "preferred_strategy": preferred_strategy
            }
            
            # Save to database
            user.update_preferences(updated_preferences)
            
            show_success("Preferences saved")
    
    # Account settings
    st.markdown("### Account Settings")
    
    with st.form("password_form"):
        current_password = st.text_input("Current Password", type="password")
        new_password = st.text_input("New Password", type="password")
        confirm_password = st.text_input("Confirm New Password", type="password")
        
        if st.form_submit_button("Change Password"):
            if not current_password or not new_password or not confirm_password:
                show_error("Please fill in all fields")
            elif new_password != confirm_password:
                show_error("New passwords do not match")
            else:
                # Verify current password
                if AuthenticationManager.verify_password(user.password_hash, current_password):
                    # Hash the new password
                    new_hash = AuthenticationManager.hash_password(new_password)
                    
                    # Update in the database (directly access the model field)
                    user.password_hash = new_hash
                    user.save()
                    
                    show_success("Password changed successfully")
                else:
                    show_error("Current password is incorrect")


def show_recommendations_page(user: UserModel, engine: RecommendationEngine) -> None:
    """
    Display the recommendations page.
    
    Args:
        user: The current user
        engine: The recommendation engine instance
    """
    show_header("Your Recommendations", f"Personalized for {user.username}")
    
    # Get all categories
    categories = [item.category for item in ItemModel.find_all()]
    unique_categories = list(set(categories))
    
    # Show filters in sidebar
    filters = show_filter_sidebar(unique_categories)
    
    # Show a loading message while generating recommendations
    with st.spinner("Generating personalized recommendations..."):
        try:
            # Check if we should use diverse recommendations
            if filters.get("diversity", 0) > 0:
                recommendations = engine.get_diverse_recommendations(
                    user.id,
                    n=filters.get("count", 10),
                    strategy_type=filters.get("strategy", "hybrid"),
                    diversity_factor=filters.get("diversity", 0.3)
                )
            else:
                # Use regular recommendations
                recommendations = engine.recommend(
                    user.id,
                    n=filters.get("count", 10),
                    strategy_type=filters.get("strategy", "hybrid"),
                    filters={"category": filters.get("category")} if "category" in filters else None
                )
            
            if not recommendations:
                show_info("No recommendations found. Try adjusting your filters or rating more items.")
            else:
                st.markdown(f"### Showing {len(recommendations)} recommendations")
                
                # Define callbacks
                def view_item(item_id):
                    st.session_state["selected_item_id"] = item_id
                    st.session_state["page"] = "ItemDetail"
                    
                    # Notify observers of recommendation click
                    if "activity_observer" in st.session_state:
                        observer = st.session_state["activity_observer"]
                        observer.update(None, "recommendation_clicked", {
                            "user_id": user.id,
                            "item_id": item_id
                        })
                    
                    st.rerun()
                
                def rate_item(item_id, rating_value):
                    # Create or update rating
                    rating = RatingModel.find_by_user_and_item(user.id, item_id)
                    
                    if rating:
                        rating.value = rating_value
                        rating.save()
                    else:
                        rating = RatingModel(
                            user_id=user.id,
                            item_id=item_id,
                            value=rating_value
                        )
                        rating.save()
                    
                    # Notify observers of rating event
                    if "activity_observer" in st.session_state:
                        observer = st.session_state["activity_observer"]
                        observer.update(None, "rating_created", {
                            "user_id": user.id,
                            "item_id": item_id,
                            "rating_value": rating_value
                        })
                    
                    # Update item popularity
                    engine.update_item_popularity(item_id)
                    
                    show_success(f"Rating saved: {rating_value}/5")
                
                # Display recommendations
                for rec in recommendations:
                    show_recommendation_card(rec, on_click=view_item, on_rate=rate_item)
        
        except Exception as e:
            logger.error(f"Error generating recommendations: {str(e)}")
            show_error(f"Error: {str(e)}")


def show_browse_items_page(user: UserModel) -> None:
    """
    Display the browse items page.
    
    Args:
        user: The current user
    """
    show_header("Browse Items", "Explore our catalog")
    
    # Get all categories
    categories = [item.category for item in ItemModel.find_all()]
    unique_categories = list(set(categories))
    
    # Category filter
    selected_category = st.selectbox("Filter by Category", ["All"] + unique_categories)
    
    # Search bar
    search_query = st.text_input("Search Items")
    
    # Get items based on filters
    if selected_category != "All":
        items = ItemModel.find_by_category(selected_category)
    else:
        items = ItemModel.find_all()
    
    # Filter by search query if provided
    if search_query:
        items = [
            item for item in items
            if search_query.lower() in item.name.lower() or 
               (item.description and search_query.lower() in item.description.lower())
        ]
    
    # Display items
    if not items:
        show_info("No items found matching your criteria")
    else:
        st.markdown(f"### Showing {len(items)} items")
        
        # Define callbacks
        def view_item(item_id):
            st.session_state["selected_item_id"] = item_id
            st.session_state["page"] = "ItemDetail"
            st.rerun()
        
        def rate_item(item_id, rating_value):
            # Create or update rating
            rating = RatingModel.find_by_user_and_item(user.id, item_id)
            
            if rating:
                rating.value = rating_value
                rating.save()
            else:
                rating = RatingModel(
                    user_id=user.id,
                    item_id=item_id,
                    value=rating_value
                )
                rating.save()
            
            # Notify observers of rating event
            if "activity_observer" in st.session_state:
                observer = st.session_state["activity_observer"]
                observer.update(None, "rating_created", {
                    "user_id": user.id,
                    "item_id": item_id,
                    "rating_value": rating_value
                })
            
            show_success(f"Rating saved: {rating_value}/5")
        
        # Display items in a grid layout
        cols = st.columns(2)
        for i, item in enumerate(items):
            with cols[i % 2]:
                item_dict = {
                    "item_id": item.id,
                    "name": item.name,
                    "description": item.description,
                    "category": item.category
                }
                show_recommendation_card(item_dict, on_click=view_item, on_rate=rate_item)


def show_my_ratings_page(user: UserModel) -> None:
    """
    Display the user's ratings page.
    
    Args:
        user: The current user
    """
    show_header("My Ratings", "Items you've rated")
    
    # Get user's ratings
    ratings = RatingModel.find_by_user(user.id)
    
    if not ratings:
        show_info("You haven't rated any items yet")
    else:
        st.markdown(f"### You have rated {len(ratings)} items")
        
        # Create table data
        table_data = []
        for rating in ratings:
            item = ItemModel.find_by_id(rating.item_id)
            if item:
                # Use created_at for the initial rating date, updated_at would show the last time the rating was modified
                date_rated = rating.created_at.strftime("%Y-%m-%d") if rating.created_at else "N/A"
                
                table_data.append({
                    "Item": item.name,
                    "Category": item.category,
                    "Your Rating": f"{rating.value}/5",
                    "Date Rated": date_rated
                })
        
        # Display as a table
        st.table(table_data)
        
        # Option to delete ratings
        if st.button("Clear All Ratings"):
            st.warning("This will delete all your ratings. Are you sure?")
            if st.button("Yes, Delete All Ratings", key="confirm_delete"):
                for rating in ratings:
                    rating.delete()
                
                show_success("All ratings deleted")
                st.rerun()


def show_admin_page() -> None:
    """Display the admin page."""
    show_header("Admin Dashboard", "System Management")
    
    # Check if user has admin privileges
    user = UserModel.find_by_id(st.session_state.get("user_id"))
    if not user or not user.preferences.get("is_admin", False):
        show_error("You do not have permission to access this page")
        return
    
    # Admin sections
    tab1, tab2, tab3 = st.tabs(["Users", "Items", "System Stats"])
    
    with tab1:
        st.markdown("### User Management")
        users = UserModel.find_all()
        
        # Create table data
        user_data = []
        for user in users:
            user_data.append({
                "ID": user.id,
                "Username": user.username,
                "Email": user.email,
                "Created": user.created_at.strftime("%Y-%m-%d"),
                "Last Login": user.last_login.strftime("%Y-%m-%d %H:%M") if user.last_login else "Never"
            })
        
        st.table(user_data)
    
    with tab2:
        st.markdown("### Item Management")
        items = ItemModel.find_all()
        
        # Create table data
        item_data = []
        for item in items:
            item_data.append({
                "ID": item.id,
                "Name": item.name,
                "Category": item.category,
                "Popularity": f"{item.popularity:.2f}",
                "Active": "Yes" if item.active else "No"
            })
        
        st.table(item_data)
        
        # Add new item form
        st.markdown("### Add New Item")
        with st.form("add_item_form"):
            name = st.text_input("Item Name")
            category = st.text_input("Category")
            description = st.text_area("Description")
            features_json = st.text_area("Features (JSON format)")
            
            if st.form_submit_button("Add Item"):
                try:
                    # Create new item
                    item = ItemModel(
                        name=name,
                        category=category,
                        description=description
                    )
                    
                    # Parse features if provided
                    if features_json:
                        import json
                        try:
                            features = json.loads(features_json)
                            item.features = features
                        except json.JSONDecodeError:
                            show_error("Invalid JSON for features")
                    
                    # Save to database
                    item.save()
                    
                    show_success("Item added successfully")
                except Exception as e:
                    show_error(f"Error adding item: {str(e)}")
    
    with tab3:
        st.markdown("### System Statistics")
        
        # Count entities
        user_count = len(UserModel.find_all())
        item_count = len(ItemModel.find_all())
        rating_count = len(RatingModel.find_all())
        
        # Display counts
        col1, col2, col3 = st.columns(3)
        col1.metric("Total Users", user_count)
        col2.metric("Total Items", item_count)
        col3.metric("Total Ratings", rating_count)
        
        # Display activity counts if observer exists
        if "activity_observer" in st.session_state:
            observer = st.session_state["activity_observer"]
            
            st.markdown("### Recent Activity")
            
            logins = observer.get_event_count("user_login")
            ratings = observer.get_event_count("rating_created")
            clicks = observer.get_event_count("recommendation_clicked")
            
            col1, col2, col3 = st.columns(3)
            col1.metric("Recent Logins", logins)
            col2.metric("Recent Ratings", ratings)
            col3.metric("Recommendation Clicks", clicks)


def show_item_detail_page(item_id: int, user: UserModel, engine: RecommendationEngine) -> None:
    """
    Display detailed information about a specific item.
    
    Args:
        item_id: The ID of the item to display
        user: The current user
        engine: The recommendation engine instance
    """
    # Get the item
    item = ItemModel.find_by_id(item_id)
    
    if not item:
        show_error("Item not found")
        return
    
    show_header(item.name, f"Category: {item.category}")
    
    # Item details
    show_item_details(item)
    
    # User rating for this item
    st.markdown("### Your Rating")
    
    rating = RatingModel.find_by_user_and_item(user.id, item_id)
    current_rating = rating.value if rating else 3
    
    col1, col2 = st.columns([3, 1])
    
    with col1:
        new_rating = st.slider(
            "Rate this item",
            min_value=1,
            max_value=5,
            value=current_rating,
            step=1
        )
    
    with col2:
        if st.button("Save Rating"):
            if rating:
                rating.value = new_rating
                rating.save()
            else:
                rating = RatingModel(
                    user_id=user.id,
                    item_id=item_id,
                    value=new_rating
                )
                rating.save()
            
            # Notify observers
            if "activity_observer" in st.session_state:
                observer = st.session_state["activity_observer"]
                observer.update(None, "rating_created", {
                    "user_id": user.id,
                    "item_id": item_id,
                    "rating_value": new_rating
                })
            
            # Update item popularity
            engine.update_item_popularity(item_id)
            
            show_success("Rating saved")
    
    # Recommendation explanation
    st.markdown("### Why was this recommended to you?")
    
    try:
        explanation = engine.explain_recommendation(user.id, item_id)
        st.write(explanation)
    except Exception as e:
        logger.error(f"Error getting recommendation explanation: {str(e)}")
        st.write("No explanation available for this item")
    
    # Similar items
    st.markdown("### Similar Items")
    
    try:
        similar_items = engine.get_similar_items(item_id, n=3)
        
        if similar_items:
            cols = st.columns(len(similar_items))
            
            for i, similar_item in enumerate(similar_items):
                with cols[i]:
                    st.markdown(f"#### {similar_item['name']}")
                    st.markdown(f"**Similarity:** {similar_item['similarity_percent']}")
                    st.markdown(f"**Category:** {similar_item['category']}")
                    
                    if st.button("View Item", key=f"similar_{similar_item['item_id']}"):
                        st.session_state["selected_item_id"] = similar_item['item_id']
                        st.session_state["page"] = "ItemDetail"
                        st.rerun()
        else:
            st.write("No similar items found")
    except Exception as e:
        logger.error(f"Error getting similar items: {str(e)}")
        st.write("Similar items could not be loaded")


def _get_strategy_description(strategy_type: str) -> str:
    """
    Get a human-readable description of a recommendation strategy.
    
    Args:
        strategy_type: The type of strategy
        
    Returns:
        A description of the strategy
    """
    descriptions = {
        "collaborative": "Recommends items based on what similar users have liked",
        "content-based": "Recommends items with features similar to what you've liked in the past",
        "hybrid": "Combines multiple strategies for more balanced recommendations"
    }
    
    return descriptions.get(strategy_type, "Unknown strategy type")
