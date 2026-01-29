#!/usr/bin/env python3
"""
HTI (Health Technology Innovation) App - Realistic 6-Month Data Generator

Generates realistic health & wellness marketplace data including:
- Healthcare providers, fitness centers, pharmacies, wellness services
- Diverse user segments with health-related interests
- 6 months of realistic interaction patterns with seasonal health trends
"""
import asyncio
import json
import random
import sys
from datetime import datetime, timedelta
from typing import List, Dict, Tuple
import hashlib

sys.path.insert(0, '/app')

from app.database import AsyncSessionLocal
from sqlalchemy import text

# ========== CONFIGURATION ==========
NUM_BUSINESSES = 500
NUM_USERS = 1000
DAYS_OF_DATA = 180  # 6 months
MIN_INTERACTIONS_PER_DAY = 800
MAX_INTERACTIONS_PER_DAY = 4000

# ========== HTI BUSINESS CATEGORIES ==========
HTI_CATEGORIES = {
    "healthcare": {
        "weight": 0.20,
        "subcategories": [
            {"name": "general_clinic", "tags": ["primary_care", "family_medicine", "checkup", "consultation"]},
            {"name": "specialist", "tags": ["cardiology", "dermatology", "orthopedics", "neurology"]},
            {"name": "dental", "tags": ["dentist", "orthodontics", "oral_health", "teeth_whitening"]},
            {"name": "eye_care", "tags": ["optometry", "vision", "glasses", "contacts", "lasik"]},
            {"name": "urgent_care", "tags": ["walk_in", "emergency", "after_hours", "quick_service"]},
        ]
    },
    "pharmacy": {
        "weight": 0.15,
        "subcategories": [
            {"name": "retail_pharmacy", "tags": ["prescriptions", "otc", "medicine", "delivery"]},
            {"name": "compounding", "tags": ["custom_medication", "specialty", "personalized"]},
            {"name": "online_pharmacy", "tags": ["delivery", "subscription", "refills", "telehealth"]},
        ]
    },
    "fitness": {
        "weight": 0.18,
        "subcategories": [
            {"name": "gym", "tags": ["weights", "cardio", "24_hour", "personal_training"]},
            {"name": "yoga_studio", "tags": ["yoga", "meditation", "mindfulness", "flexibility"]},
            {"name": "crossfit", "tags": ["hiit", "strength", "community", "competition"]},
            {"name": "pilates", "tags": ["core", "posture", "rehabilitation", "low_impact"]},
            {"name": "martial_arts", "tags": ["self_defense", "discipline", "fitness", "training"]},
            {"name": "swimming", "tags": ["aquatic", "low_impact", "cardio", "lessons"]},
        ]
    },
    "mental_health": {
        "weight": 0.12,
        "subcategories": [
            {"name": "therapy", "tags": ["counseling", "psychotherapy", "anxiety", "depression"]},
            {"name": "psychiatry", "tags": ["medication_management", "mental_illness", "diagnosis"]},
            {"name": "wellness_coaching", "tags": ["life_coaching", "stress_management", "mindfulness"]},
            {"name": "support_groups", "tags": ["community", "peer_support", "recovery", "group_therapy"]},
        ]
    },
    "nutrition": {
        "weight": 0.12,
        "subcategories": [
            {"name": "health_food_store", "tags": ["organic", "supplements", "vitamins", "natural"]},
            {"name": "nutritionist", "tags": ["diet_planning", "weight_management", "meal_prep"]},
            {"name": "juice_bar", "tags": ["smoothies", "cold_pressed", "detox", "vegan"]},
            {"name": "meal_delivery", "tags": ["healthy_meals", "portion_control", "diet_specific"]},
        ]
    },
    "wellness_spa": {
        "weight": 0.10,
        "subcategories": [
            {"name": "spa", "tags": ["massage", "relaxation", "facial", "body_treatment"]},
            {"name": "acupuncture", "tags": ["traditional_medicine", "pain_relief", "holistic"]},
            {"name": "chiropractic", "tags": ["spine", "alignment", "pain_management", "posture"]},
            {"name": "float_therapy", "tags": ["sensory_deprivation", "relaxation", "recovery"]},
        ]
    },
    "diagnostics": {
        "weight": 0.08,
        "subcategories": [
            {"name": "lab_testing", "tags": ["blood_work", "diagnostics", "health_screening"]},
            {"name": "imaging_center", "tags": ["xray", "mri", "ct_scan", "ultrasound"]},
            {"name": "genetic_testing", "tags": ["dna", "ancestry", "health_risk", "personalized"]},
        ]
    },
    "medical_equipment": {
        "weight": 0.05,
        "subcategories": [
            {"name": "medical_supplies", "tags": ["home_health", "mobility", "diabetes_supplies"]},
            {"name": "wearables", "tags": ["fitness_tracker", "smart_watch", "health_monitoring"]},
        ]
    },
}

