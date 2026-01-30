#!/usr/bin/env python3
"""
Seed Data Generator for Recommendation Engine

Generates realistic marketplace data including:
- Businesses with categories, tags, ratings, and locations
- Users with interests and locations
- User interactions (views, likes, saves, purchases, shares)

Usage:
    docker compose exec recommender python scripts/seed_data.py

    Or with custom counts:
    docker compose exec recommender python scripts/seed_data.py --businesses 200 --users 500 --days 90
"""
import argparse
import asyncio
import json
import random
import sys
from datetime import datetime, timedelta

sys.path.insert(0, '/app')

from app.database import AsyncSessionLocal
from sqlalchemy import text

# =============================================================================
# CONFIGURATION
# =============================================================================

DEFAULT_NUM_BUSINESSES = 100
DEFAULT_NUM_USERS = 200
DEFAULT_DAYS_OF_DATA = 30

INTERACTION_TYPES = {
    'view': 1.0,
    'like': 2.0,
    'save': 3.0,
    'purchase': 5.0,
    'share': 4.0,
}

# =============================================================================
# BUSINESS DATA
# =============================================================================

BUSINESS_CATEGORIES = {
    'restaurant': {
        'weight': 0.20,
        'tags': ['dine_in', 'takeout', 'delivery', 'reservations', 'outdoor_seating'],
        'names': ['Bistro', 'Kitchen', 'Grill', 'Eatery', 'Table', 'Cafe'],
    },
    'cafe': {
        'weight': 0.15,
        'tags': ['coffee', 'wifi', 'pastries', 'breakfast', 'cozy'],
        'names': ['Coffee House', 'Brew', 'Roasters', 'Bean', 'Cup'],
    },
    'fitness': {
        'weight': 0.12,
        'tags': ['gym', 'yoga', 'personal_training', '24_hour', 'classes'],
        'names': ['Fitness', 'Gym', 'Studio', 'Wellness Center', 'Athletic Club'],
    },
    'retail': {
        'weight': 0.15,
        'tags': ['clothing', 'accessories', 'shoes', 'trending', 'sale'],
        'names': ['Boutique', 'Shop', 'Store', 'Fashion', 'Outlet'],
    },
    'beauty': {
        'weight': 0.10,
        'tags': ['salon', 'spa', 'nails', 'hair', 'skincare'],
        'names': ['Beauty Bar', 'Salon', 'Spa', 'Studio', 'Lounge'],
    },
    'tech': {
        'weight': 0.08,
        'tags': ['electronics', 'repair', 'gadgets', 'accessories', 'service'],
        'names': ['Tech', 'Digital', 'Electronics', 'Gadget', 'Device'],
    },
    'health': {
        'weight': 0.10,
        'tags': ['pharmacy', 'clinic', 'wellness', 'vitamins', 'organic'],
        'names': ['Health', 'Wellness', 'Care', 'Medical', 'Pharmacy'],
    },
    'entertainment': {
        'weight': 0.10,
        'tags': ['movies', 'games', 'events', 'nightlife', 'live_music'],
        'names': ['Entertainment', 'Arcade', 'Lounge', 'Club', 'Theater'],
    },
}

LOCATIONS = [
    {'name': 'Downtown', 'lat': 40.7128, 'lon': -74.0060},
    {'name': 'Midtown', 'lat': 40.7549, 'lon': -73.9840},
    {'name': 'Uptown', 'lat': 40.7831, 'lon': -73.9712},
    {'name': 'Brooklyn', 'lat': 40.6782, 'lon': -73.9442},
    {'name': 'Queens', 'lat': 40.7282, 'lon': -73.7949},
]

ADJECTIVES = ['Urban', 'Metro', 'City', 'Local', 'Premier', 'Elite', 'Golden', 'Silver', 'Blue', 'Green']

# =============================================================================
# USER DATA
# =============================================================================

USER_SEGMENTS = {
    'foodie': {
        'weight': 0.25,
        'interests': ['restaurant', 'cafe'],
    },
    'fitness_enthusiast': {
        'weight': 0.20,
        'interests': ['fitness', 'health'],
    },
    'shopper': {
        'weight': 0.20,
        'interests': ['retail', 'beauty'],
    },
    'tech_savvy': {
        'weight': 0.15,
        'interests': ['tech', 'entertainment'],
    },
    'wellness_seeker': {
        'weight': 0.20,
        'interests': ['health', 'beauty', 'fitness'],
    },
}

FIRST_NAMES = ['Alex', 'Sam', 'Jordan', 'Taylor', 'Morgan', 'Casey', 'Riley', 'Quinn', 'Avery', 'Blake']
LAST_NAMES = ['Smith', 'Johnson', 'Williams', 'Brown', 'Jones', 'Garcia', 'Miller', 'Davis', 'Wilson', 'Lee']


