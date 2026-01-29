-- HTI Super App - Sample Seed Data
-- Social Marketplace Platform (Facebook + Reddit + Twitter + Marketplace + Events + Services)
-- Quick seed for testing - use hti_social_marketplace_generator.py for full 6-month data

-- Clear existing data
TRUNCATE TABLE user_interactions CASCADE;
TRUNCATE TABLE users CASCADE;
TRUNCATE TABLE businesses CASCADE;

-- =============================================
-- BUSINESSES / SHOPS / SERVICES / CREATORS
-- =============================================

-- MARKETPLACE - Retail Shops
INSERT INTO businesses (name, description, categories, tags, location, popularity_score, rating, rating_count) VALUES
('Urban Fashion Boutique', 'Trendy clothing and accessories for the modern shopper', '["retail_shop", "fashion_boutique", "marketplace"]', '["clothing", "fashion", "trendy", "style", "verified", "local_favorite"]', '{"lat": 40.7580, "lon": -73.9855, "area": "downtown"}', 8.5, 4.6, 1250),
('TechZone Electronics', 'Latest gadgets, phones, and tech accessories', '["retail_shop", "electronics_store", "marketplace"]', '["tech", "gadgets", "phones", "gaming", "trending", "verified"]', '{"lat": 40.7549, "lon": -73.9840, "area": "midtown"}', 9.2, 4.7, 2100),
('Home Harmony Decor', 'Beautiful furniture and home decor items', '["retail_shop", "home_decor", "marketplace"]', '["furniture", "decor", "interior", "home", "featured"]', '{"lat": 40.6782, "lon": -73.9442, "area": "brooklyn"}', 7.8, 4.4, 890),
('Glow Beauty Shop', 'Premium cosmetics and skincare products', '["retail_shop", "beauty_cosmetics", "marketplace"]', '["makeup", "skincare", "beauty", "self_care", "popular"]', '{"lat": 40.7831, "lon": -73.9712, "area": "uptown"}', 8.1, 4.5, 1560),
('Active Gear Sports', 'Sports equipment and outdoor adventure gear', '["retail_shop", "sports_outdoor", "marketplace"]', '["fitness", "sports", "outdoor", "gear", "active", "verified"]', '{"lat": 40.7282, "lon": -73.7949, "area": "queens"}', 7.5, 4.3, 720);

-- FOOD & BEVERAGE
INSERT INTO businesses (name, description, categories, tags, location, popularity_score, rating, rating_count) VALUES
('The Corner Kitchen', 'Farm-to-table dining with seasonal menus', '["food_beverage", "restaurant", "marketplace"]', '["dining", "food", "cuisine", "local_favorite", "organic"]', '{"lat": 40.7590, "lon": -73.9850, "area": "downtown"}', 8.9, 4.8, 2350),
('Urban Coffee House', 'Artisan coffee and cozy workspace vibes', '["food_beverage", "cafe_coffee", "marketplace"]', '["coffee", "cafe", "wifi", "hangout", "trending"]', '{"lat": 40.7555, "lon": -73.9835, "area": "midtown"}', 8.7, 4.6, 1890),
('Quick Bites Express', 'Fast, fresh, and delicious takeaway meals', '["food_beverage", "fast_food", "marketplace"]', '["quick_bites", "takeaway", "delivery", "casual", "popular"]', '{"lat": 40.6790, "lon": -73.9450, "area": "brooklyn"}', 7.2, 4.1, 3200),
('Skyline Bar & Lounge', 'Craft cocktails with stunning city views', '["food_beverage", "bar_nightlife", "marketplace"]', '["drinks", "nightlife", "social", "cocktails", "rooftop"]', '{"lat": 40.7600, "lon": -73.9860, "area": "downtown"}', 8.4, 4.5, 1650),
('Sweet Delights Bakery', 'Fresh-baked pastries and artisan breads', '["food_beverage", "bakery", "marketplace"]', '["bread", "pastries", "desserts", "fresh", "artisan"]', '{"lat": 40.7840, "lon": -73.9720, "area": "uptown"}', 7.9, 4.7, 980),
('FastFeast Delivery', 'Your favorite meals delivered in 30 minutes', '["food_beverage", "food_delivery", "marketplace"]', '["delivery", "online_order", "convenience", "meals", "fast"]', '{"lat": 40.7128, "lon": -74.0060, "area": "downtown"}', 8.0, 4.2, 4500);

