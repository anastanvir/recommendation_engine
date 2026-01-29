#!/usr/bin/env python3
"""
HTI Super App - Social Marketplace Data Generator

Comprehensive data generator for an all-in-one platform combining:
- Social networking (Facebook-like profiles, friends, posts)
- Microblogging (Twitter/Threads-style content)
- Communities (Reddit-style subreddits/groups)
- Events (local, virtual, ticketed)
- Business marketplace (shops, services, products)
- Professional services (gig economy)
- Local discovery

Generates 6 months of realistic user behavior data.
"""
import asyncio
import json
import random
import sys
from datetime import datetime, timedelta
from typing import List, Dict, Tuple
import math

sys.path.insert(0, '/app')

from app.database import AsyncSessionLocal
from sqlalchemy import text

# ========== CONFIGURATION ==========
NUM_BUSINESSES = 600       # Diverse businesses/shops/services
NUM_USERS = 1200           # Active users
DAYS_OF_DATA = 180         # 6 months
MIN_INTERACTIONS_PER_DAY = 1500
MAX_INTERACTIONS_PER_DAY = 6000

# ========== BUSINESS CATEGORIES FOR SUPER APP ==========
PLATFORM_CATEGORIES = {
    # === MARKETPLACE & SHOPS ===
    "retail_shop": {
        "weight": 0.12,
        "type": "marketplace",
        "subcategories": [
            {"name": "fashion_boutique", "tags": ["clothing", "accessories", "trendy", "fashion", "style"]},
            {"name": "electronics_store", "tags": ["tech", "gadgets", "phones", "computers", "gaming"]},
            {"name": "home_decor", "tags": ["furniture", "decor", "interior", "home", "living"]},
            {"name": "beauty_cosmetics", "tags": ["makeup", "skincare", "beauty", "cosmetics", "self_care"]},
            {"name": "sports_outdoor", "tags": ["fitness", "sports", "outdoor", "gear", "active"]},
            {"name": "books_media", "tags": ["books", "music", "movies", "games", "entertainment"]},
        ]
    },
    "food_beverage": {
        "weight": 0.15,
        "type": "marketplace",
        "subcategories": [
            {"name": "restaurant", "tags": ["dining", "food", "cuisine", "eat_out", "meals"]},
            {"name": "cafe_coffee", "tags": ["coffee", "cafe", "tea", "pastries", "hangout"]},
            {"name": "fast_food", "tags": ["quick_bites", "takeaway", "delivery", "casual"]},
            {"name": "bar_nightlife", "tags": ["drinks", "nightlife", "social", "cocktails", "pub"]},
            {"name": "bakery", "tags": ["bread", "pastries", "desserts", "fresh", "artisan"]},
            {"name": "food_delivery", "tags": ["delivery", "online_order", "convenience", "meals"]},
        ]
    },

    # === SERVICES ===
    "professional_services": {
        "weight": 0.10,
        "type": "services",
        "subcategories": [
            {"name": "freelancer", "tags": ["gig", "freelance", "remote", "skilled", "hire"]},
            {"name": "consultant", "tags": ["business", "strategy", "expert", "advice", "professional"]},
            {"name": "legal_services", "tags": ["lawyer", "legal", "contracts", "advice"]},
            {"name": "financial_services", "tags": ["accounting", "tax", "finance", "investment"]},
            {"name": "marketing_agency", "tags": ["digital", "marketing", "branding", "social_media"]},
        ]
    },
    "home_services": {
        "weight": 0.08,
        "type": "services",
        "subcategories": [
            {"name": "cleaning", "tags": ["house_cleaning", "maid", "tidy", "home_care"]},
            {"name": "repair_maintenance", "tags": ["handyman", "plumber", "electrician", "fix"]},
            {"name": "moving", "tags": ["movers", "relocation", "packing", "transport"]},
            {"name": "landscaping", "tags": ["garden", "lawn", "outdoor", "plants"]},
            {"name": "pest_control", "tags": ["exterminator", "bugs", "rodents", "prevention"]},
        ]
    },
    "personal_services": {
        "weight": 0.08,
        "type": "services",
        "subcategories": [
            {"name": "salon_spa", "tags": ["hair", "nails", "spa", "beauty", "grooming"]},
            {"name": "fitness_trainer", "tags": ["personal_training", "workout", "fitness", "health"]},
            {"name": "tutoring", "tags": ["education", "learning", "lessons", "teaching"]},
            {"name": "pet_services", "tags": ["pet_sitting", "grooming", "walking", "vet"]},
            {"name": "photography", "tags": ["photographer", "photos", "events", "portraits"]},
        ]
    },

    # === EVENTS ===
    "events": {
        "weight": 0.10,
        "type": "events",
        "subcategories": [
            {"name": "concert_music", "tags": ["live_music", "concert", "performance", "artist"]},
            {"name": "workshop_class", "tags": ["learning", "skill", "hands_on", "education"]},
            {"name": "networking", "tags": ["business", "meetup", "professional", "connect"]},
            {"name": "sports_event", "tags": ["game", "match", "competition", "sports"]},
            {"name": "festival", "tags": ["celebration", "cultural", "community", "fun"]},
            {"name": "virtual_event", "tags": ["online", "webinar", "stream", "remote"]},
            {"name": "community_meetup", "tags": ["local", "gathering", "social", "neighborhood"]},
        ]
    },

    # === ENTERTAINMENT ===
    "entertainment": {
        "weight": 0.08,
        "type": "entertainment",
        "subcategories": [
            {"name": "movie_theater", "tags": ["movies", "cinema", "films", "entertainment"]},
            {"name": "arcade_gaming", "tags": ["games", "arcade", "fun", "gaming"]},
            {"name": "escape_room", "tags": ["puzzle", "adventure", "team", "experience"]},
            {"name": "bowling_recreation", "tags": ["bowling", "recreation", "fun", "group"]},
            {"name": "museum_gallery", "tags": ["art", "culture", "history", "exhibition"]},
        ]
    },

    # === CONTENT CREATORS / INFLUENCERS ===
    "content_creator": {
        "weight": 0.08,
        "type": "creator",
        "subcategories": [
            {"name": "lifestyle_blogger", "tags": ["lifestyle", "blog", "daily", "tips", "vlogs"]},
            {"name": "food_influencer", "tags": ["foodie", "recipes", "reviews", "cooking"]},
            {"name": "tech_reviewer", "tags": ["tech", "reviews", "gadgets", "unboxing"]},
            {"name": "fitness_influencer", "tags": ["fitness", "workout", "health", "motivation"]},
            {"name": "fashion_influencer", "tags": ["fashion", "style", "outfit", "trends"]},
            {"name": "travel_creator", "tags": ["travel", "adventure", "explore", "destinations"]},
            {"name": "comedy_entertainment", "tags": ["funny", "comedy", "memes", "entertainment"]},
        ]
    },

    # === COMMUNITIES / GROUPS ===
    "community_group": {
        "weight": 0.08,
        "type": "community",
        "subcategories": [
            {"name": "hobby_interest", "tags": ["hobby", "interest", "enthusiast", "community"]},
            {"name": "local_neighborhood", "tags": ["local", "neighbors", "area", "community"]},
            {"name": "professional_network", "tags": ["career", "industry", "networking", "jobs"]},
            {"name": "sports_fan", "tags": ["sports", "team", "fan", "games"]},
            {"name": "parenting", "tags": ["parents", "kids", "family", "advice"]},
            {"name": "gaming_community", "tags": ["gaming", "esports", "players", "games"]},
            {"name": "diy_makers", "tags": ["diy", "crafts", "making", "creative"]},
        ]
    },

    # === LOCAL & TRAVEL ===
    "local_discovery": {
        "weight": 0.06,
        "type": "local",
        "subcategories": [
            {"name": "attractions", "tags": ["tourism", "sightseeing", "landmark", "visit"]},
            {"name": "parks_nature", "tags": ["park", "nature", "outdoor", "trails"]},
            {"name": "hotels_lodging", "tags": ["hotel", "stay", "accommodation", "travel"]},
            {"name": "transportation", "tags": ["transit", "rides", "transport", "travel"]},
        ]
    },

    # === HEALTH & WELLNESS ===
    "health_wellness": {
        "weight": 0.07,
        "type": "services",
        "subcategories": [
            {"name": "gym_fitness", "tags": ["gym", "workout", "fitness", "exercise", "health"]},
            {"name": "yoga_meditation", "tags": ["yoga", "meditation", "wellness", "mindfulness"]},
            {"name": "medical_clinic", "tags": ["doctor", "health", "medical", "clinic"]},
            {"name": "pharmacy", "tags": ["medicine", "pharmacy", "health", "prescriptions"]},
            {"name": "mental_health", "tags": ["therapy", "counseling", "mental_health", "support"]},
        ]
    },
}

