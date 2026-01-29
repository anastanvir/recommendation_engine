-- Create extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_trgm";

-- Create users table
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(100) UNIQUE NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    interests JSONB DEFAULT '[]'::jsonb,
    location JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Create businesses table
CREATE TABLE businesses (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    categories JSONB DEFAULT '[]'::jsonb,
    tags JSONB DEFAULT '[]'::jsonb,
    location JSONB,
    popularity_score FLOAT DEFAULT 0.0,
    rating FLOAT DEFAULT 0.0,
    rating_count INTEGER DEFAULT 0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Create user_interactions table
CREATE TABLE user_interactions (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    business_id INTEGER REFERENCES businesses(id) ON DELETE CASCADE,
    interaction_type VARCHAR(50) NOT NULL CHECK (interaction_type IN ('view', 'like', 'save', 'purchase', 'share')),
    weight FLOAT DEFAULT 1.0,
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    metadata JSONB DEFAULT '{}'::jsonb,
    UNIQUE(user_id, business_id, interaction_type)
);

-- Create indexes for performance
CREATE INDEX idx_users_created ON users(created_at);
CREATE INDEX idx_businesses_popularity ON businesses(popularity_score DESC);
CREATE INDEX idx_businesses_categories ON businesses USING GIN(categories);
CREATE INDEX idx_businesses_tags ON businesses USING GIN(tags);
CREATE INDEX idx_interactions_user_time ON user_interactions(user_id, timestamp DESC);
CREATE INDEX idx_interactions_user_business ON user_interactions(user_id, business_id);
CREATE INDEX idx_interactions_type ON user_interactions(interaction_type);

-- Create function to update timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Create triggers for updated_at
CREATE TRIGGER update_users_updated_at BEFORE UPDATE ON users
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_businesses_updated_at BEFORE UPDATE ON businesses
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Insert sample data for testing
INSERT INTO users (username, email, interests, location) VALUES
('john_doe', 'john@example.com', '["restaurants", "coffee", "shopping"]', '{"lat": 40.7128, "lon": -74.0060}'),
('jane_smith', 'jane@example.com', '["fashion", "beauty", "fitness"]', '{"lat": 34.0522, "lon": -118.2437}'),
('bob_wilson', 'bob@example.com', '["tech", "books", "music"]', '{"lat": 51.5074, "lon": -0.1278}');

INSERT INTO businesses (name, description, categories, tags, location, popularity_score, rating) VALUES
('Coffee Corner', 'Artisanal coffee shop with organic pastries', '["cafe", "coffee"]', '["organic", "artisanal", "wifi"]', '{"lat": 40.7125, "lon": -74.0062}', 8.5, 4.7),
('Tech Gadgets', 'Latest tech gadgets and accessories', '["electronics", "tech"]', '["gadgets", "accessories", "trending"]', '{"lat": 40.7130, "lon": -74.0058}', 9.2, 4.5),
('Fashion Hub', 'Trendy clothing and accessories', '["fashion", "clothing"]', '["trendy", "affordable", "stylish"]', '{"lat": 40.7140, "lon": -74.0065}', 7.8, 4.3),
('Book Nook', 'Independent bookstore with reading space', '["books", "cafe"]', '["cozy", "reading", "quiet"]', '{"lat": 40.7135, "lon": -74.0070}', 6.9, 4.6),
('Fitness Plus', '24/7 gym with personal training', '["fitness", "gym"]', '["24/7", "training", "health"]', '{"lat": 40.7120, "lon": -74.0055}', 8.1, 4.4);