#!/usr/bin/env python3
"""
Realistic data generator for recommendation engine testing
Simulates 6 months of user behavior with daily patterns
"""
import asyncio
import json
import random
import sys
from datetime import datetime, timedelta
from typing import List, Dict
import numpy as np

sys.path.insert(0, '/app')

from app.database import AsyncSessionLocal
from sqlalchemy import text

# ========== CONFIGURATION ==========
NUM_BUSINESSES = 500       # 500 different businesses
NUM_USERS = 1000           # 1000 active users
DAYS_OF_DATA = 180         # 6 months of historical data
MIN_INTERACTIONS_PER_DAY = 1000  # At least 1000 interactions daily
MAX_INTERACTIONS_PER_DAY = 5000  # Up to 5000 interactions daily

# Business categories with realistic distribution
CATEGORIES = {
    "restaurant": {"weight": 0.25, "subcategories": ["italian", "chinese", "mexican", "indian", "fast_food"]},
    "cafe": {"weight": 0.15, "subcategories": ["coffee", "tea", "pastry", "breakfast"]},
    "retail": {"weight": 0.20, "subcategories": ["clothing", "electronics", "home_goods", "beauty"]},
    "services": {"weight": 0.15, "subcategories": ["salon", "gym", "repair", "cleaning"]},
    "entertainment": {"weight": 0.10, "subcategories": ["movies", "games", "events", "parks"]},
    "grocery": {"weight": 0.15, "subcategories": ["supermarket", "organic", "convenience"]}
}

# User demographic segments
USER_SEGMENTS = {
    "young_adults": {"age_range": (18, 30), "weight": 0.35, "active_hours": [(18, 23), (12, 14)]},
    "professionals": {"age_range": (25, 45), "weight": 0.30, "active_hours": [(7, 9), (18, 20), (12, 13)]},
    "families": {"age_range": (30, 50), "weight": 0.25, "active_hours": [(16, 20), (10, 12)]},
    "retirees": {"age_range": (55, 75), "weight": 0.10, "active_hours": [(10, 16)]}
}

# Location clusters (simulating city neighborhoods)
LOCATIONS = [
    {"name": "downtown", "lat": 40.7128, "lon": -74.0060, "density": 0.40},
    {"name": "uptown", "lat": 40.8116, "lon": -73.9465, "density": 0.25},
    {"name": "brooklyn", "lat": 40.6782, "lon": -73.9442, "density": 0.20},
    {"name": "queens", "lat": 40.7282, "lon": -73.7949, "density": 0.15}
]

# ========== HELPER FUNCTIONS ==========
def weighted_choice(choices):
    """Choose based on weights"""
    total = sum(w for _, w in choices)
    r = random.uniform(0, total)
    upto = 0
    for item, weight in choices:
        if upto + weight >= r:
            return item
        upto += weight
    return choices[-1][0]

def generate_business_profile(business_id: int) -> Dict:
    """Generate realistic business profile"""
    category = weighted_choice([(cat, data["weight"]) for cat, data in CATEGORIES.items()])
    subcat = random.choice(CATEGORIES[category]["subcategories"])
    
    # Choose location based on density
    location = weighted_choice([(loc["name"], loc["density"]) for loc in LOCATIONS])
    loc_data = next(loc for loc in LOCATIONS if loc["name"] == location)
    
    # Add some randomness to location
    lat = loc_data["lat"] + random.uniform(-0.02, 0.02)
    lon = loc_data["lon"] + random.uniform(-0.02, 0.02)
    
    # Generate popularity score (some businesses are more popular)
    base_popularity = random.uniform(0.5, 1.0)
    trending_factor = random.uniform(0.8, 1.2)  # Some businesses are trending
    
    return {
        "id": business_id,
        "name": f"{subcat.capitalize()} {business_id}",
        "category": category,
        "subcategory": subcat,
        "full_categories": json.dumps([category, subcat]),
        "tags": json.dumps([category, subcat, "quality", "service"]),
        "location": json.dumps({"lat": lat, "lon": lon, "area": location}),
        "base_popularity": base_popularity,
        "trending_factor": trending_factor,
        "price_level": random.choice(["$", "$$", "$$$", "$$$$"]),
        "rating": round(random.uniform(3.0, 5.0), 1),
        "rating_count": random.randint(10, 5000)
    }