# ========== USER SEGMENTS (Super App Users) ==========
USER_SEGMENTS = {
    "social_butterfly": {
        "weight": 0.18,
        "age_range": (18, 35),
        "interests": ["food_beverage", "entertainment", "events", "content_creator", "community_group"],
        "active_hours": [(7, 9), (12, 14), (18, 24)],
        "behavior": "high_engagement",
        "interaction_rate": 1.4,
        "content_preferences": ["trending", "social", "local", "events"],
    },
    "shopper": {
        "weight": 0.15,
        "age_range": (22, 55),
        "interests": ["retail_shop", "food_beverage", "local_discovery"],
        "active_hours": [(10, 14), (19, 22)],
        "behavior": "purchase_focused",
        "interaction_rate": 1.0,
        "content_preferences": ["deals", "products", "reviews", "shops"],
    },
    "professional": {
        "weight": 0.14,
        "age_range": (25, 50),
        "interests": ["professional_services", "events", "community_group"],
        "active_hours": [(7, 9), (12, 13), (17, 20)],
        "behavior": "networking",
        "interaction_rate": 0.9,
        "content_preferences": ["business", "networking", "career", "industry"],
    },
    "content_consumer": {
        "weight": 0.16,
        "age_range": (16, 45),
        "interests": ["content_creator", "entertainment", "community_group"],
        "active_hours": [(6, 8), (12, 14), (20, 24)],
        "behavior": "passive_viewer",
        "interaction_rate": 0.7,
        "content_preferences": ["videos", "memes", "trending", "creators"],
    },
    "local_explorer": {
        "weight": 0.12,
        "age_range": (20, 45),
        "interests": ["food_beverage", "entertainment", "events", "local_discovery"],
        "active_hours": [(11, 14), (17, 23)],
        "behavior": "discovery",
        "interaction_rate": 1.1,
        "content_preferences": ["local", "new", "experiences", "recommendations"],
    },
    "service_seeker": {
        "weight": 0.10,
        "age_range": (28, 60),
        "interests": ["home_services", "personal_services", "professional_services", "health_wellness"],
        "active_hours": [(8, 12), (14, 18)],
        "behavior": "task_oriented",
        "interaction_rate": 0.8,
        "content_preferences": ["services", "reviews", "local", "quality"],
    },
    "community_member": {
        "weight": 0.08,
        "age_range": (20, 55),
        "interests": ["community_group", "events", "local_discovery"],
        "active_hours": [(8, 10), (19, 23)],
        "behavior": "community_engaged",
        "interaction_rate": 1.2,
        "content_preferences": ["discussions", "local", "community", "groups"],
    },
    "casual_browser": {
        "weight": 0.07,
        "age_range": (18, 65),
        "interests": ["food_beverage", "retail_shop", "entertainment"],
        "active_hours": [(10, 22)],
        "behavior": "occasional",
        "interaction_rate": 0.5,
        "content_preferences": ["popular", "trending", "easy"],
    },
}

