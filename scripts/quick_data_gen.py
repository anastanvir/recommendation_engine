#!/usr/bin/env python3
import asyncio
import json
import random
import sys

# Fix path
sys.path.insert(0, '/app')

# Import after fixing path
from app.database import AsyncSessionLocal
from sqlalchemy import text

async def main():
    print("Quick data generator starting...")
    
    async with AsyncSessionLocal() as db:
        # Simple data
        categories = ['restaurant', 'cafe', 'electronics', 'clothing']
        
        # Businesses
        for i in range(30):
            cat = random.choice(categories)
            await db.execute(
                text('INSERT INTO businesses (name, categories) VALUES (:name, :cat)'),
                {'name': f'{cat.capitalize()} Place {i+1}', 'cat': json.dumps([cat])}
            )
        
        # Users
        for i in range(100):
            interests = random.sample(categories, 2)
            await db.execute(
                text('INSERT INTO users (username, interests) VALUES (:user, :interests)'),
                {'user': f'user_{i+1}', 'interests': json.dumps(interests)}
            )
        
        await db.commit()
        print("✅ Generated 30 businesses and 100 users")

if __name__ == "__main__":
    asyncio.run(main())
