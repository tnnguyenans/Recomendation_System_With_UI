"""
Smart Recommendation Engine Application.

Main application entry point for the Smart Recommendation System.
"""
import logging
import logging.config
import os
import streamlit as st
from dotenv import load_dotenv

# Import custom modules
from models.user_model import UserModel
from models.item_model import ItemModel
from utils.recommendation_engine import RecommendationEngine
from utils.observer import UserActivityObserver
from ui import (
    show_sidebar_navigation,
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
from utils.config import APP_TITLE

# Setup logging
def setup_logging():
    """Configure logging for the application."""
    load_dotenv()
    
    log_level = os.getenv("LOG_LEVEL", "INFO").upper()
    log_file = os.getenv("LOG_FILE", "recommendation_engine.log")
    
    logging_config = {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "standard": {
                "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
            },
        },
        "handlers": {
            "console": {
                "class": "logging.StreamHandler",
                "level": "DEBUG",
                "formatter": "standard",
                "stream": "ext://sys.stdout"
            },
            "file": {
                "class": "logging.FileHandler",
                "level": "DEBUG",
                "formatter": "standard",
                "filename": log_file,
                "mode": "a"
            }
        },
        "loggers": {
            "": {  # Root logger
                "handlers": ["console", "file"],
                "level": log_level,
                "propagate": True
            }
        }
    }
    
    logging.config.dictConfig(logging_config)
    logging.info("Logging configured")


def main():
    """Main application entry point."""
    # Set up logging
    setup_logging()
    logger = logging.getLogger(__name__)
    
    # Set page configuration
    st.set_page_config(
        page_title=APP_TITLE,
        page_icon="🎯",
        layout="wide"
    )
    
    # Initialize session state
    if "initialized" not in st.session_state:
        logger.info("Initializing application")
        st.session_state["initialized"] = True
        
        # Initialize recommendation engine
        engine = RecommendationEngine()
        try:
            engine.initialize()
            st.session_state["engine"] = engine
            logger.info("Recommendation engine initialized")
        except Exception as e:
            logger.error(f"Failed to initialize recommendation engine: {str(e)}")
            st.error(f"Error initializing recommendation engine: {str(e)}")
            return
        
        # Initialize observer
        observer = UserActivityObserver()
        st.session_state["activity_observer"] = observer
        logger.info("Activity observer initialized")
    
    # Get recommendation engine from session state
    engine = st.session_state.get("engine")
    
    # Get current user if logged in
    current_user = None
    if "user_id" in st.session_state:
        user_id = st.session_state["user_id"]
        current_user = UserModel.find_by_id(user_id)
        
        # If user not found, clear session state
        if not current_user:
            st.session_state.pop("user_id", None)
            st.session_state.pop("page", None)
    
    # Navigation
    selected_page = show_sidebar_navigation(current_user)
    
    # Override selected page if in session state
    if "page" in st.session_state:
        selected_page = st.session_state["page"]
        st.session_state.pop("page", None)
    
    # Display selected page
    try:
        if selected_page == "Home":
            show_home_page()
        elif selected_page == "Login":
            show_login_page()
        elif selected_page == "Register":
            show_register_page()
        elif selected_page == "Profile" and current_user:
            show_profile_page(current_user)
        elif selected_page == "Recommendations" and current_user:
            show_recommendations_page(current_user, engine)
        elif selected_page == "Browse Items" and current_user:
            show_browse_items_page(current_user)
        elif selected_page == "My Ratings" and current_user:
            show_my_ratings_page(current_user)
        elif selected_page == "Admin" and current_user:
            show_admin_page()
        elif selected_page == "ItemDetail" and current_user and "selected_item_id" in st.session_state:
            show_item_detail_page(
                st.session_state["selected_item_id"], 
                current_user, 
                engine
            )
        else:
            # Default to home page
            show_home_page()
    except Exception as e:
        logger.error(f"Error displaying page {selected_page}: {str(e)}")
        st.error(f"An error occurred: {str(e)}")
        
        # Show exception details in development mode
        if os.getenv("ENVIRONMENT") == "development":
            st.exception(e)


if __name__ == "__main__":
    main()