# ========== LOCATION CLUSTERS ==========
LOCATIONS = [
    {"name": "downtown", "lat": 40.7580, "lon": -73.9855, "density": 0.25, "vibe": "urban_busy"},
    {"name": "midtown", "lat": 40.7549, "lon": -73.9840, "density": 0.20, "vibe": "commercial"},
    {"name": "uptown", "lat": 40.7831, "lon": -73.9712, "density": 0.15, "vibe": "residential"},
    {"name": "brooklyn", "lat": 40.6782, "lon": -73.9442, "density": 0.18, "vibe": "trendy"},
    {"name": "queens", "lat": 40.7282, "lon": -73.7949, "density": 0.12, "vibe": "diverse"},
    {"name": "suburbs", "lat": 40.7128, "lon": -74.0800, "density": 0.10, "vibe": "family"},
]

# ========== TIME-BASED PATTERNS ==========
TIME_PATTERNS = {
    "morning_rush": {"hours": (7, 10), "boost_categories": ["food_beverage", "health_wellness"]},
    "lunch_break": {"hours": (11, 14), "boost_categories": ["food_beverage", "retail_shop", "content_creator"]},
    "afternoon": {"hours": (14, 17), "boost_categories": ["professional_services", "home_services"]},
    "evening_social": {"hours": (17, 21), "boost_categories": ["events", "entertainment", "food_beverage"]},
    "night_owl": {"hours": (21, 24), "boost_categories": ["content_creator", "community_group", "entertainment"]},
}

# ========== SEASONAL TRENDS ==========
SEASONAL_TRENDS = {
    "winter": {
        "months": [12, 1, 2],
        "boost": {"entertainment": 1.3, "food_beverage": 1.2, "retail_shop": 1.4, "events": 0.8},
    },
    "spring": {
        "months": [3, 4, 5],
        "boost": {"events": 1.3, "local_discovery": 1.4, "health_wellness": 1.3, "home_services": 1.2},
    },
    "summer": {
        "months": [6, 7, 8],
        "boost": {"events": 1.5, "entertainment": 1.4, "local_discovery": 1.5, "food_beverage": 1.3},
    },
    "fall": {
        "months": [9, 10, 11],
        "boost": {"retail_shop": 1.3, "events": 1.2, "professional_services": 1.2},
    },
}

