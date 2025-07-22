-- Setup Database Tables for Smart Recommendation Engine

-- Users Table
CREATE TABLE IF NOT EXISTS public.users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(50) NOT NULL UNIQUE,
    email VARCHAR(255) NOT NULL UNIQUE,
    password_hash TEXT NOT NULL,
    first_name VARCHAR(100),
    last_name VARCHAR(100),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    last_login TIMESTAMP WITH TIME ZONE,
    preferences JSONB DEFAULT '{}'::jsonb,
    is_active BOOLEAN DEFAULT TRUE
);

-- Items Table
CREATE TABLE IF NOT EXISTS public.items (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    category VARCHAR(100) NOT NULL,
    features JSONB DEFAULT '{}'::jsonb,
    metadata JSONB DEFAULT '{}'::jsonb,
    popularity_score REAL DEFAULT 0.0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    is_active BOOLEAN DEFAULT TRUE
);

-- Ratings Table
CREATE TABLE IF NOT EXISTS public.ratings (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES public.users(id) ON DELETE CASCADE,
    item_id INTEGER NOT NULL REFERENCES public.items(id) ON DELETE CASCADE,
    value INTEGER NOT NULL CHECK (value >= 1 AND value <= 5),
    context JSONB DEFAULT '{}'::jsonb,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(user_id, item_id)
);

-- Add sample data for testing

-- Sample Users
INSERT INTO public.users (username, email, password_hash, first_name, last_name, preferences)
VALUES 
('admin', 'admin@example.com', 'pbkdf2_sha256$100000$saltysalt$hashedpassword123', 'Admin', 'User', '{"is_admin": true}'::jsonb),
('user1', 'user1@example.com', 'pbkdf2_sha256$100000$saltysalt$hashedpassword123', 'John', 'Doe', '{}'::jsonb),
('user2', 'user2@example.com', 'pbkdf2_sha256$100000$saltysalt$hashedpassword123', 'Jane', 'Smith', '{}'::jsonb)
ON CONFLICT (username) DO NOTHING;

-- Sample Items (Books)
INSERT INTO public.items (name, description, category, features, popularity)
VALUES 
('The Great Gatsby', 'Classic novel by F. Scott Fitzgerald', 'Books', '{"genre": "Classic", "pages": 180, "author": "F. Scott Fitzgerald", "year": 1925}'::jsonb, 4.2),
('To Kill a Mockingbird', 'Novel by Harper Lee', 'Books', '{"genre": "Fiction", "pages": 281, "author": "Harper Lee", "year": 1960}'::jsonb, 4.5),
('1984', 'Dystopian novel by George Orwell', 'Books', '{"genre": "Dystopian", "pages": 328, "author": "George Orwell", "year": 1949}'::jsonb, 4.3),
('Pride and Prejudice', 'Novel by Jane Austen', 'Books', '{"genre": "Romance", "pages": 432, "author": "Jane Austen", "year": 1813}'::jsonb, 4.0),
('The Hobbit', 'Fantasy novel by J.R.R. Tolkien', 'Books', '{"genre": "Fantasy", "pages": 310, "author": "J.R.R. Tolkien", "year": 1937}'::jsonb, 4.7)
ON CONFLICT DO NOTHING;

-- Sample Items (Movies)
INSERT INTO public.items (name, description, category, features, popularity)
VALUES 
('The Shawshank Redemption', 'Drama film directed by Frank Darabont', 'Movies', '{"genre": "Drama", "duration": 142, "director": "Frank Darabont", "year": 1994}'::jsonb, 4.9),
('The Godfather', 'Crime film directed by Francis Ford Coppola', 'Movies', '{"genre": "Crime", "duration": 175, "director": "Francis Ford Coppola", "year": 1972}'::jsonb, 4.8),
('Pulp Fiction', 'Crime film directed by Quentin Tarantino', 'Movies', '{"genre": "Crime", "duration": 154, "director": "Quentin Tarantino", "year": 1994}'::jsonb, 4.6),
('The Dark Knight', 'Superhero film directed by Christopher Nolan', 'Movies', '{"genre": "Action", "duration": 152, "director": "Christopher Nolan", "year": 2008}'::jsonb, 4.7),
('Inception', 'Sci-fi film directed by Christopher Nolan', 'Movies', '{"genre": "Sci-Fi", "duration": 148, "director": "Christopher Nolan", "year": 2010}'::jsonb, 4.5)
ON CONFLICT DO NOTHING;

-- Sample Items (Music)
INSERT INTO public.items (name, description, category, features, popularity)
VALUES 
('Abbey Road', 'Album by The Beatles', 'Music', '{"genre": "Rock", "artist": "The Beatles", "year": 1969, "tracks": 17}'::jsonb, 4.8),
('Thriller', 'Album by Michael Jackson', 'Music', '{"genre": "Pop", "artist": "Michael Jackson", "year": 1982, "tracks": 9}'::jsonb, 4.9),
('Back in Black', 'Album by AC/DC', 'Music', '{"genre": "Rock", "artist": "AC/DC", "year": 1980, "tracks": 10}'::jsonb, 4.5),
('The Dark Side of the Moon', 'Album by Pink Floyd', 'Music', '{"genre": "Progressive Rock", "artist": "Pink Floyd", "year": 1973, "tracks": 10}'::jsonb, 4.7),
('Kind of Blue', 'Album by Miles Davis', 'Music', '{"genre": "Jazz", "artist": "Miles Davis", "year": 1959, "tracks": 5}'::jsonb, 4.6)
ON CONFLICT DO NOTHING;

-- Sample Ratings
INSERT INTO public.ratings (user_id, item_id, value)
VALUES
(1, 1, 5),
(1, 2, 4),
(1, 3, 5),
(1, 6, 5),
(1, 7, 4),
(1, 11, 5),
(1, 12, 5),
(2, 1, 3),
(2, 4, 5),
(2, 5, 4),
(2, 8, 5),
(2, 9, 3),
(2, 13, 4),
(2, 14, 5),
(3, 2, 4),
(3, 3, 3),
(3, 5, 5),
(3, 7, 5),
(3, 10, 4),
(3, 14, 3),
(3, 15, 5)
ON CONFLICT DO NOTHING;

-- Create indexes for better performance
CREATE INDEX IF NOT EXISTS idx_ratings_user_id ON public.ratings(user_id);
CREATE INDEX IF NOT EXISTS idx_ratings_item_id ON public.ratings(item_id);
CREATE INDEX IF NOT EXISTS idx_items_category ON public.items(category);
CREATE INDEX IF NOT EXISTS idx_users_email ON public.users(email);
CREATE INDEX IF NOT EXISTS idx_users_username ON public.users(username);