-- PROFESSIONAL SERVICES
INSERT INTO businesses (name, description, categories, tags, location, popularity_score, rating, rating_count) VALUES
('ProFreelance Hub', 'Connect with skilled freelancers for any project', '["professional_services", "freelancer", "services"]', '["gig", "freelance", "remote", "skilled", "hire", "verified"]', '{"lat": 40.7560, "lon": -73.9845, "area": "midtown"}', 8.3, 4.4, 890),
('Elite Business Consulting', 'Strategic consulting for growing businesses', '["professional_services", "consultant", "services"]', '["business", "strategy", "expert", "advice", "professional"]', '{"lat": 40.7570, "lon": -73.9850, "area": "midtown"}', 7.8, 4.6, 320),
('LegalEase Services', 'Affordable legal help for individuals and small businesses', '["professional_services", "legal_services", "services"]', '["lawyer", "legal", "contracts", "advice", "trusted"]', '{"lat": 40.7585, "lon": -73.9860, "area": "downtown"}', 7.5, 4.5, 450),
('MoneyWise Financial', 'Personal and business financial planning', '["professional_services", "financial_services", "services"]', '["accounting", "tax", "finance", "investment", "planning"]', '{"lat": 40.7590, "lon": -73.9855, "area": "downtown"}', 7.9, 4.4, 560),
('Digital Spark Marketing', 'Full-service digital marketing and branding', '["professional_services", "marketing_agency", "services"]', '["digital", "marketing", "branding", "social_media", "growth"]', '{"lat": 40.6785, "lon": -73.9445, "area": "brooklyn"}', 8.1, 4.5, 670);

-- HOME SERVICES
INSERT INTO businesses (name, description, categories, tags, location, popularity_score, rating, rating_count) VALUES
('Sparkle Clean Services', 'Professional home and office cleaning', '["home_services", "cleaning", "services"]', '["house_cleaning", "maid", "tidy", "home_care", "reliable"]', '{"lat": 40.7835, "lon": -73.9715, "area": "uptown"}', 7.6, 4.3, 1230),
('FixIt Pro Repairs', 'Handyman services for all your home needs', '["home_services", "repair_maintenance", "services"]', '["handyman", "plumber", "electrician", "fix", "trusted"]', '{"lat": 40.7290, "lon": -73.7955, "area": "queens"}', 8.2, 4.6, 890),
('Swift Movers', 'Stress-free moving and relocation services', '["home_services", "moving", "services"]', '["movers", "relocation", "packing", "transport", "careful"]', '{"lat": 40.7130, "lon": -74.0070, "area": "downtown"}', 7.4, 4.2, 560),
('Green Thumb Landscaping', 'Beautiful gardens and lawn care', '["home_services", "landscaping", "services"]', '["garden", "lawn", "outdoor", "plants", "professional"]', '{"lat": 40.7140, "lon": -74.0810, "area": "suburbs"}', 7.8, 4.5, 340);

-- PERSONAL SERVICES
INSERT INTO businesses (name, description, categories, tags, location, popularity_score, rating, rating_count) VALUES
('Luxe Salon & Spa', 'Premium hair, nails, and spa treatments', '["personal_services", "salon_spa", "services"]', '["hair", "nails", "spa", "beauty", "grooming", "luxury"]', '{"lat": 40.7595, "lon": -73.9858, "area": "downtown"}', 8.6, 4.7, 1780),
('Peak Performance Training', 'Personal training for all fitness levels', '["personal_services", "fitness_trainer", "services"]', '["personal_training", "workout", "fitness", "health", "certified"]', '{"lat": 40.7552, "lon": -73.9842, "area": "midtown"}', 8.4, 4.8, 920),
('SmartStart Tutoring', 'Expert tutoring for students of all ages', '["personal_services", "tutoring", "services"]', '["education", "learning", "lessons", "teaching", "results"]', '{"lat": 40.7838, "lon": -73.9718, "area": "uptown"}', 7.7, 4.6, 450),
('Pawfect Pet Care', 'Loving care for your furry family members', '["personal_services", "pet_services", "services"]', '["pet_sitting", "grooming", "walking", "vet", "trusted"]', '{"lat": 40.6788, "lon": -73.9448, "area": "brooklyn"}', 8.0, 4.7, 670),
('Capture Moments Photography', 'Professional photography for all occasions', '["personal_services", "photography", "services"]', '["photographer", "photos", "events", "portraits", "creative"]', '{"lat": 40.7285, "lon": -73.7952, "area": "queens"}', 7.9, 4.5, 380);

