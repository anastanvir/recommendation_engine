#!/usr/bin/env python3
"""
Test data generator for recommendation engine
"""
import asyncio
import json
import random
import sys
import os
from datetime import datetime, timedelta

# Fix Python path - add /app to sys.path
sys.path.insert(0, '/app')

try:
    from sqlalchemy.ext.asyncio import AsyncSession
    from sqlalchemy import text
    print("✓ SQLAlchemy imported")
except ImportError as e:
    print(f"✗ SQLAlchemy import error: {e}")
    sys.exit(1)

try:
    from app.database import AsyncSessionLocal
    print("✓ Database module imported")
except ImportError as e:
    print(f"✗ App module import error: {e}")
    print("Current sys.path:", sys.path)
    sys.exit(1)

# Business categories
CATEGORIES = [
    "restaurant", "cafe", "bar", "clothing", "electronics", 
    "grocery", "pharmacy", "salon", "gym", "bookstore",
    "jewelry", "home_decor", "pet_store", "hardware", "bakery"
]

async def generate_businesses(db: AsyncSession, count: int = 50):
    """Generate businesses"""
    print(f"Generating {count} businesses...")
    
    for i in range(count):
        biz_type = random.choice(CATEGORIES)
        business = {
            "name": f"{biz_type.capitalize()} {i+1}",
            "categories": json.dumps([biz_type]),
            "tags": json.dumps(["local", "popular"]),
            "location": json.dumps({
                "lat": 40.7128 + random.uniform(-0.05, 0.05),
                "lon": -74.0060 + random.uniform(-0.05, 0.05)
            }),
            "popularity_score": round(random.uniform(5.0, 9.9), 1),
            "rating": round(random.uniform(3.5, 5.0), 1),
            "rating_count": random.randint(10, 1000)
        }
        
        await db.execute(
            text("""
            INSERT INTO businesses 
            (name, categories, tags, location, popularity_score, rating, rating_count)
            VALUES (:name, :categories, :tags, :location, :popularity_score, :rating, :rating_count)
            """),
            business
        )
    
    await db.commit()
    print(f"✓ Generated {count} businesses")

async def generate_users(db: AsyncSession, count: int = 200):
    """Generate users"""
    print(f"Generating {count} users...")
    
    for i in range(count):
        interests = random.sample(CATEGORIES, random.randint(1, 4))
        user = {
            "username": f"user_{i+1}",
            "email": f"user_{i+1}@test.com",
            "interests": json.dumps(interests),
            "location": json.dumps({
                "lat": 40.7128 + random.uniform(-0.05, 0.05),
                "lon": -74.0060 + random.uniform(-0.05, 0.05)
            })
        }
        
        await db.execute(
            text("""
            INSERT INTO users 
            (username, email, interests, location)
            VALUES (:username, :email, :interests, :location)
            """),
            user
        )
    
    await db.commit()
    print(f"✓ Generated {count} users")

async def main():
    """Main function"""
    print("Starting test data generation...")
    
    async with AsyncSessionLocal() as db:
        # Clear existing data
        print("Clearing existing data...")
        try:
            await db.execute(text("TRUNCATE TABLE user_interactions CASCADE"))
            await db.execute(text("TRUNCATE TABLE users CASCADE"))
            await db.execute(text("TRUNCATE TABLE businesses CASCADE"))
            await db.commit()
            print("✓ Cleared existing data")
        except Exception as e:
            print(f"⚠ Could not clear data (might be first run): {e}")
            await db.rollback()
        
        # Generate new data
        await generate_businesses(db, 50)
        await generate_users(db, 200)
        
        # Verify counts
        result = await db.execute(text("SELECT COUNT(*) FROM users"))
        user_count = result.scalar()
        
        result = await db.execute(text("SELECT COUNT(*) FROM businesses"))
        biz_count = result.scalar()
        
        print(f"\n✅ Data generation complete!")
        print(f"   Users: {user_count}")
        print(f"   Businesses: {biz_count}")
        print(f"\nTest your recommendations:")
        print(f"   curl http://localhost:8000/recommend/1")
        print(f"   curl http://localhost:8000/recommend/2")

if __name__ == "__main__":
    asyncio.run(main())