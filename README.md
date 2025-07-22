# Smart Recommendation Engine

A sophisticated, object-oriented recommendation system built in Python with multiple recommendation strategies, database integration, and a streamlined user interface.

## Main UI
<img width="2307" height="1567" alt="image" src="https://github.com/user-attachments/assets/8f001c65-58e2-4c40-99b5-4d95ebd2c86b" />

### Register page
<img width="3092" height="1531" alt="image" src="https://github.com/user-attachments/assets/9098f035-d720-42c9-9c23-94d5c7bde835" />

### Login page
<img width="3109" height="1249" alt="image" src="https://github.com/user-attachments/assets/d940681f-9dbf-46d3-b70f-dc03c5ca065f" />

### Home page: Provide general information
<img width="1872" height="1119" alt="image" src="https://github.com/user-attachments/assets/535ff20b-9b9a-4246-aef0-dbfa946d1f61" />

### Recommendations page: To provide recommended items/products based on user ratings
<img width="3139" height="1639" alt="image" src="https://github.com/user-attachments/assets/aaab59b7-7565-47e0-9567-11fec6865ac2" />

User can choose categories and recommedation strategy
<img width="3158" height="1191" alt="image" src="https://github.com/user-attachments/assets/5a3af0f7-8296-416b-8096-89872a94306e" />

### Browse items page
Items can be selected by categories
<img width="1872" height="1119" alt="image" src="https://github.com/user-attachments/assets/60a35591-5afc-4901-b66f-d482a7e87447" />

User can select item and provide rating for this item by clicking on Submit Rating 
<img width="2736" height="1581" alt="image" src="https://github.com/user-attachments/assets/399765ec-d711-41b4-a772-762cab9ba645" />

### My Rating page
<img width="2828" height="1314" alt="image" src="https://github.com/user-attachments/assets/da52a4dd-f117-4c7e-86ab-28159b22dc5a" />

### Profile page
<img width="3099" height="1636" alt="image" src="https://github.com/user-attachments/assets/251a358e-827b-4aa0-80fa-995aa1df7046" />

<img width="3128" height="1482" alt="image" src="https://github.com/user-attachments/assets/3c67498b-9c80-47ba-acf0-17d5ffb06aa3" />

## Project Overview

This Smart Recommendation Engine is designed to provide personalized recommendations using multiple algorithms and strategies. The system is built with extensibility, maintainability, and scalability in mind, following SOLID principles and leveraging multiple design patterns.

### Key Features

- Multiple recommendation strategies (Collaborative Filtering, Content-Based, Hybrid)
- User interface for browsing items and viewing recommendations
- User account management and preference tracking
- User profile image upload and management
- Rating system and personalized explanations
- Admin dashboard for system management
- Comprehensive logging and error handling
- Database integration with Supabase
- Advanced features including diversity optimization and similarity search
- Robust unit testing with unittest framework

## Architecture

The application follows an object-oriented architecture with several key design patterns:

- **Strategy Pattern**: Different recommendation algorithms implemented as strategies
- **Factory Pattern**: Dynamic creation of recommendation strategies
- **Observer Pattern**: Monitoring user interactions and system events
- **Singleton Pattern**: Database connection management
- **Active Record Pattern**: Data models with built-in persistence operations
- **Template Method Pattern**: Standardized recommendation workflows

### Directory Structure

```
RCM_Demo/
├── app.py                    # Main application entry point
├── models/                   # Data models and database schema
│   ├── __init__.py
│   ├── base_model.py         # Base model with Active Record pattern
│   ├── user_model.py         # User entity model
│   ├── item_model.py         # Item entity model
│   └── rating_model.py       # Rating entity model
├── strategies/               # Recommendation algorithms
│   ├── __init__.py
│   ├── recommendation_strategy.py    # Strategy interface
│   ├── collaborative_filtering.py    # User-based collaborative filtering
│   ├── content_based_filtering.py    # Content-based recommendations
│   └── hybrid_filtering.py           # Combined strategy approach
├── ui/                       # User interface components
│   ├── __init__.py
│   ├── components.py         # Reusable UI elements
│   └── pages.py              # Page layouts and handlers
├── utils/                    # Utility modules
│   ├── __init__.py
│   ├── auth.py               # Authentication utilities
│   ├── config.py             # Application configuration
│   ├── db_manager.py         # Database connection (Singleton)
│   ├── observer.py           # Observer pattern implementation
│   ├── recommendation_engine.py      # Core orchestration engine
│   └── recommendation_factory.py     # Factory for strategies
├── tests/                    # Unit and integration tests
├── requirements.txt          # Project dependencies
└── .env.example              # Environment variables template
```