-- EVENTS
INSERT INTO businesses (name, description, categories, tags, location, popularity_score, rating, rating_count) VALUES
('City Sounds Live', 'Live music events featuring local and touring artists', '["events", "concert_music", "events"]', '["live_music", "concert", "performance", "artist", "tickets"]', '{"lat": 40.7610, "lon": -73.9865, "area": "downtown"}', 9.0, 4.8, 3400),
('SkillUp Workshops', 'Hands-on workshops to learn new skills', '["events", "workshop_class", "events"]', '["learning", "skill", "hands_on", "education", "weekend"]', '{"lat": 40.7565, "lon": -73.9848, "area": "midtown"}', 8.2, 4.6, 890),
('Connect Networking Events', 'Professional networking for career growth', '["events", "networking", "events"]', '["business", "meetup", "professional", "connect", "career"]', '{"lat": 40.7575, "lon": -73.9852, "area": "midtown"}', 7.8, 4.4, 560),
('Metro Sports Events', 'Local sports games and tournaments', '["events", "sports_event", "events"]', '["game", "match", "competition", "sports", "local"]', '{"lat": 40.7295, "lon": -73.7958, "area": "queens"}', 8.5, 4.5, 2100),
('CultureFest', 'Celebrating diversity through food, music, and art', '["events", "festival", "events"]', '["celebration", "cultural", "community", "fun", "annual"]', '{"lat": 40.6795, "lon": -73.9455, "area": "brooklyn"}', 9.1, 4.9, 4500),
('Virtual Summit Series', 'Online conferences and webinars', '["events", "virtual_event", "events"]', '["online", "webinar", "stream", "remote", "global"]', '{"lat": 40.7580, "lon": -73.9855, "area": "downtown"}', 7.5, 4.3, 1200),
('Neighborhood Social Club', 'Local community gatherings and meetups', '["events", "community_meetup", "events"]', '["local", "gathering", "social", "neighborhood", "weekly"]', '{"lat": 40.7145, "lon": -74.0815, "area": "suburbs"}', 7.2, 4.4, 340);

-- ENTERTAINMENT
INSERT INTO businesses (name, description, categories, tags, location, popularity_score, rating, rating_count) VALUES
('Metro Cinema', 'Premium movie experience with latest releases', '["entertainment", "movie_theater", "entertainment"]', '["movies", "cinema", "films", "entertainment", "imax"]', '{"lat": 40.7605, "lon": -73.9862, "area": "downtown"}', 8.3, 4.5, 2800),
('GameZone Arcade', 'Retro and modern gaming entertainment', '["entertainment", "arcade_gaming", "entertainment"]', '["games", "arcade", "fun", "gaming", "family"]', '{"lat": 40.6792, "lon": -73.9452, "area": "brooklyn"}', 8.0, 4.4, 1450),
('Escape Quest', 'Immersive escape room adventures', '["entertainment", "escape_room", "entertainment"]', '["puzzle", "adventure", "team", "experience", "exciting"]', '{"lat": 40.7558, "lon": -73.9845, "area": "midtown"}', 8.7, 4.7, 980),
('Strike Zone Bowling', 'Modern bowling alley with food and drinks', '["entertainment", "bowling_recreation", "entertainment"]', '["bowling", "recreation", "fun", "group", "nightlife"]', '{"lat": 40.7288, "lon": -73.7955, "area": "queens"}', 7.6, 4.3, 1120),
('City Art Museum', 'World-class art exhibitions and cultural events', '["entertainment", "museum_gallery", "entertainment"]', '["art", "culture", "history", "exhibition", "educational"]', '{"lat": 40.7842, "lon": -73.9722, "area": "uptown"}', 8.8, 4.8, 3200);