# =============================================================================
# HELPER FUNCTIONS
# =============================================================================

def weighted_choice(choices: list) -> any:
    """Select from list of (item, weight) tuples."""
    total = sum(w for _, w in choices)
    r = random.uniform(0, total)
    cumulative = 0
    for item, weight in choices:
        cumulative += weight
        if r <= cumulative:
            return item
    return choices[-1][0]


def generate_business(business_id: int) -> dict:
    """Generate a single business record."""
    category = weighted_choice([(k, v['weight']) for k, v in BUSINESS_CATEGORIES.items()])
    cat_data = BUSINESS_CATEGORIES[category]

    adjective = random.choice(ADJECTIVES)
    name_suffix = random.choice(cat_data['names'])
    name = f"{adjective} {name_suffix}"

    location = random.choice(LOCATIONS)
    lat = location['lat'] + random.uniform(-0.02, 0.02)
    lon = location['lon'] + random.uniform(-0.02, 0.02)

    tags = random.sample(cat_data['tags'], min(3, len(cat_data['tags'])))
    rating = round(random.uniform(3.5, 5.0), 1)
    popularity = round(random.uniform(5.0, 10.0), 1)

    return {
        'id': business_id,
        'name': f"{name} #{business_id}",
        'description': f"A great {category} place in {location['name']}",
        'categories': [category],
        'tags': tags,
        'location': {'lat': lat, 'lon': lon, 'area': location['name']},
        'rating': rating,
        'rating_count': random.randint(10, 500),
        'popularity_score': popularity,
    }


def generate_user(user_id: int) -> dict:
    """Generate a single user record."""
    segment = weighted_choice([(k, v['weight']) for k, v in USER_SEGMENTS.items()])
    seg_data = USER_SEGMENTS[segment]

    first = random.choice(FIRST_NAMES)
    last = random.choice(LAST_NAMES)
    username = f"{first.lower()}_{last.lower()}_{user_id}"
    email = f"{username}@example.com"

    location = random.choice(LOCATIONS)
    lat = location['lat'] + random.uniform(-0.02, 0.02)
    lon = location['lon'] + random.uniform(-0.02, 0.02)

    return {
        'id': user_id,
        'username': username,
        'email': email,
        'interests': seg_data['interests'],
        'location': {'lat': lat, 'lon': lon},
        'segment': segment,
    }