# ========== HTI USER SEGMENTS ==========
HTI_USER_SEGMENTS = {
    "fitness_enthusiast": {
        "age_range": (20, 40),
        "weight": 0.25,
        "interests": ["fitness", "nutrition", "wellness_spa"],
        "active_hours": [(6, 8), (17, 21)],  # Early morning and after work
        "health_focus": ["weight_training", "cardio", "supplements", "protein"],
    },
    "health_conscious_parent": {
        "age_range": (28, 50),
        "weight": 0.20,
        "interests": ["healthcare", "pharmacy", "nutrition", "fitness"],
        "active_hours": [(9, 12), (19, 22)],  # School hours and evenings
        "health_focus": ["family_health", "pediatrics", "vitamins", "healthy_meals"],
    },
    "chronic_condition_manager": {
        "age_range": (35, 70),
        "weight": 0.15,
        "interests": ["healthcare", "pharmacy", "diagnostics"],
        "active_hours": [(8, 18)],  # Regular business hours
        "health_focus": ["medication", "monitoring", "specialist_care", "lab_testing"],
    },
    "wellness_seeker": {
        "age_range": (25, 55),
        "weight": 0.18,
        "interests": ["mental_health", "wellness_spa", "nutrition", "fitness"],
        "active_hours": [(10, 14), (18, 22)],
        "health_focus": ["stress_relief", "meditation", "holistic", "self_care"],
    },
    "senior_health": {
        "age_range": (60, 85),
        "weight": 0.12,
        "interests": ["healthcare", "pharmacy", "diagnostics", "wellness_spa"],
        "active_hours": [(9, 16)],
        "health_focus": ["mobility", "chronic_care", "prevention", "checkups"],
    },
    "young_professional": {
        "age_range": (22, 35),
        "weight": 0.10,
        "interests": ["fitness", "mental_health", "nutrition"],
        "active_hours": [(7, 9), (12, 13), (18, 23)],
        "health_focus": ["convenience", "stress", "quick_service", "apps"],
    },
}

# ========== LOCATION CLUSTERS (Major Health Districts) ==========
HTI_LOCATIONS = [
    {"name": "medical_district", "lat": 40.7614, "lon": -73.9776, "density": 0.30,
     "business_bias": ["healthcare", "diagnostics", "pharmacy"]},
    {"name": "fitness_district", "lat": 40.7484, "lon": -73.9857, "density": 0.20,
     "business_bias": ["fitness", "nutrition"]},
    {"name": "wellness_village", "lat": 40.7282, "lon": -73.7949, "density": 0.20,
     "business_bias": ["wellness_spa", "mental_health", "nutrition"]},
    {"name": "suburban_health", "lat": 40.6782, "lon": -73.9442, "density": 0.15,
     "business_bias": ["healthcare", "pharmacy", "fitness"]},
    {"name": "downtown_express", "lat": 40.7128, "lon": -74.0060, "density": 0.15,
     "business_bias": ["pharmacy", "urgent_care", "fitness"]},
]