# ========== BUSINESS NAME GENERATORS ==========
BUSINESS_NAME_PARTS = {
    "retail_shop": {
        "prefixes": ["Urban", "Trendy", "Classic", "Modern", "The", "Blue", "Golden", "Elite"],
        "suffixes": ["Boutique", "Store", "Shop", "Emporium", "Market", "Hub", "Corner", "Place"],
    },
    "food_beverage": {
        "prefixes": ["The", "Mama's", "Urban", "Fresh", "Golden", "Blue", "Sunset", "Corner"],
        "suffixes": ["Kitchen", "Cafe", "Bistro", "Grill", "House", "Table", "Spot", "Den"],
    },
    "professional_services": {
        "prefixes": ["Pro", "Elite", "Premier", "Expert", "Prime", "First", "Top"],
        "suffixes": ["Solutions", "Partners", "Group", "Services", "Consulting", "Agency"],
    },
    "home_services": {
        "prefixes": ["Quick", "Reliable", "Pro", "Expert", "Local", "Trusted", "Fast"],
        "suffixes": ["Services", "Solutions", "Pros", "Team", "Experts", "Help"],
    },
    "personal_services": {
        "prefixes": ["Luxe", "Pure", "Radiant", "Elite", "Glow", "Serene", "Bliss"],
        "suffixes": ["Studio", "Salon", "Spa", "Wellness", "Care", "Beauty"],
    },
    "events": {
        "prefixes": ["Epic", "Premier", "Grand", "Live", "Main", "City", "Metro"],
        "suffixes": ["Events", "Productions", "Experience", "Live", "Stage", "Festival"],
    },
    "entertainment": {
        "prefixes": ["Fun", "Play", "Epic", "Grand", "Star", "Magic", "Wonder"],
        "suffixes": ["Zone", "World", "Palace", "Center", "Arena", "Land"],
    },
    "content_creator": {
        "prefixes": ["", "", "", "The", "Real", "Just", "Its"],
        "suffixes": ["Vibes", "Life", "World", "Daily", "Show", "Channel", ""],
    },
    "community_group": {
        "prefixes": ["The", "Local", "Urban", "Metro", "City", "Our", ""],
        "suffixes": ["Community", "Hub", "Network", "Circle", "Club", "Society", "Collective"],
    },
    "local_discovery": {
        "prefixes": ["City", "Metro", "Urban", "Local", "Grand", "Historic"],
        "suffixes": ["Tours", "Adventures", "Guides", "Spots", "Discoveries"],
    },
    "health_wellness": {
        "prefixes": ["Vitality", "Peak", "Pure", "Core", "Zen", "Balance", "Life"],
        "suffixes": ["Fitness", "Wellness", "Health", "Center", "Studio", "Gym"],
    },
}

# User names
FIRST_NAMES = [
    "Emma", "Liam", "Olivia", "Noah", "Ava", "Ethan", "Sophia", "Mason", "Isabella", "William",
    "Mia", "James", "Charlotte", "Benjamin", "Amelia", "Lucas", "Harper", "Henry", "Evelyn",
    "Alexander", "Abigail", "Michael", "Emily", "Daniel", "Elizabeth", "Matthew", "Sofia",
    "David", "Avery", "Joseph", "Ella", "Samuel", "Scarlett", "Sebastian", "Grace", "Jack",
    "Victoria", "Owen", "Riley", "Theodore", "Aria", "Aiden", "Luna", "John", "Chloe",
    "Ryan", "Penelope", "Nathan", "Layla", "Caleb", "Zoe", "Marcus", "Lily", "Jordan",
    "Hannah", "Tyler", "Addison", "Brandon", "Natalie", "Justin", "Leah", "Austin", "Savannah",
    "Kevin", "Audrey", "Brian", "Brooklyn", "Jason", "Bella", "Aaron", "Claire", "Adam",
]

LAST_NAMES = [
    "Smith", "Johnson", "Williams", "Brown", "Jones", "Garcia", "Miller", "Davis", "Rodriguez",
    "Martinez", "Hernandez", "Lopez", "Gonzalez", "Wilson", "Anderson", "Thomas", "Taylor",
    "Moore", "Jackson", "Martin", "Lee", "Perez", "Thompson", "White", "Harris", "Sanchez",
    "Clark", "Ramirez", "Lewis", "Robinson", "Walker", "Young", "Allen", "King", "Wright",
    "Scott", "Torres", "Nguyen", "Hill", "Flores", "Green", "Adams", "Nelson", "Baker",
    "Hall", "Rivera", "Campbell", "Mitchell", "Carter", "Roberts", "Turner", "Phillips",
    "Evans", "Collins", "Stewart", "Morris", "Murphy", "Rivera", "Cook", "Rogers", "Morgan",
]


def weighted_choice(choices: List[Tuple]) -> any:
    """Select item based on weights"""
    total = sum(w for _, w in choices)
    r = random.uniform(0, total)
    upto = 0
    for item, weight in choices:
        if upto + weight >= r:
            return item
        upto += weight
    return choices[-1][0]