def generate_user_profile(user_id: int) -> Dict:
    """Generate realistic user profile"""
    segment = weighted_choice([(seg, data["weight"]) for seg, data in USER_SEGMENTS.items()])
    seg_data = USER_SEGMENTS[segment]
    
    # Generate user interests based on segment
    if segment == "young_adults":
        interests = random.sample(["cafe", "restaurant", "entertainment", "retail"], 3)
    elif segment == "professionals":
        interests = random.sample(["cafe", "restaurant", "services", "grocery"], 3)
    elif segment == "families":
        interests = random.sample(["grocery", "entertainment", "restaurant", "retail"], 3)
    else:  # retirees
        interests = random.sample(["grocery", "services", "cafe", "entertainment"], 3)
    
    # Choose location
    location = weighted_choice([(loc["name"], loc["density"]) for loc in LOCATIONS])
    loc_data = next(loc for loc in LOCATIONS if loc["name"] == location)
    
    # Add some randomness
    lat = loc_data["lat"] + random.uniform(-0.01, 0.01)
    lon = loc_data["lon"] + random.uniform(-0.01, 0.01)
    
    return {
        "id": user_id,
        "username": f"user_{user_id}",
        "email": f"user_{user_id}@test.com",
        "segment": segment,
        "interests": json.dumps(interests),
        "location": json.dumps({"lat": lat, "lon": lon, "area": location}),
        "active_hours": seg_data["active_hours"],
        "activity_level": random.uniform(0.3, 1.0),  # How active this user is
        "exploration_rate": random.uniform(0.1, 0.5)  # How likely to try new things
    }

def calculate_interaction_probability(user: Dict, business: Dict, time_of_day: int) -> float:
    """Calculate probability of user interacting with business"""
    probability = 1.0
    
    # 1. Location similarity (users prefer nearby businesses)
    user_loc = json.loads(user["location"])
    biz_loc = json.loads(business["location"])
    lat_diff = abs(user_loc["lat"] - biz_loc["lat"])
    lon_diff = abs(user_loc["lon"] - biz_loc["lon"])
    distance_factor = max(0, 1.0 - (lat_diff + lon_diff) * 100)  # Normalize
    
    # 2. Interest match
    user_interests = json.loads(user["interests"])
    biz_cats = json.loads(business["full_categories"])
    interest_match = len(set(user_interests) & set(biz_cats)) / max(len(user_interests), 1)
    
    # 3. Time of day factor (some businesses are more popular at certain times)
    if business["category"] == "cafe" and 7 <= time_of_day <= 10:
        time_factor = 2.0  # Morning coffee
    elif business["category"] == "restaurant" and 12 <= time_of_day <= 14:
        time_factor = 1.8  # Lunch
    elif business["category"] == "restaurant" and 18 <= time_of_day <= 21:
        time_factor = 2.2  # Dinner
    elif business["category"] == "entertainment" and 19 <= time_of_day <= 23:
        time_factor = 1.5  # Evening entertainment
    else:
        time_factor = 1.0
    
    # 4. Business popularity
    popularity_factor = business["base_popularity"] * business["trending_factor"]
    
    # 5. User activity level
    activity_factor = user["activity_level"]
    
    # Combine factors
    probability = (distance_factor * 0.3 + 
                  interest_match * 0.3 + 
                  popularity_factor * 0.2 + 
                  activity_factor * 0.2) * time_factor
    
    return min(max(probability, 0), 1)  # Clamp between 0 and 1