-- CONTENT CREATORS / INFLUENCERS
INSERT INTO businesses (name, description, categories, tags, location, popularity_score, rating, rating_count) VALUES
('@alexlifestyle', 'Sharing daily life tips and inspiration', '["content_creator", "lifestyle_blogger", "creator"]', '["lifestyle", "blog", "daily", "tips", "vlogs", "verified"]', '{"lat": 40.7588, "lon": -73.9858, "area": "downtown"}', 9.2, 4.8, 45000),
('@foodie_sam', 'Discovering the best eats in the city', '["content_creator", "food_influencer", "creator"]', '["foodie", "recipes", "reviews", "cooking", "trending"]', '{"lat": 40.6798, "lon": -73.9458, "area": "brooklyn"}', 8.9, 4.7, 32000),
('@techreview_mike', 'Honest tech reviews and unboxings', '["content_creator", "tech_reviewer", "creator"]', '["tech", "reviews", "gadgets", "unboxing", "popular"]', '{"lat": 40.7562, "lon": -73.9848, "area": "midtown"}', 8.7, 4.6, 28000),
('@fitjenna', 'Your daily dose of fitness motivation', '["content_creator", "fitness_influencer", "creator"]', '["fitness", "workout", "health", "motivation", "verified"]', '{"lat": 40.7835, "lon": -73.9718, "area": "uptown"}', 9.0, 4.8, 52000),
('@styledbyjordan', 'Fashion inspiration for every occasion', '["content_creator", "fashion_influencer", "creator"]', '["fashion", "style", "outfit", "trends", "featured"]', '{"lat": 40.7592, "lon": -73.9855, "area": "downtown"}', 8.8, 4.7, 38000),
('@wanderlust_chris', 'Exploring hidden gems around the world', '["content_creator", "travel_creator", "creator"]', '["travel", "adventure", "explore", "destinations", "popular"]', '{"lat": 40.7585, "lon": -73.9852, "area": "downtown"}', 8.5, 4.6, 41000),
('@laughwithlisa', 'Making your day brighter with comedy', '["content_creator", "comedy_entertainment", "creator"]', '["funny", "comedy", "memes", "entertainment", "viral"]', '{"lat": 40.6795, "lon": -73.9455, "area": "brooklyn"}', 9.1, 4.9, 67000);

-- COMMUNITY GROUPS
INSERT INTO businesses (name, description, categories, tags, location, popularity_score, rating, rating_count) VALUES
('Photography Enthusiasts Club', 'Share your photos and learn from others', '["community_group", "hobby_interest", "community"]', '["hobby", "photography", "enthusiast", "community", "creative"]', '{"lat": 40.7580, "lon": -73.9855, "area": "downtown"}', 7.8, 4.5, 2300),
('Downtown Neighbors Network', 'Connecting our local community', '["community_group", "local_neighborhood", "community"]', '["local", "neighbors", "area", "community", "helpful"]', '{"lat": 40.7590, "lon": -73.9860, "area": "downtown"}', 7.5, 4.4, 1800),
('Tech Professionals Network', 'Career growth and industry insights', '["community_group", "professional_network", "community"]', '["career", "industry", "networking", "jobs", "tech"]', '{"lat": 40.7568, "lon": -73.9850, "area": "midtown"}', 8.2, 4.6, 3400),
('Metro Sports Fans', 'The ultimate home for local sports fans', '["community_group", "sports_fan", "community"]', '["sports", "team", "fan", "games", "passionate"]', '{"lat": 40.7292, "lon": -73.7958, "area": "queens"}', 8.5, 4.7, 5600),
('Parents of Brooklyn', 'Support and resources for local parents', '["community_group", "parenting", "community"]', '["parents", "kids", "family", "advice", "supportive"]', '{"lat": 40.6788, "lon": -73.9448, "area": "brooklyn"}', 7.9, 4.6, 2100),
('GamersUnite Community', 'Connect with fellow gamers', '["community_group", "gaming_community", "community"]', '["gaming", "esports", "players", "games", "competitive"]', '{"lat": 40.7555, "lon": -73.9842, "area": "midtown"}', 8.8, 4.8, 8900),
('DIY Makers Collective', 'Share projects and learn new crafts', '["community_group", "diy_makers", "community"]', '["diy", "crafts", "making", "creative", "tutorials"]', '{"lat": 40.6800, "lon": -73.9460, "area": "brooklyn"}', 7.6, 4.5, 1650);