def get_season(month: int) -> str:
    """Get season from month"""
    for season, data in SEASONAL_TRENDS.items():
        if month in data["months"]:
            return season
    return "spring"


def get_time_pattern(hour: int) -> str:
    """Get time pattern for hour"""
    for pattern, data in TIME_PATTERNS.items():
        start, end = data["hours"]
        if start <= hour < end:
            return pattern
    return "afternoon"


def generate_business_name(category: str, subcategory: str) -> str:
    """Generate a realistic business name"""
    name_data = BUSINESS_NAME_PARTS.get(category, BUSINESS_NAME_PARTS["retail_shop"])

    # For content creators, use personal name style
    if category == "content_creator":
        first = random.choice(FIRST_NAMES)
        suffix = random.choice(name_data["suffixes"])
        if random.random() < 0.5:
            return f"@{first.lower()}{suffix.lower()}"
        else:
            return f"{first} {suffix}".strip()

    prefix = random.choice(name_data["prefixes"])
    suffix = random.choice(name_data["suffixes"])

    # Add subcategory flavor sometimes
    if random.random() < 0.3:
        subcat_word = subcategory.replace("_", " ").title().split()[0]
        return f"{prefix} {subcat_word} {suffix}"

    return f"{prefix} {suffix}"


def generate_description(category: str, subcategory: str, tags: List[str]) -> str:
    """Generate business description"""
    descriptions = {
        "retail_shop": [
            "Discover the latest trends and quality products",
            "Your one-stop shop for all your needs",
            "Curated selection of premium items",
            "Shop local, shop quality",
        ],
        "food_beverage": [
            "Delicious food made with love and fresh ingredients",
            "Your neighborhood spot for great food and vibes",
            "Experience flavors that bring people together",
            "Good food, good mood, great times",
        ],
        "professional_services": [
            "Expert solutions tailored to your needs",
            "Professional service you can trust",
            "Helping businesses grow and succeed",
            "Your success is our priority",
        ],
        "home_services": [
            "Reliable service when you need it most",
            "Quality work, fair prices, trusted professionals",
            "Making your home life easier",
            "Professional help, just a click away",
        ],
        "personal_services": [
            "Pamper yourself, you deserve it",
            "Transform your look, transform your confidence",
            "Expert care for your personal wellness",
            "Self-care made accessible",
        ],
        "events": [
            "Unforgettable experiences await",
            "Connect, celebrate, and create memories",
            "Your next great experience starts here",
            "Bringing people together through amazing events",
        ],
        "entertainment": [
            "Fun for everyone, memories for life",
            "Your destination for entertainment and joy",
            "Experience the best in entertainment",
            "Where good times happen",
        ],
        "content_creator": [
            "Sharing my journey, one post at a time",
            "Creating content that inspires and entertains",
            "Follow along for daily inspiration",
            "Keeping it real, keeping it fun",
        ],
        "community_group": [
            "Connect with like-minded people",
            "Your community, your tribe, your space",
            "Building connections that matter",
            "Join the conversation, join the community",
        ],
        "local_discovery": [
            "Explore the best of your city",
            "Hidden gems waiting to be discovered",
            "Your guide to local adventures",
            "Discover something new today",
        ],
        "health_wellness": [
            "Your journey to better health starts here",
            "Wellness for body, mind, and soul",
            "Invest in yourself, invest in your health",
            "Empowering your health journey",
        ],
    }
    return random.choice(descriptions.get(category, descriptions["retail_shop"]))


def generate_business_profile(business_id: int) -> Dict:
    """Generate comprehensive business profile"""
    # Select category
    category = weighted_choice([(cat, data["weight"]) for cat, data in PLATFORM_CATEGORIES.items()])
    cat_data = PLATFORM_CATEGORIES[category]

    # Select subcategory
    subcat_data = random.choice(cat_data["subcategories"])
    subcategory = subcat_data["name"]
    base_tags = subcat_data["tags"]

    # Select location
    location = weighted_choice([(loc, loc["density"]) for loc in LOCATIONS])
    lat = location["lat"] + random.uniform(-0.02, 0.02)
    lon = location["lon"] + random.uniform(-0.02, 0.02)

    # Generate metrics
    base_rating = random.uniform(3.2, 5.0)
    rating_count = random.randint(5, 5000)

    # Popularity based on rating and type
    popularity = (base_rating / 5.0) * random.uniform(0.5, 1.0)

    # Content creators and trending places get boost
    if category in ["content_creator", "events"]:
        popularity *= random.uniform(1.0, 1.5)

    # Build tags
    tags = list(base_tags[:4])
    platform_tags = ["verified", "popular", "local_favorite", "trending", "new", "featured"]
    tags.extend(random.sample(platform_tags, random.randint(1, 3)))

    # Add business type tag
    tags.append(cat_data["type"])

    return {
        "id": business_id,
        "name": generate_business_name(category, subcategory),
        "description": generate_description(category, subcategory, tags),
        "category": category,
        "subcategory": subcategory,
        "business_type": cat_data["type"],
        "categories_json": json.dumps([category, subcategory, cat_data["type"]]),
        "tags_json": json.dumps(list(set(tags))),
        "location_json": json.dumps({"lat": lat, "lon": lon, "area": location["name"]}),
        "popularity": popularity,
        "rating": round(base_rating, 1),
        "rating_count": rating_count,
    }