def generate_daily_interactions(date: datetime, users: List[Dict], businesses: List[Dict]) -> List[Dict]:
    """Generate interactions for a specific day"""
    interactions = []
    
    # Day of week effects
    day_of_week = date.weekday()
    if day_of_week >= 5:  # Weekend
        daily_interactions = random.randint(MAX_INTERACTIONS_PER_DAY // 2, MAX_INTERACTIONS_PER_DAY)
    else:  # Weekday
        daily_interactions = random.randint(MIN_INTERACTIONS_PER_DAY, MAX_INTERACTIONS_PER_DAY // 2)
    
    # Time patterns throughout the day
    time_slots = {
        "morning": (7, 12),
        "afternoon": (12, 17),
        "evening": (17, 22),
        "night": (22, 24)
    }
    
    # Generate interactions
    for _ in range(daily_interactions):
        # Select random user
        user = random.choice(users)
        
        # Select time based on user's active hours
        active_slots = []
        for start, end in user["active_hours"]:
            active_slots.append((start, end))
        
        if not active_slots:
            active_slots = [(9, 21)]  # Default if no active hours
        
        slot = random.choice(active_slots)
        hour = random.randint(slot[0], slot[1] - 1)
        minute = random.randint(0, 59)
        
        interaction_time = date.replace(hour=hour, minute=minute, second=0, microsecond=0)
        
        # Select business (weighted by probability)
        candidate_businesses = random.sample(businesses, min(50, len(businesses)))
        scored_businesses = []
        
        for business in candidate_businesses:
            score = calculate_interaction_probability(user, business, hour)
            # Add some randomness
            score *= random.uniform(0.8, 1.2)
            scored_businesses.append((business, score))
        
        # Select business with highest score
        if scored_businesses:
            scored_businesses.sort(key=lambda x: x[1], reverse=True)
            selected_business = scored_businesses[0][0]
            
            # Determine interaction type
            rand = random.random()
            if rand < 0.60:
                interaction_type = "view"
                weight = 1.0
            elif rand < 0.85:
                interaction_type = "like"
                weight = 2.0
            elif rand < 0.95:
                interaction_type = "save"
                weight = 3.0
            else:
                interaction_type = "purchase"
                weight = 5.0
            
            interactions.append({
                "user_id": user["id"],
                "business_id": selected_business["id"],
                "interaction_type": interaction_type,
                "weight": weight,
                "timestamp": interaction_time
            })
    
    return interactions

# ========== MAIN DATA GENERATION ==========
async def generate_all_data():
    """Generate complete dataset"""
    print("=" * 60)
    print("🚀 REALISTIC DATA GENERATOR FOR RECOMMENDATION ENGINE")
    print("=" * 60)
    
    async with AsyncSessionLocal() as db:
        # Clear existing data
        print("\n🗑️  Clearing existing data...")
        await db.execute(text("TRUNCATE TABLE user_interactions CASCADE"))
        await db.execute(text("TRUNCATE TABLE users CASCADE"))
        await db.execute(text("TRUNCATE TABLE businesses CASCADE"))
        await db.commit()
        print("✅ Cleared existing data")
        
        # ========== GENERATE BUSINESSES ==========
        print(f"\n🏪 Generating {NUM_BUSINESSES} businesses...")
        businesses = []
        
        for i in range(1, NUM_BUSINESSES + 1):
            biz = generate_business_profile(i)
            
            await db.execute(
                text("""
                INSERT INTO businesses 
                (name, categories, tags, location, popularity_score, rating, rating_count) 
                VALUES (:name, :categories, :tags, :location, :popularity, :rating, :rating_count)
                """),
                {
                    "name": biz["name"],
                    "categories": biz["full_categories"],
                    "tags": biz["tags"],
                    "location": biz["location"],
                    "popularity": biz["base_popularity"] * biz["trending_factor"] * 10,  # Scale to 1-10
                    "rating": biz["rating"],
                    "rating_count": biz["rating_count"]
                }
            )
            
            businesses.append(biz)
            
            if i % 100 == 0:
                print(f"  Generated {i}/{NUM_BUSINESSES} businesses")
                await db.commit()
        
        await db.commit()
        print(f"✅ Generated {NUM_BUSINESSES} businesses")
        
        # ========== GENERATE USERS ==========
        print(f"\n👥 Generating {NUM_USERS} users...")
        users = []
        
        for i in range(1, NUM_USERS + 1):
            user = generate_user_profile(i)
            
            await db.execute(
                text("""
                INSERT INTO users 
                (username, email, interests, location) 
                VALUES (:username, :email, :interests, :location)
                """),
                {
                    "username": user["username"],
                    "email": user["email"],
                    "interests": user["interests"],
                    "location": user["location"]
                }
            )
            
            users.append(user)
            
            if i % 200 == 0:
                print(f"  Generated {i}/{NUM_USERS} users")
                await db.commit()
        
        await db.commit()
        print(f"✅ Generated {NUM_USERS} users")
        
        # ========== GENERATE INTERACTIONS OVER TIME ==========
        print(f"\n📊 Generating {DAYS_OF_DATA} days of interactions...")
        print("  (This may take a few minutes)")
        
        total_interactions = 0
        start_date = datetime.now() - timedelta(days=DAYS_OF_DATA)
        
        for day_offset in range(DAYS_OF_DATA):
            current_date = start_date + timedelta(days=day_offset)
            
            if day_offset % 30 == 0:
                print(f"  Month {day_offset//30 + 1}: Generating day {day_offset + 1}/{DAYS_OF_DATA}")
            
            # Generate interactions for this day
            daily_interactions = generate_daily_interactions(current_date, users, businesses)
            
            # Insert in batches
            batch_size = 1000
            for i in range(0, len(daily_interactions), batch_size):
                batch = daily_interactions[i:i + batch_size]
                
                for interaction in batch:
                    await db.execute(
                        text("""
                        INSERT INTO user_interactions 
                        (user_id, business_id, interaction_type, weight, timestamp) 
                        VALUES (:user_id, :business_id, :interaction_type, :weight, :timestamp)
                        """),
                        interaction
                    )
                
                await db.commit()
            
            total_interactions += len(daily_interactions)
            
            # Update business popularity based on recent interactions
            if day_offset % 7 == 0:  # Update weekly
                await db.execute(
                    text("""
                    UPDATE businesses 
                    SET popularity_score = popularity_score * (0.95 + random() * 0.1)
                    WHERE random() < 0.3  # 30% of businesses change popularity each week
                    """)
                )
                await db.commit()
        
        await db.commit()
        print(f"✅ Generated {total_interactions:,} total interactions")
        
        # ========== FINAL STATISTICS ==========
        print("\n" + "=" * 60)
        print("📈 DATA GENERATION COMPLETE!")
        print("=" * 60)
        
        # Get final statistics
        result = await db.execute(text("SELECT COUNT(*) FROM users"))
        user_count = result.scalar()
        
        result = await db.execute(text("SELECT COUNT(*) FROM businesses"))
        business_count = result.scalar()
        
        result = await db.execute(text("SELECT COUNT(*) FROM user_interactions"))
        interaction_count = result.scalar()
        
        result = await db.execute(text("""
            SELECT 
                interaction_type,
                COUNT(*) as count,
                ROUND(COUNT(*) * 100.0 / (SELECT COUNT(*) FROM user_interactions), 2) as percentage
            FROM user_interactions 
            GROUP BY interaction_type 
            ORDER BY count DESC
        """))
        interaction_stats = result.fetchall()
        
        print(f"\n📊 DATASET STATISTICS:")
        print(f"   Users: {user_count:,}")
        print(f"   Businesses: {business_count:,}")
        print(f"   Interactions: {interaction_count:,}")
        print(f"   Avg interactions per user: {interaction_count/user_count:,.1f}")
        
        print(f"\n🔍 INTERACTION BREAKDOWN:")
        for row in interaction_stats:
            print(f"   {row[0]}: {row[1]:,} ({row[2]}%)")
        
        print(f"\n🎯 TEST YOUR RECOMMENDATION ENGINE:")
        print(f"   New user test:    curl http://localhost:8000/recommend/{NUM_USERS}")
        print(f"   Active user test: curl http://localhost:8000/recommend/1")
        print(f"   Diverse test:     curl http://localhost:8000/recommend/{NUM_USERS//2}")
        print(f"   API Docs:         http://localhost:8000/docs")
        
        print(f"\n📅 DATA TIMELINE:")
        print(f"   Time period: {DAYS_OF_DATA} days ({DAYS_OF_DATA//30} months)")
        print(f"   Start date: {start_date.strftime('%Y-%m-%d')}")
        print(f"   End date: {datetime.now().strftime('%Y-%m-%d')}")
        print(f"   Daily avg: {interaction_count/DAYS_OF_DATA:,.0f} interactions/day")
        
        print("\n" + "=" * 60)
        print("🚀 Ready for production-level testing!")
        print("=" * 60)

async def main():
    """Main function"""
    try:
        await generate_all_data()
    except KeyboardInterrupt:
        print("\n\n⚠️  Data generation interrupted by user")
    except Exception as e:
        print(f"\n❌ Error during data generation: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())