# ========== SEASONAL HEALTH TRENDS ==========
SEASONAL_TRENDS = {
    "winter": {  # Dec, Jan, Feb
        "months": [12, 1, 2],
        "category_boost": {
            "healthcare": 1.4,  # Flu season
            "pharmacy": 1.5,
            "mental_health": 1.3,  # SAD
            "fitness": 1.2,  # New Year resolutions
        }
    },
    "spring": {  # Mar, Apr, May
        "months": [3, 4, 5],
        "category_boost": {
            "fitness": 1.4,  # Getting in shape
            "nutrition": 1.3,
            "wellness_spa": 1.2,
            "diagnostics": 1.2,  # Annual checkups
        }
    },
    "summer": {  # Jun, Jul, Aug
        "months": [6, 7, 8],
        "category_boost": {
            "fitness": 1.3,
            "nutrition": 1.2,
            "wellness_spa": 1.4,
            "healthcare": 0.9,  # Lower routine visits
        }
    },
    "fall": {  # Sep, Oct, Nov
        "months": [9, 10, 11],
        "category_boost": {
            "healthcare": 1.2,  # Back to school checkups
            "pharmacy": 1.2,  # Flu shots
            "mental_health": 1.2,  # Transition stress
            "fitness": 1.1,
        }
    },
}

# ========== BUSINESS NAME PREFIXES/SUFFIXES ==========
BUSINESS_NAMES = {
    "healthcare": {
        "prefixes": ["Premier", "Family", "Advanced", "Metro", "Community", "Elite", "Wellness", "Care"],
        "suffixes": ["Medical Center", "Health Clinic", "Care Center", "Medical Group", "Health Partners"]
    },
    "pharmacy": {
        "prefixes": ["Quick", "Care", "Health", "Metro", "Family", "Express", "Plus"],
        "suffixes": ["Pharmacy", "Rx", "Drug Store", "Medicine Shop", "Health Mart"]
    },
    "fitness": {
        "prefixes": ["Iron", "Peak", "Flex", "Power", "Core", "Fit", "Prime", "Strong"],
        "suffixes": ["Fitness", "Gym", "Studio", "Athletics", "Training Center", "Performance"]
    },
    "mental_health": {
        "prefixes": ["Mindful", "Serenity", "Balance", "Clarity", "Harmony", "Inner", "Peaceful"],
        "suffixes": ["Counseling", "Therapy Center", "Wellness", "Mental Health", "Psychology"]
    },
    "nutrition": {
        "prefixes": ["Fresh", "Natural", "Pure", "Organic", "Vital", "Green", "Nourish"],
        "suffixes": ["Nutrition", "Health Foods", "Wellness Market", "Juice Bar", "Kitchen"]
    },
    "wellness_spa": {
        "prefixes": ["Serenity", "Bliss", "Tranquil", "Zen", "Harmony", "Radiant", "Pure"],
        "suffixes": ["Spa", "Wellness Center", "Retreat", "Body Works", "Healing Center"]
    },
    "diagnostics": {
        "prefixes": ["Precision", "Advanced", "Metro", "Quick", "Accurate", "Complete"],
        "suffixes": ["Diagnostics", "Lab Services", "Testing Center", "Imaging", "Health Labs"]
    },
    "medical_equipment": {
        "prefixes": ["Med", "Health", "Care", "Home", "Pro", "Quality"],
        "suffixes": ["Supply", "Equipment", "Medical Supplies", "Health Store", "Med Shop"]
    },
}

# ========== REALISTIC USER NAMES ==========
FIRST_NAMES = [
    "Emma", "Liam", "Olivia", "Noah", "Ava", "Ethan", "Sophia", "Mason",
    "Isabella", "William", "Mia", "James", "Charlotte", "Benjamin", "Amelia",
    "Lucas", "Harper", "Henry", "Evelyn", "Alexander", "Abigail", "Michael",
    "Emily", "Daniel", "Elizabeth", "Matthew", "Sofia", "David", "Avery",
    "Joseph", "Ella", "Samuel", "Scarlett", "Sebastian", "Grace", "Jack",
    "Victoria", "Owen", "Riley", "Theodore", "Aria", "Aiden", "Luna",
    "John", "Chloe", "Ryan", "Penelope", "Nathan", "Layla", "Caleb"
]