-- LOCAL DISCOVERY
INSERT INTO businesses (name, description, categories, tags, location, popularity_score, rating, rating_count) VALUES
('City Landmark Tours', 'Discover the history and beauty of our city', '["local_discovery", "attractions", "local"]', '["tourism", "sightseeing", "landmark", "visit", "guided"]', '{"lat": 40.7600, "lon": -73.9865, "area": "downtown"}', 8.4, 4.6, 4500),
('Central Park Adventures', 'Explore the urban oasis', '["local_discovery", "parks_nature", "local"]', '["park", "nature", "outdoor", "trails", "scenic"]', '{"lat": 40.7850, "lon": -73.9680, "area": "uptown"}', 9.0, 4.9, 12000),
('Metro Grand Hotel', 'Luxury accommodations in the heart of downtown', '["local_discovery", "hotels_lodging", "local"]', '["hotel", "stay", "accommodation", "travel", "luxury"]', '{"lat": 40.7585, "lon": -73.9858, "area": "downtown"}', 8.6, 4.7, 3200),
('CityRide Transport', 'Convenient rides across the metro area', '["local_discovery", "transportation", "local"]', '["transit", "rides", "transport", "travel", "reliable"]', '{"lat": 40.7580, "lon": -73.9855, "area": "downtown"}', 7.8, 4.3, 8900);

-- HEALTH & WELLNESS
INSERT INTO businesses (name, description, categories, tags, location, popularity_score, rating, rating_count) VALUES
('Peak Fitness Gym', 'State-of-the-art equipment and expert trainers', '["health_wellness", "gym_fitness", "services"]', '["gym", "workout", "fitness", "exercise", "health", "24hour"]', '{"lat": 40.7558, "lon": -73.9845, "area": "midtown"}', 8.8, 4.7, 2800),
('Zen Yoga Studio', 'Find your inner peace through yoga and meditation', '["health_wellness", "yoga_meditation", "services"]', '["yoga", "meditation", "wellness", "mindfulness", "classes"]', '{"lat": 40.6792, "lon": -73.9452, "area": "brooklyn"}', 8.5, 4.8, 1450),
('CareFirst Medical Clinic', 'Comprehensive healthcare for the whole family', '["health_wellness", "medical_clinic", "services"]', '["doctor", "health", "medical", "clinic", "trusted"]', '{"lat": 40.7840, "lon": -73.9720, "area": "uptown"}', 8.2, 4.5, 1200),
('QuickMeds Pharmacy', 'Fast prescriptions and health consultations', '["health_wellness", "pharmacy", "services"]', '["medicine", "pharmacy", "health", "prescriptions", "delivery"]', '{"lat": 40.7290, "lon": -73.7955, "area": "queens"}', 7.8, 4.4, 890),
('MindWell Therapy Center', 'Professional mental health support', '["health_wellness", "mental_health", "services"]', '["therapy", "counseling", "mental_health", "support", "confidential"]', '{"lat": 40.7585, "lon": -73.9852, "area": "downtown"}', 8.4, 4.7, 560);

-- =============================================
-- USERS (Diverse segments)
-- =============================================

INSERT INTO users (username, email, interests, location) VALUES
-- Social Butterflies
('sarah_social', 'sarah.social@email.com', '["food_beverage", "entertainment", "events", "content_creator", "community_group", "trending", "social", "local"]', '{"lat": 40.7582, "lon": -73.9857, "area": "downtown"}'),
('mike_partytime', 'mike.party@email.com', '["food_beverage", "events", "entertainment", "bar_nightlife", "social", "nightlife"]', '{"lat": 40.7600, "lon": -73.9862, "area": "downtown"}'),
('emma_socialite', 'emma.social@email.com', '["events", "content_creator", "food_beverage", "entertainment", "trending", "fashion"]', '{"lat": 40.6785, "lon": -73.9448, "area": "brooklyn"}'),

-- Shoppers
('jessica_shops', 'jessica.shops@email.com', '["retail_shop", "food_beverage", "beauty_cosmetics", "fashion", "deals", "products"]', '{"lat": 40.7560, "lon": -73.9845, "area": "midtown"}'),
('david_deals', 'david.deals@email.com', '["retail_shop", "electronics_store", "tech", "gadgets", "reviews"]', '{"lat": 40.7555, "lon": -73.9840, "area": "midtown"}'),
('amanda_buyer', 'amanda.buyer@email.com', '["retail_shop", "home_decor", "local_discovery", "products", "quality"]', '{"lat": 40.7835, "lon": -73.9718, "area": "uptown"}'),

-- Professionals
('john_professional', 'john.pro@email.com', '["professional_services", "events", "networking", "community_group", "business", "career"]', '{"lat": 40.7575, "lon": -73.9852, "area": "midtown"}'),
('lisa_networker', 'lisa.network@email.com', '["professional_services", "events", "consultant", "networking", "industry"]', '{"lat": 40.7570, "lon": -73.9850, "area": "midtown"}'),