def generate_user_profile(user_id: int) -> Dict:
    """Generate diverse user profile"""
    # Select segment
    segment = weighted_choice([(seg, data["weight"]) for seg, data in USER_SEGMENTS.items()])
    seg_data = USER_SEGMENTS[segment]

    # Generate name and credentials (use user_id to ensure uniqueness)
    first_name = random.choice(FIRST_NAMES)
    last_name = random.choice(LAST_NAMES)
    username = f"{first_name.lower()}_{last_name.lower()}_{user_id}"
    email = f"user{user_id}@htiapp.test"

    # Build interests from segment
    base_interests = list(seg_data["interests"])

    # Add content preferences as interests
    content_prefs = seg_data["content_preferences"]
    all_interests = base_interests + content_prefs

    # Maybe add random extra interests
    all_categories = list(PLATFORM_CATEGORIES.keys())
    extra = random.sample([c for c in all_categories if c not in base_interests], random.randint(0, 2))
    all_interests.extend(extra)

    # Select location
    location = weighted_choice([(loc, loc["density"]) for loc in LOCATIONS])
    lat = location["lat"] + random.uniform(-0.015, 0.015)
    lon = location["lon"] + random.uniform(-0.015, 0.015)

    return {
        "id": user_id,
        "username": username,
        "email": email,
        "segment": segment,
        "interests_json": json.dumps(list(set(all_interests))),
        "location_json": json.dumps({"lat": lat, "lon": lon, "area": location["name"]}),
        "active_hours": seg_data["active_hours"],
        "interaction_rate": seg_data["interaction_rate"],
        "behavior": seg_data["behavior"],
    }


def calculate_interaction_probability(
    user: Dict,
    business: Dict,
    hour: int,
    season: str,
    day_of_week: int
) -> float:
    """Calculate probability of user interacting with business"""
    score = 0.0

    # 1. Interest match (35%)
    user_interests = json.loads(user["interests_json"])
    biz_cats = json.loads(business["categories_json"])
    interest_overlap = len(set(user_interests) & set(biz_cats))
    score += (interest_overlap / max(len(user_interests), 1)) * 0.35

    # 2. Location proximity (20%)
    user_loc = json.loads(user["location_json"])
    biz_loc = json.loads(business["location_json"])
    distance = math.sqrt(
        (user_loc["lat"] - biz_loc["lat"])**2 +
        (user_loc["lon"] - biz_loc["lon"])**2
    )
    proximity = max(0, 1.0 - distance * 30)
    score += proximity * 0.20

    # 3. Time relevance (15%)
    time_pattern = get_time_pattern(hour)
    pattern_data = TIME_PATTERNS[time_pattern]
    if business["category"] in pattern_data["boost_categories"]:
        score += 0.15
    else:
        score += 0.05

    # 4. Seasonal boost (10%)
    seasonal_boost = SEASONAL_TRENDS[season]["boost"].get(business["category"], 1.0)
    score += (seasonal_boost - 0.8) * 0.10

    # 5. Business popularity (10%)
    score += business["popularity"] * 0.10

    # 6. Weekend boost for certain categories (5%)
    if day_of_week >= 5:  # Weekend
        if business["category"] in ["events", "entertainment", "food_beverage", "local_discovery"]:
            score += 0.05

    # 7. User interaction rate modifier (5%)
    score += (user["interaction_rate"] - 0.5) * 0.05

    # Add randomness
    score *= random.uniform(0.85, 1.15)

    return min(max(score, 0), 1)


