#!/usr/bin/env python3
"""
Lightweight interaction generator - generates 6 months of interactions
for existing users and businesses with minimal memory footprint.
"""
import asyncio
import json
import random
import sys
import logging
from datetime import datetime, timedelta

# Disable SQLAlchemy logging to reduce noise
logging.getLogger('sqlalchemy.engine').setLevel(logging.WARNING)

sys.path.insert(0, '/app')

from app.database import AsyncSessionLocal
from sqlalchemy import text

# Configuration - reduced for memory efficiency
DAYS_OF_DATA = 180
INTERACTIONS_PER_DAY = 800  # Reduced from 1500-6000

async def generate_interactions():
    """Generate interactions for existing users/businesses"""
    print("=" * 60)
    print("  Interaction Generator - 6 months of data")
    print("=" * 60)

    async with AsyncSessionLocal() as db:
        # Get user and business counts
        result = await db.execute(text("SELECT COUNT(*) FROM users"))
        num_users = result.scalar()

        result = await db.execute(text("SELECT COUNT(*) FROM businesses"))
        num_businesses = result.scalar()

        print(f"\n  Found {num_users} users and {num_businesses} businesses")

        if num_users == 0 or num_businesses == 0:
            print("  ERROR: No users or businesses found. Run full generator first.")
            return

        # Clear existing interactions
        print("\n  Clearing existing interactions...")
        await db.execute(text("TRUNCATE TABLE user_interactions"))
        await db.commit()

        # Generate interactions
        print(f"\n  Generating {DAYS_OF_DATA} days of interactions...")
        start_date = datetime.now() - timedelta(days=DAYS_OF_DATA)
        total = 0
        interaction_counts = {"view": 0, "like": 0, "save": 0, "purchase": 0, "share": 0}

        for day_offset in range(DAYS_OF_DATA):
            current_date = start_date + timedelta(days=day_offset)

            # Vary daily count
            day_of_week = current_date.weekday()
            if day_of_week >= 5:  # Weekend
                daily_count = random.randint(int(INTERACTIONS_PER_DAY * 0.8), INTERACTIONS_PER_DAY)
            else:
                daily_count = random.randint(int(INTERACTIONS_PER_DAY * 0.5), int(INTERACTIONS_PER_DAY * 0.8))

            # Generate batch
            batch = []
            seen = set()

            for _ in range(daily_count):
                user_id = random.randint(1, num_users)
                business_id = random.randint(1, num_businesses)

                # Determine interaction type
                rand = random.random()
                if rand < 0.50:
                    itype, weight = "view", 1.0
                elif rand < 0.75:
                    itype, weight = "like", 2.0
                elif rand < 0.90:
                    itype, weight = "save", 3.0
                elif rand < 0.97:
                    itype, weight = "purchase", 5.0
                else:
                    itype, weight = "share", 4.0

                key = (user_id, business_id, itype)
                if key in seen:
                    continue
                seen.add(key)

                hour = random.randint(6, 23)
                minute = random.randint(0, 59)
                timestamp = current_date.replace(hour=hour, minute=minute, second=0, microsecond=0)

                batch.append({
                    "user_id": user_id,
                    "business_id": business_id,
                    "interaction_type": itype,
                    "weight": weight,
                    "timestamp": timestamp
                })
                interaction_counts[itype] += 1

            # Insert batch
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
                except Exception:
                    pass

            await db.commit()
            total += len(batch)

            if (day_offset + 1) % 30 == 0:
                print(f"    Month {(day_offset + 1) // 30}: {total:,} interactions")

        # Final commit
        await db.commit()

        # Get final count
        result = await db.execute(text("SELECT COUNT(*) FROM user_interactions"))
        final_count = result.scalar()

        print("\n" + "=" * 60)
        print("  COMPLETE")
        print("=" * 60)
        print(f"\n  Total interactions: {final_count:,}")
        print(f"\n  Breakdown:")
        for itype, count in sorted(interaction_counts.items(), key=lambda x: -x[1]):
            pct = count / sum(interaction_counts.values()) * 100
            print(f"    {itype:10}: {count:,} ({pct:.1f}%)")

        print(f"\n  Test: curl http://localhost:8000/recommend/1")
        print("=" * 60)


async def main():
    try:
        await generate_interactions()
    except KeyboardInterrupt:
        print("\nInterrupted")
    except Exception as e:
        print(f"\nError: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())