-- Content Consumers
('chris_viewer', 'chris.viewer@email.com', '["content_creator", "entertainment", "community_group", "videos", "memes", "trending"]', '{"lat": 40.6790, "lon": -73.9450, "area": "brooklyn"}'),
('alex_scroll', 'alex.scroll@email.com', '["content_creator", "entertainment", "food_influencer", "videos", "creators"]', '{"lat": 40.7290, "lon": -73.7955, "area": "queens"}'),

-- Local Explorers
('maya_explorer', 'maya.explorer@email.com', '["food_beverage", "entertainment", "events", "local_discovery", "local", "new", "experiences"]', '{"lat": 40.7592, "lon": -73.9858, "area": "downtown"}'),
('ryan_discover', 'ryan.discover@email.com', '["local_discovery", "food_beverage", "events", "attractions", "recommendations"]', '{"lat": 40.6798, "lon": -73.9455, "area": "brooklyn"}'),

-- Service Seekers
('tom_homeowner', 'tom.home@email.com', '["home_services", "personal_services", "professional_services", "services", "reviews", "quality"]', '{"lat": 40.7145, "lon": -74.0815, "area": "suburbs"}'),
('nancy_needs', 'nancy.needs@email.com', '["home_services", "health_wellness", "personal_services", "local", "trusted"]', '{"lat": 40.7840, "lon": -73.9722, "area": "uptown"}'),

-- Community Members
('ben_community', 'ben.community@email.com', '["community_group", "events", "local_discovery", "discussions", "local", "community"]', '{"lat": 40.7285, "lon": -73.7952, "area": "queens"}'),
('olivia_local', 'olivia.local@email.com', '["community_group", "local_neighborhood", "events", "community", "groups"]', '{"lat": 40.7150, "lon": -74.0820, "area": "suburbs"}'),

-- Fitness Enthusiasts
('jake_fitness', 'jake.fitness@email.com', '["health_wellness", "fitness", "nutrition", "personal_services", "workout", "gym"]', '{"lat": 40.7560, "lon": -73.9848, "area": "midtown"}'),
('samantha_active', 'sam.active@email.com', '["health_wellness", "fitness_trainer", "yoga_meditation", "wellness", "health"]', '{"lat": 40.6792, "lon": -73.9455, "area": "brooklyn"}'),

-- Casual Browsers
('kevin_casual', 'kevin.casual@email.com', '["food_beverage", "retail_shop", "entertainment", "popular", "trending"]', '{"lat": 40.7580, "lon": -73.9855, "area": "downtown"}'),
('anna_browse', 'anna.browse@email.com', '["food_beverage", "entertainment", "retail_shop", "easy", "popular"]', '{"lat": 40.7838, "lon": -73.9720, "area": "uptown"}');

-- =============================================
-- SAMPLE INTERACTIONS (Recent activity)
-- =============================================

-- Generate varied interactions for testing
INSERT INTO user_interactions (user_id, business_id, interaction_type, weight, timestamp) VALUES
-- Sarah (Social Butterfly) - High engagement with events and social places
(1, 6, 'view', 1.0, NOW() - INTERVAL '2 days'),
(1, 6, 'like', 2.0, NOW() - INTERVAL '2 days'),
(1, 21, 'view', 1.0, NOW() - INTERVAL '1 day'),
(1, 21, 'save', 3.0, NOW() - INTERVAL '1 day'),
(1, 25, 'view', 1.0, NOW() - INTERVAL '12 hours'),
(1, 25, 'like', 2.0, NOW() - INTERVAL '12 hours'),
(1, 31, 'view', 1.0, NOW() - INTERVAL '6 hours'),
(1, 31, 'like', 2.0, NOW() - INTERVAL '6 hours'),
(1, 31, 'share', 4.0, NOW() - INTERVAL '5 hours'),

-- Jessica (Shopper) - Purchase focused
(4, 1, 'view', 1.0, NOW() - INTERVAL '3 days'),
(4, 1, 'save', 3.0, NOW() - INTERVAL '3 days'),
(4, 1, 'purchase', 5.0, NOW() - INTERVAL '2 days'),
(4, 4, 'view', 1.0, NOW() - INTERVAL '1 day'),
(4, 4, 'like', 2.0, NOW() - INTERVAL '1 day'),
(4, 4, 'save', 3.0, NOW() - INTERVAL '12 hours'),
(4, 2, 'view', 1.0, NOW() - INTERVAL '6 hours'),