def determine_interaction_type(score: float, behavior: str) -> Tuple[str, float]:
    """Determine interaction type based on score and user behavior"""
    rand = random.random()

    # Adjust based on user behavior
    if behavior == "purchase_focused":
        # More likely to save and purchase
        if rand < 0.40:
            return "view", 1.0
        elif rand < 0.60:
            return "like", 2.0
        elif rand < 0.82:
            return "save", 3.0
        elif rand < 0.95:
            return "purchase", 5.0
        else:
            return "share", 4.0

    elif behavior == "high_engagement":
        # More likes and shares
        if rand < 0.35:
            return "view", 1.0
        elif rand < 0.65:
            return "like", 2.0
        elif rand < 0.80:
            return "save", 3.0
        elif rand < 0.92:
            return "share", 4.0
        else:
            return "purchase", 5.0

    elif behavior == "passive_viewer":
        # Mostly views
        if rand < 0.65:
            return "view", 1.0
        elif rand < 0.85:
            return "like", 2.0
        elif rand < 0.95:
            return "save", 3.0
        else:
            return "share", 4.0

    else:
        # Default distribution
        if rand < 0.50:
            return "view", 1.0
        elif rand < 0.75:
            return "like", 2.0
        elif rand < 0.90:
            return "save", 3.0
        elif rand < 0.97:
            return "purchase", 5.0
        else:
            return "share", 4.0


def generate_daily_interactions(
    date: datetime,
    users: List[Dict],
    businesses: List[Dict]
) -> List[Dict]:
    """Generate interactions for a day"""
    interactions = []
    season = get_season(date.month)
    day_of_week = date.weekday()

    # Adjust count based on day
    if day_of_week >= 5:  # Weekend
        daily_count = random.randint(
            int(MAX_INTERACTIONS_PER_DAY * 0.7),
            MAX_INTERACTIONS_PER_DAY
        )
    else:
        daily_count = random.randint(
            MIN_INTERACTIONS_PER_DAY,
            int(MAX_INTERACTIONS_PER_DAY * 0.75)
        )

    seen = set()
    attempts = 0

    while len(interactions) < daily_count and attempts < daily_count * 3:
        attempts += 1

        user = random.choice(users)

        # Select hour based on user's active hours
        slots = user["active_hours"]
        if not slots:
            slots = [(9, 22)]

        slot = random.choice(slots)
        hour = random.randint(slot[0], min(slot[1] - 1, 23))
        minute = random.randint(0, 59)
        second = random.randint(0, 59)

        try:
            timestamp = date.replace(hour=hour, minute=minute, second=second, microsecond=0)
        except ValueError:
            continue

        # Sample and score candidates
        candidates = random.sample(businesses, min(40, len(businesses)))
        scored = []

        for biz in candidates:
            prob = calculate_interaction_probability(user, biz, hour, season, day_of_week)
            scored.append((biz, prob))

        scored.sort(key=lambda x: x[1], reverse=True)

        # Pick from top candidates
        top_n = min(8, len(scored))
        selected_biz, score = random.choice(scored[:top_n])

        # Determine interaction type
        interaction_type, weight = determine_interaction_type(score, user["behavior"])

        # Check uniqueness
        key = (user["id"], selected_biz["id"], interaction_type)
        if key in seen:
            continue
        seen.add(key)

        interactions.append({
            "user_id": user["id"],
            "business_id": selected_biz["id"],
            "interaction_type": interaction_type,
            "weight": weight,
            "timestamp": timestamp,
        })

    return interactions