## Technology Stack

- **Python 3.11**: Core programming language
- **Streamlit**: User interface framework
- **Supabase**: Database and authentication
- **NumPy/SciPy/Pandas**: Data processing and algorithm implementation
- **Pydantic**: Data validation and settings management
- **Python Logging**: Comprehensive logging system
- **unittest**: Testing framework

## Setup Instructions

1. **Clone the repository**

```bash
git clone <repository-url>
cd RCM_Demo
```

2. **Create a virtual environment**

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies**

```bash
pip install -r requirements.txt
```

4. **Set up environment variables**

Create a `.env` file based on `.env.example`:

```bash
cp .env.example .env
```

Edit the `.env` file and fill in your Supabase credentials and other configuration options:

```
SUPABASE_URL=your_supabase_url
SUPABASE_KEY=your_supabase_key
LOG_LEVEL=INFO
LOG_FILE=recommendation_engine.log
ENVIRONMENT=development
```

5. **Database setup**

Create the following tables in your Supabase project:

- `users`: User information and authentication
- `items`: Catalog of items that can be recommended
- `ratings`: User ratings for items

The exact schema should match the fields defined in the corresponding model classes.

6. **Run the application**

```bash
streamlit run app.py
```

## Usage Guide

### User Features

1. **Register/Login**: Create an account or log in to access personalized features
2. **View Recommendations**: Get personalized item recommendations based on your preferences
3. **Browse Items**: Browse the catalog of available items
4. **Rate Items**: Provide ratings for items to improve recommendations
5. **View & Edit Profile**: Manage your profile information, preferences, and upload profile image
6. **Profile Image Management**: Upload JPG/PNG images as your profile picture (stored as base64 encoded data)

### Admin Features

1. **User Management**: View and manage user accounts
2. **Item Management**: Add, edit, or remove items from the catalog
3. **System Statistics**: View usage statistics and system performance metrics

## Development Guide

### Adding a New Recommendation Strategy

1. Create a new class in the `strategies` directory that extends `BaseRecommendationStrategy`
2. Implement the required methods: `train()`, `recommend()`, `explain()`, and `get_similarity()`
3. Register the new strategy with the `RecommendationFactory`

### Extending Data Models

1. Create a new class in the `models` directory that extends `BaseModel`
2. Define the fields and validation logic
3. Implement any model-specific methods

### Adding UI Components

1. Add new UI component functions in `ui/components.py`
2. Create new page handlers in `ui/pages.py`
3. Update the navigation and page routing in `app.py`

## Testing

The application uses Python's unittest framework for comprehensive testing of all components following object-oriented design principles. Tests are organized by component with proper mocking of dependencies.

### Running All Tests

To run the complete test suite:

```bash
python -m unittest discover tests
```

### Running Specific Test Categories

To run tests for a specific component:

```bash
python -m unittest tests.test_models  # Run all model tests
python -m unittest tests.test_authentication_manager  # Run auth tests
python -m unittest tests.test_recommendation_engine  # Run engine tests
```

### Running Individual Test Files

To run a specific test file:

```bash
python -m unittest tests/test_user_model.py
```

### Test Coverage

The test suite aims for 100% coverage of all business logic with proper testing of:

- Model validation and business rules
- Authentication and security features
- Recommendation algorithms and strategies
- UI component functionality
- Database interactions with proper mocking

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a new Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.