LAST_NAMES = [
    "Smith", "Johnson", "Williams", "Brown", "Jones", "Garcia", "Miller",
    "Davis", "Rodriguez", "Martinez", "Hernandez", "Lopez", "Gonzalez",
    "Wilson", "Anderson", "Thomas", "Taylor", "Moore", "Jackson", "Martin",
    "Lee", "Perez", "Thompson", "White", "Harris", "Sanchez", "Clark",
    "Ramirez", "Lewis", "Robinson", "Walker", "Young", "Allen", "King",
    "Wright", "Scott", "Torres", "Nguyen", "Hill", "Flores", "Green",
    "Adams", "Nelson", "Baker", "Hall", "Rivera", "Campbell", "Mitchell"
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
    """Get season name from month"""
    for season, data in SEASONAL_TRENDS.items():
        if month in data["months"]:
            return season
    return "spring"


def generate_business_name(category: str, subcategory: str, business_id: int) -> str:
    """Generate realistic business name"""
    name_data = BUSINESS_NAMES.get(category, BUSINESS_NAMES["healthcare"])
    prefix = random.choice(name_data["prefixes"])
    suffix = random.choice(name_data["suffixes"])

    # Sometimes add location flavor
    if random.random() < 0.3:
        areas = ["Downtown", "Midtown", "East Side", "West End", "Central", "Park"]
        return f"{random.choice(areas)} {prefix} {suffix}"

    return f"{prefix} {suffix}"


def generate_business_description(category: str, subcategory: str, tags: List[str]) -> str:
    """Generate realistic business description"""
    descriptions = {
        "healthcare": [
            "Comprehensive healthcare services with experienced medical professionals",
            "Patient-centered care focused on your health and wellness",
            "Modern medical facility offering a full range of health services",
        ],
        "pharmacy": [
            "Your trusted neighborhood pharmacy with personalized service",
            "Fast, reliable prescription services with free delivery",
            "Full-service pharmacy with health consultations available",
        ],
        "fitness": [
            "State-of-the-art fitness facility with expert trainers",
            "Transform your health with our comprehensive fitness programs",
            "Modern gym equipment and personalized training plans",
        ],
        "mental_health": [
            "Compassionate mental health services in a supportive environment",
            "Professional counseling and therapy for all life challenges",
            "Your journey to mental wellness starts here",
        ],
        "nutrition": [
            "Fresh, organic products for a healthier lifestyle",
            "Expert nutrition guidance and quality health foods",
            "Fuel your body with the best natural ingredients",
        ],
        "wellness_spa": [
            "Relaxation and rejuvenation for mind, body, and soul",
            "Premium spa treatments in a tranquil setting",
            "Experience ultimate wellness and stress relief",
        ],
        "diagnostics": [
            "Accurate, fast diagnostic testing with quick results",
            "Advanced medical imaging and lab services",
            "Comprehensive health screening and testing",
        ],
        "medical_equipment": [
            "Quality medical supplies and health equipment",
            "Home health solutions for better daily living",
            "Trusted source for medical equipment and supplies",
        ],
    }
    return random.choice(descriptions.get(category, descriptions["healthcare"]))


def generate_business_profile(business_id: int) -> Dict:
    """Generate realistic HTI business profile"""
    # Select category based on weight
    category = weighted_choice([(cat, data["weight"]) for cat, data in HTI_CATEGORIES.items()])
    cat_data = HTI_CATEGORIES[category]

    # Select subcategory
    subcat_data = random.choice(cat_data["subcategories"])
    subcategory = subcat_data["name"]
    base_tags = subcat_data["tags"]

    # Select location (with bias toward certain areas for certain categories)
    location_weights = []
    for loc in HTI_LOCATIONS:
        weight = loc["density"]
        if category in loc.get("business_bias", []):
            weight *= 1.5
        location_weights.append((loc, weight))

    location = weighted_choice(location_weights)

    # Add location randomness
    lat = location["lat"] + random.uniform(-0.015, 0.015)
    lon = location["lon"] + random.uniform(-0.015, 0.015)

    # Generate ratings and popularity
    base_rating = random.uniform(3.5, 5.0)
    rating_count = random.randint(20, 2000)

    # Higher rated places tend to be more popular
    popularity_base = (base_rating / 5.0) * random.uniform(0.6, 1.0)
    trending = random.uniform(0.8, 1.3)

    # Build tags
    tags = list(base_tags[:3])
    generic_tags = ["verified", "accepting_new", "insurance_accepted", "online_booking", "telehealth"]
    tags.extend(random.sample(generic_tags, min(2, len(generic_tags))))

    return {
        "id": business_id,
        "name": generate_business_name(category, subcategory, business_id),
        "description": generate_business_description(category, subcategory, tags),
        "category": category,
        "subcategory": subcategory,
        "categories_json": json.dumps([category, subcategory]),
        "tags_json": json.dumps(tags),
        "location_json": json.dumps({"lat": lat, "lon": lon, "area": location["name"]}),
        "popularity_base": popularity_base,
        "trending": trending,
        "rating": round(base_rating, 1),
        "rating_count": rating_count,
    }


def generate_user_profile(user_id: int) -> Dict:
    """Generate realistic HTI user profile"""
    # Select segment
    segment = weighted_choice([(seg, data["weight"]) for seg, data in HTI_USER_SEGMENTS.items()])
    seg_data = HTI_USER_SEGMENTS[segment]

    # Generate name
    first_name = random.choice(FIRST_NAMES)
    last_name = random.choice(LAST_NAMES)
    username = f"{first_name.lower()}_{last_name.lower()}_{user_id}"
    email = f"{first_name.lower()}.{last_name.lower()}{random.randint(1, 99)}@email.com"

    # Interests based on segment
    base_interests = list(seg_data["interests"])
    # Add 1-2 random additional interests
    all_categories = list(HTI_CATEGORIES.keys())
    extra = random.sample([c for c in all_categories if c not in base_interests], min(2, len(all_categories)))
    interests = base_interests + extra[:random.randint(0, 2)]

    # Add health focus topics as interests
    health_focus = seg_data["health_focus"]
    interests.extend(random.sample(health_focus, min(2, len(health_focus))))

    # Select location
    location = weighted_choice([(loc, loc["density"]) for loc in HTI_LOCATIONS])
    lat = location["lat"] + random.uniform(-0.01, 0.01)
    lon = location["lon"] + random.uniform(-0.01, 0.01)

    return {
        "id": user_id,
        "username": username,
        "email": email,
        "segment": segment,
        "interests_json": json.dumps(interests),
        "location_json": json.dumps({"lat": lat, "lon": lon, "area": location["name"]}),
        "active_hours": seg_data["active_hours"],
        "activity_level": random.uniform(0.3, 1.0),
        "health_focus": health_focus,
    }


def calculate_interaction_probability(
    user: Dict,
    business: Dict,
    hour: int,
    season: str
) -> float:
    """Calculate probability of user interacting with business"""
    score = 0.0

    # 1. Interest match (40%)
    user_interests = json.loads(user["interests_json"])
    biz_cats = json.loads(business["categories_json"])
    interest_overlap = len(set(user_interests) & set(biz_cats))
    score += (interest_overlap / max(len(user_interests), 1)) * 0.40

    # 2. Location proximity (25%)
    user_loc = json.loads(user["location_json"])
    biz_loc = json.loads(business["location_json"])
    distance = abs(user_loc["lat"] - biz_loc["lat"]) + abs(user_loc["lon"] - biz_loc["lon"])
    proximity = max(0, 1.0 - distance * 50)  # Closer = higher score
    score += proximity * 0.25

    # 3. Time relevance (15%)
    time_bonus = 0.0
    category = business["category"]

    # Healthcare/pharmacy peak during business hours
    if category in ["healthcare", "pharmacy", "diagnostics"]:
        if 8 <= hour <= 18:
            time_bonus = 1.0
        elif 18 <= hour <= 20:
            time_bonus = 0.5  # Urgent care hours
    # Fitness peaks morning and evening
    elif category == "fitness":
        if 6 <= hour <= 8 or 17 <= hour <= 21:
            time_bonus = 1.0
        elif 12 <= hour <= 13:
            time_bonus = 0.6  # Lunch workouts
    # Mental health during work hours
    elif category == "mental_health":
        if 9 <= hour <= 19:
            time_bonus = 1.0
    # Wellness/spa peaks midday and weekends
    elif category == "wellness_spa":
        if 10 <= hour <= 20:
            time_bonus = 1.0
    # Nutrition - throughout the day
    elif category == "nutrition":
        if 7 <= hour <= 21:
            time_bonus = 1.0
    else:
        time_bonus = 0.5

    score += time_bonus * 0.15

    # 4. Seasonal boost (10%)
    seasonal_boost = SEASONAL_TRENDS[season]["category_boost"].get(category, 1.0)
    score += (seasonal_boost - 0.5) * 0.10  # Normalize around 0.5

    # 5. Business popularity (10%)
    popularity = business["popularity_base"] * business["trending"]
    score += popularity * 0.10

    # Add some randomness
    score *= random.uniform(0.8, 1.2)

    return min(max(score, 0), 1)


def determine_interaction_type(user: Dict, business: Dict, score: float) -> Tuple[str, float]:
    """Determine interaction type based on context"""
    # Higher engagement for businesses matching user interests well
    rand = random.random()

    if score > 0.7:  # High relevance
        if rand < 0.45:
            return "view", 1.0
        elif rand < 0.70:
            return "like", 2.0
        elif rand < 0.88:
            return "save", 3.0
        elif rand < 0.96:
            return "purchase", 5.0
        else:
            return "share", 4.0
    elif score > 0.4:  # Medium relevance
        if rand < 0.55:
            return "view", 1.0
        elif rand < 0.80:
            return "like", 2.0
        elif rand < 0.93:
            return "save", 3.0
        else:
            return "purchase", 5.0
    else:  # Low relevance - mostly just views
        if rand < 0.70:
            return "view", 1.0
        elif rand < 0.90:
            return "like", 2.0
        else:
            return "save", 3.0


def generate_daily_interactions(
    date: datetime,
    users: List[Dict],
    businesses: List[Dict]
) -> List[Dict]:
    """Generate interactions for a specific day"""
    interactions = []

    # Seasonal and day-of-week adjustments
    season = get_season(date.month)
    day_of_week = date.weekday()

    # Weekends have different patterns
    if day_of_week >= 5:  # Weekend
        daily_count = random.randint(
            int(MAX_INTERACTIONS_PER_DAY * 0.6),
            MAX_INTERACTIONS_PER_DAY
        )
    else:  # Weekday
        daily_count = random.randint(
            MIN_INTERACTIONS_PER_DAY,
            int(MAX_INTERACTIONS_PER_DAY * 0.7)
        )

    # Track unique interactions to avoid duplicates within same day
    seen_interactions = set()

    attempts = 0
    while len(interactions) < daily_count and attempts < daily_count * 3:
        attempts += 1

        # Select user
        user = random.choice(users)

        # Determine hour based on user's active hours
        active_slots = user["active_hours"]
        if not active_slots:
            active_slots = [(9, 21)]

        slot = random.choice(active_slots)
        hour = random.randint(slot[0], min(slot[1] - 1, 23))
        minute = random.randint(0, 59)
        second = random.randint(0, 59)

        try:
            timestamp = date.replace(hour=hour, minute=minute, second=second, microsecond=0)
        except ValueError:
            continue

        # Sample candidate businesses
        candidates = random.sample(businesses, min(30, len(businesses)))

        # Score and select
        scored = []
        for biz in candidates:
            prob = calculate_interaction_probability(user, biz, hour, season)
            scored.append((biz, prob))

        scored.sort(key=lambda x: x[1], reverse=True)

        # Select from top candidates with some randomness
        top_n = min(5, len(scored))
        selected_biz, score = random.choice(scored[:top_n])

        # Check for duplicate
        interaction_key = (user["id"], selected_biz["id"])

        # Determine interaction type
        interaction_type, weight = determine_interaction_type(user, selected_biz, score)

        # Allow same user-business pair with different interaction types
        full_key = (user["id"], selected_biz["id"], interaction_type)
        if full_key in seen_interactions:
            continue
        seen_interactions.add(full_key)

        interactions.append({
            "user_id": user["id"],
            "business_id": selected_biz["id"],
            "interaction_type": interaction_type,
            "weight": weight,
            "timestamp": timestamp,
        })

    return interactions


async def generate_all_data():
    """Main data generation function"""
    print("=" * 70)
    print("  HTI (Health Technology Innovation) App - Data Generator")
    print("  Generating 6 months of realistic health marketplace data")
    print("=" * 70)

    async with AsyncSessionLocal() as db:
        # Clear existing data
        print("\n[1/4] Clearing existing data...")
        await db.execute(text("TRUNCATE TABLE user_interactions CASCADE"))
        await db.execute(text("TRUNCATE TABLE users CASCADE"))
        await db.execute(text("TRUNCATE TABLE businesses CASCADE"))
        await db.commit()
        print("      Done - existing data cleared")

        # Generate businesses
        print(f"\n[2/4] Generating {NUM_BUSINESSES} HTI businesses...")
        businesses = []

        category_counts = {}
        for i in range(1, NUM_BUSINESSES + 1):
            biz = generate_business_profile(i)

            cat = biz["category"]
            category_counts[cat] = category_counts.get(cat, 0) + 1

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
                    "popularity": round(biz["popularity_base"] * biz["trending"] * 10, 2),
                    "rating": biz["rating"],
                    "rating_count": biz["rating_count"],
                }
            )
            businesses.append(biz)

            if i % 100 == 0:
                await db.commit()
                print(f"      Generated {i}/{NUM_BUSINESSES} businesses")

        await db.commit()
        print(f"      Done - {NUM_BUSINESSES} businesses created")
        print(f"      Category distribution: {category_counts}")

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
                print(f"      Generated {i}/{NUM_USERS} users")

        await db.commit()
        print(f"      Done - {NUM_USERS} users created")
        print(f"      Segment distribution: {segment_counts}")

        # Generate 6 months of interactions
        print(f"\n[4/4] Generating {DAYS_OF_DATA} days of interactions...")
        print("      This will take a while...")

        total_interactions = 0
        start_date = datetime.now() - timedelta(days=DAYS_OF_DATA)

        interaction_type_counts = {}
        monthly_counts = {}

        for day_offset in range(DAYS_OF_DATA):
            current_date = start_date + timedelta(days=day_offset)
            month_key = current_date.strftime("%Y-%m")

            if day_offset % 30 == 0:
                month_num = day_offset // 30 + 1
                print(f"      Month {month_num}/6: Processing {current_date.strftime('%Y-%m')}...")

            daily_interactions = generate_daily_interactions(current_date, users, businesses)

            # Insert in batches
            batch_size = 500
            for i in range(0, len(daily_interactions), batch_size):
                batch = daily_interactions[i:i + batch_size]

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
                        interaction_type_counts[itype] = interaction_type_counts.get(itype, 0) + 1
                    except Exception:
                        pass  # Skip duplicates

                await db.commit()

            monthly_counts[month_key] = monthly_counts.get(month_key, 0) + len(daily_interactions)
            total_interactions += len(daily_interactions)

        await db.commit()

        # Final statistics
        print("\n" + "=" * 70)
        print("  DATA GENERATION COMPLETE")
        print("=" * 70)

        result = await db.execute(text("SELECT COUNT(*) FROM users"))
        user_count = result.scalar()

        result = await db.execute(text("SELECT COUNT(*) FROM businesses"))
        business_count = result.scalar()

        result = await db.execute(text("SELECT COUNT(*) FROM user_interactions"))
        interaction_count = result.scalar()

        print(f"\n  DATASET SUMMARY:")
        print(f"  ----------------")
        print(f"  Users:        {user_count:,}")
        print(f"  Businesses:   {business_count:,}")
        print(f"  Interactions: {interaction_count:,}")
        print(f"  Avg per user: {interaction_count/user_count:,.1f}")

        print(f"\n  INTERACTION BREAKDOWN:")
        for itype, count in sorted(interaction_type_counts.items(), key=lambda x: -x[1]):
            pct = count / sum(interaction_type_counts.values()) * 100
            print(f"    {itype:10}: {count:,} ({pct:.1f}%)")

        print(f"\n  MONTHLY ACTIVITY:")
        for month, count in sorted(monthly_counts.items()):
            print(f"    {month}: {count:,} interactions")

        print(f"\n  TIME RANGE:")
        print(f"    Start: {start_date.strftime('%Y-%m-%d')}")
        print(f"    End:   {datetime.now().strftime('%Y-%m-%d')}")
        print(f"    Days:  {DAYS_OF_DATA}")

        print(f"\n  TEST ENDPOINTS:")
        print(f"    curl http://localhost:8000/recommend/1")
        print(f"    curl http://localhost:8000/recommend/500")
        print(f"    curl http://localhost:8000/health")
        print(f"    http://localhost:8000/docs")

        print("\n" + "=" * 70)


async def main():
    """Entry point"""
    try:
        await generate_all_data()
    except KeyboardInterrupt:
        print("\n\nData generation interrupted")
    except Exception as e:
        print(f"\nError: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())