async def generate_all_data():
    """Main generation function"""
    print("=" * 75)
    print("  HTI SUPER APP - Social Marketplace Data Generator")
    print("  Facebook + Reddit + Twitter + Marketplace + Events + Services")
    print("=" * 75)

    async with AsyncSessionLocal() as db:
        # Clear existing data
        print("\n[1/4] Clearing existing data...")
        await db.execute(text("TRUNCATE TABLE user_interactions CASCADE"))
        await db.execute(text("TRUNCATE TABLE users CASCADE"))
        await db.execute(text("TRUNCATE TABLE businesses CASCADE"))
        await db.commit()
        print("      Done")

        # Generate businesses
        print(f"\n[2/4] Generating {NUM_BUSINESSES} businesses/shops/creators...")
        businesses = []
        category_counts = {}
        type_counts = {}

        for i in range(1, NUM_BUSINESSES + 1):
            biz = generate_business_profile(i)

            cat = biz["category"]
            btype = biz["business_type"]
            category_counts[cat] = category_counts.get(cat, 0) + 1
            type_counts[btype] = type_counts.get(btype, 0) + 1

            await db.execute(
                text("""
                    INSERT INTO businesses
                    (name, description, categories, tags, location, popularity_score, rating, rating_count)
                    VALUES (:name, :description, :categories, :tags, :location, :popularity, :rating, :rating_count)
                """),
                {
                    "name": biz["name"],
                    "description": biz["description"],
                    "categories": biz["categories_json"],
                    "tags": biz["tags_json"],
                    "location": biz["location_json"],
                    "popularity": round(biz["popularity"] * 10, 2),
                    "rating": biz["rating"],
                    "rating_count": biz["rating_count"],
                }
            )
            businesses.append(biz)

            if i % 100 == 0:
                await db.commit()
                print(f"      Generated {i}/{NUM_BUSINESSES}")

        await db.commit()
        print(f"      Done - {NUM_BUSINESSES} entities created")
        print(f"      Types: {type_counts}")

        # Generate users
        print(f"\n[3/4] Generating {NUM_USERS} users...")
        users = []
        segment_counts = {}

        for i in range(1, NUM_USERS + 1):
            user = generate_user_profile(i)

            seg = user["segment"]
            segment_counts[seg] = segment_counts.get(seg, 0) + 1

            await db.execute(
                text("""
                    INSERT INTO users (username, email, interests, location)
                    VALUES (:username, :email, :interests, :location)
                """),
                {
                    "username": user["username"],
                    "email": user["email"],
                    "interests": user["interests_json"],
                    "location": user["location_json"],
                }
            )
            users.append(user)

            if i % 200 == 0:
                await db.commit()
                print(f"      Generated {i}/{NUM_USERS}")

        await db.commit()
        print(f"      Done - {NUM_USERS} users created")
        print(f"      Segments: {segment_counts}")

        # Generate 6 months of interactions
        print(f"\n[4/4] Generating {DAYS_OF_DATA} days of interactions...")

        total_interactions = 0
        start_date = datetime.now() - timedelta(days=DAYS_OF_DATA)
        interaction_counts = {}
        monthly_counts = {}

        for day_offset in range(DAYS_OF_DATA):
            current_date = start_date + timedelta(days=day_offset)
            month_key = current_date.strftime("%Y-%m")

            if day_offset % 30 == 0:
                month_num = day_offset // 30 + 1
                print(f"      Month {month_num}/6: {current_date.strftime('%Y-%m')}...")

            daily = generate_daily_interactions(current_date, users, businesses)

            batch_size = 500
            for i in range(0, len(daily), batch_size):
                batch = daily[i:i + batch_size]
                for interaction in batch:
                    try:
                        await db.execute(
                            text("""
                                INSERT INTO user_interactions
                                (user_id, business_id, interaction_type, weight, timestamp)
                                VALUES (:user_id, :business_id, :interaction_type, :weight, :timestamp)
                                ON CONFLICT (user_id, business_id, interaction_type) DO NOTHING
                            """),
                            interaction
                        )
                        itype = interaction["interaction_type"]
                        interaction_counts[itype] = interaction_counts.get(itype, 0) + 1
                    except Exception:
                        pass
                await db.commit()

            monthly_counts[month_key] = monthly_counts.get(month_key, 0) + len(daily)
            total_interactions += len(daily)

        await db.commit()

        # Final stats
        print("\n" + "=" * 75)
        print("  GENERATION COMPLETE")
        print("=" * 75)

        result = await db.execute(text("SELECT COUNT(*) FROM users"))
        user_count = result.scalar()

        result = await db.execute(text("SELECT COUNT(*) FROM businesses"))
        business_count = result.scalar()

        result = await db.execute(text("SELECT COUNT(*) FROM user_interactions"))
        interaction_count = result.scalar()

        print(f"\n  DATASET SUMMARY:")
        print(f"  {'='*40}")
        print(f"  Users:          {user_count:,}")
        print(f"  Businesses:     {business_count:,}")
        print(f"  Interactions:   {interaction_count:,}")
        print(f"  Avg/user:       {interaction_count/user_count:,.1f}")

        print(f"\n  BUSINESS TYPES:")
        for btype, count in sorted(type_counts.items(), key=lambda x: -x[1]):
            print(f"    {btype:15}: {count}")

        print(f"\n  USER SEGMENTS:")
        for seg, count in sorted(segment_counts.items(), key=lambda x: -x[1]):
            print(f"    {seg:20}: {count}")

        print(f"\n  INTERACTION TYPES:")
        for itype, count in sorted(interaction_counts.items(), key=lambda x: -x[1]):
            pct = count / sum(interaction_counts.values()) * 100
            print(f"    {itype:10}: {count:,} ({pct:.1f}%)")

        print(f"\n  MONTHLY ACTIVITY:")
        for month, count in sorted(monthly_counts.items()):
            print(f"    {month}: {count:,}")

        print(f"\n  TIME RANGE: {start_date.strftime('%Y-%m-%d')} to {datetime.now().strftime('%Y-%m-%d')}")

        print(f"\n  TEST YOUR RECOMMENDATIONS:")
        print(f"    curl http://localhost:8000/recommend/1")
        print(f"    curl http://localhost:8000/recommend/500")
        print(f"    curl http://localhost:8000/health")
        print(f"    http://localhost:8000/docs")

        print("\n" + "=" * 75)


async def main():
    try:
        await generate_all_data()
    except KeyboardInterrupt:
        print("\n\nInterrupted")
    except Exception as e:
        print(f"\nError: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())