def generate_interactions(users: list, businesses: list, days: int) -> list:
    """Generate realistic user interactions."""
    interactions = []
    start_date = datetime.now() - timedelta(days=days)

    # Build category lookup for businesses
    biz_by_category = {}
    for biz in businesses:
        for cat in biz['categories']:
            if cat not in biz_by_category:
                biz_by_category[cat] = []
            biz_by_category[cat].append(biz)

    seen = set()

    for day in range(days):
        current_date = start_date + timedelta(days=day)
        daily_count = random.randint(len(users) // 2, len(users) * 2)

        for _ in range(daily_count):
            user = random.choice(users)

            # Prefer businesses matching user interests
            if random.random() < 0.7 and user['interests']:
                interest = random.choice(user['interests'])
                if interest in biz_by_category and biz_by_category[interest]:
                    business = random.choice(biz_by_category[interest])
                else:
                    business = random.choice(businesses)
            else:
                business = random.choice(businesses)

            # Determine interaction type (views most common)
            r = random.random()
            if r < 0.60:
                itype = 'view'
            elif r < 0.80:
                itype = 'like'
            elif r < 0.90:
                itype = 'save'
            elif r < 0.97:
                itype = 'share'
            else:
                itype = 'purchase'

            # Unique constraint: user_id, business_id, interaction_type
            key = (user['id'], business['id'], itype)
            if key in seen:
                continue
            seen.add(key)

            timestamp = current_date.replace(
                hour=random.randint(8, 22),
                minute=random.randint(0, 59),
                second=random.randint(0, 59),
            )

            interactions.append({
                'user_id': user['id'],
                'business_id': business['id'],
                'interaction_type': itype,
                'weight': INTERACTION_TYPES[itype],
                'timestamp': timestamp,
            })

    return interactions


# =============================================================================
# MAIN SEEDING FUNCTION
# =============================================================================

async def seed_database(num_businesses: int, num_users: int, days: int):
    """Main function to seed the database."""
    print("=" * 60)
    print("  Recommendation Engine - Data Seeder")
    print("=" * 60)
    print(f"\n  Config: {num_businesses} businesses, {num_users} users, {days} days")

    async with AsyncSessionLocal() as db:
        try:
            # Step 1: Clear existing data and reset sequences
            print("\n[1/4] Clearing existing data...")
            await db.execute(text("TRUNCATE TABLE user_interactions RESTART IDENTITY CASCADE"))
            await db.execute(text("TRUNCATE TABLE users RESTART IDENTITY CASCADE"))
            await db.execute(text("TRUNCATE TABLE businesses RESTART IDENTITY CASCADE"))
            await db.commit()
            print("      Done")

            # Step 2: Generate and insert businesses
            print(f"\n[2/4] Generating {num_businesses} businesses...")
            businesses = []
            for i in range(1, num_businesses + 1):
                biz = generate_business(i)
                businesses.append(biz)

                await db.execute(
                    text("""
                        INSERT INTO businesses
                        (name, description, categories, tags, location, popularity_score, rating, rating_count)
                        VALUES (:name, :description, :categories, :tags, :location, :popularity_score, :rating, :rating_count)
                    """),
                    {
                        'name': biz['name'],
                        'description': biz['description'],
                        'categories': json.dumps(biz['categories']),
                        'tags': json.dumps(biz['tags']),
                        'location': json.dumps(biz['location']),
                        'popularity_score': biz['popularity_score'],
                        'rating': biz['rating'],
                        'rating_count': biz['rating_count'],
                    }
                )

                if i % 50 == 0:
                    await db.commit()
                    print(f"      {i}/{num_businesses} businesses created")

            await db.commit()
            print(f"      Done - {num_businesses} businesses created")

            # Step 3: Generate and insert users
            print(f"\n[3/4] Generating {num_users} users...")
            users = []
            for i in range(1, num_users + 1):
                user = generate_user(i)
                users.append(user)

                await db.execute(
                    text("""
                        INSERT INTO users (username, email, interests, location)
                        VALUES (:username, :email, :interests, :location)
                    """),
                    {
                        'username': user['username'],
                        'email': user['email'],
                        'interests': json.dumps(user['interests']),
                        'location': json.dumps(user['location']),
                    }
                )

                if i % 100 == 0:
                    await db.commit()
                    print(f"      {i}/{num_users} users created")

            await db.commit()
            print(f"      Done - {num_users} users created")

            # Step 4: Generate and insert interactions
            print(f"\n[4/4] Generating interactions for {days} days...")
            interactions = generate_interactions(users, businesses, days)
            print(f"      Generated {len(interactions)} interactions")

            batch_size = 500
            for i in range(0, len(interactions), batch_size):
                batch = interactions[i:i + batch_size]

                for interaction in batch:
                    await db.execute(
                        text("""
                            INSERT INTO user_interactions
                            (user_id, business_id, interaction_type, weight, timestamp)
                            VALUES (:user_id, :business_id, :interaction_type, :weight, :timestamp)
                            ON CONFLICT (user_id, business_id, interaction_type) DO NOTHING
                        """),
                        interaction
                    )

                await db.commit()

                if (i + batch_size) % 2000 == 0 or i + batch_size >= len(interactions):
                    print(f"      {min(i + batch_size, len(interactions))}/{len(interactions)} interactions inserted")

            print(f"      Done - {len(interactions)} interactions created")

            # Final summary
            print("\n" + "=" * 60)
            print("  SEEDING COMPLETE")
            print("=" * 60)

            result = await db.execute(text("SELECT COUNT(*) FROM businesses"))
            biz_count = result.scalar()

            result = await db.execute(text("SELECT COUNT(*) FROM users"))
            user_count = result.scalar()

            result = await db.execute(text("SELECT COUNT(*) FROM user_interactions"))
            interaction_count = result.scalar()

            print(f"\n  Summary:")
            print(f"    Businesses:   {biz_count:,}")
            print(f"    Users:        {user_count:,}")
            print(f"    Interactions: {interaction_count:,}")
            print(f"    Avg per user: {interaction_count/user_count:.1f}")
            print()

        except Exception as e:
            await db.rollback()
            print(f"\n  ERROR: {e}")
            print("  Database rolled back.")
            raise


def main():
    parser = argparse.ArgumentParser(description='Seed the recommendation engine database')
    parser.add_argument('--businesses', type=int, default=DEFAULT_NUM_BUSINESSES,
                        help=f'Number of businesses (default: {DEFAULT_NUM_BUSINESSES})')
    parser.add_argument('--users', type=int, default=DEFAULT_NUM_USERS,
                        help=f'Number of users (default: {DEFAULT_NUM_USERS})')
    parser.add_argument('--days', type=int, default=DEFAULT_DAYS_OF_DATA,
                        help=f'Days of interaction data (default: {DEFAULT_DAYS_OF_DATA})')

    args = parser.parse_args()
    asyncio.run(seed_database(args.businesses, args.users, args.days))


if __name__ == "__main__":
    main()