-- John (Professional) - Networking focused
(7, 13, 'view', 1.0, NOW() - INTERVAL '4 days'),
(7, 13, 'save', 3.0, NOW() - INTERVAL '4 days'),
(7, 23, 'view', 1.0, NOW() - INTERVAL '2 days'),
(7, 23, 'like', 2.0, NOW() - INTERVAL '2 days'),
(7, 23, 'purchase', 5.0, NOW() - INTERVAL '1 day'),
(7, 39, 'view', 1.0, NOW() - INTERVAL '12 hours'),
(7, 39, 'like', 2.0, NOW() - INTERVAL '12 hours'),

-- Chris (Content Consumer) - Passive viewing
(9, 31, 'view', 1.0, NOW() - INTERVAL '3 days'),
(9, 32, 'view', 1.0, NOW() - INTERVAL '2 days'),
(9, 33, 'view', 1.0, NOW() - INTERVAL '2 days'),
(9, 34, 'view', 1.0, NOW() - INTERVAL '1 day'),
(9, 34, 'like', 2.0, NOW() - INTERVAL '1 day'),
(9, 35, 'view', 1.0, NOW() - INTERVAL '12 hours'),
(9, 36, 'view', 1.0, NOW() - INTERVAL '6 hours'),
(9, 37, 'view', 1.0, NOW() - INTERVAL '3 hours'),

-- Maya (Local Explorer) - Discovery focused
(11, 45, 'view', 1.0, NOW() - INTERVAL '5 days'),
(11, 45, 'like', 2.0, NOW() - INTERVAL '5 days'),
(11, 46, 'view', 1.0, NOW() - INTERVAL '3 days'),
(11, 46, 'save', 3.0, NOW() - INTERVAL '3 days'),
(11, 6, 'view', 1.0, NOW() - INTERVAL '2 days'),
(11, 6, 'like', 2.0, NOW() - INTERVAL '2 days'),
(11, 6, 'purchase', 5.0, NOW() - INTERVAL '1 day'),
(11, 7, 'view', 1.0, NOW() - INTERVAL '12 hours'),

-- Jake (Fitness Enthusiast)
(17, 49, 'view', 1.0, NOW() - INTERVAL '7 days'),
(17, 49, 'like', 2.0, NOW() - INTERVAL '7 days'),
(17, 49, 'purchase', 5.0, NOW() - INTERVAL '6 days'),
(17, 50, 'view', 1.0, NOW() - INTERVAL '4 days'),
(17, 50, 'save', 3.0, NOW() - INTERVAL '4 days'),
(17, 19, 'view', 1.0, NOW() - INTERVAL '2 days'),
(17, 19, 'like', 2.0, NOW() - INTERVAL '2 days'),
(17, 34, 'view', 1.0, NOW() - INTERVAL '1 day'),
(17, 34, 'like', 2.0, NOW() - INTERVAL '1 day'),

-- Tom (Service Seeker)
(13, 15, 'view', 1.0, NOW() - INTERVAL '10 days'),
(13, 15, 'save', 3.0, NOW() - INTERVAL '10 days'),
(13, 16, 'view', 1.0, NOW() - INTERVAL '5 days'),
(13, 16, 'like', 2.0, NOW() - INTERVAL '5 days'),
(13, 16, 'purchase', 5.0, NOW() - INTERVAL '3 days'),
(13, 17, 'view', 1.0, NOW() - INTERVAL '1 day'),

-- Ben (Community Member)
(15, 38, 'view', 1.0, NOW() - INTERVAL '8 days'),
(15, 38, 'like', 2.0, NOW() - INTERVAL '8 days'),
(15, 40, 'view', 1.0, NOW() - INTERVAL '5 days'),
(15, 40, 'like', 2.0, NOW() - INTERVAL '5 days'),
(15, 40, 'save', 3.0, NOW() - INTERVAL '4 days'),
(15, 27, 'view', 1.0, NOW() - INTERVAL '2 days'),
(15, 27, 'like', 2.0, NOW() - INTERVAL '2 days');

-- Summary counts
SELECT 'Users' as entity, COUNT(*) as count FROM users
UNION ALL
SELECT 'Businesses', COUNT(*) FROM businesses
UNION ALL
SELECT 'Interactions', COUNT(*) FROM user_interactions;
