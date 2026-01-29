# HTI Super App - Recommendation Engine Improvements

This document outlines suggested improvements for the recommendation engine to better support the HTI super app (social marketplace combining Facebook, Reddit, Twitter, Threads + marketplace + events + services).

## Current State Analysis

The existing recommendation engine provides:
- Content-based filtering using category/tag matching
- Location-based bonus scoring
- Popularity score boost
- Redis caching with configurable TTL

## Recommended Improvements

### 1. Interaction-Weighted Scoring (High Priority)

**Current Issue:** The algorithm fetches user interactions but doesn't effectively use the weights.

**Improvement:**
```python
# Calculate weighted interaction score per business
interaction_weights = {}
for interaction in interactions:
    biz_id = interaction.business_id
    if biz_id not in interaction_weights:
        interaction_weights[biz_id] = 0
    interaction_weights[biz_id] += interaction.weight

# Apply interaction boost to scoring
interaction_bonus = interaction_weights.get(business.id, 0) * 0.05
```

### 2. Time Decay Function (High Priority)

**Current Issue:** All interactions are treated equally regardless of age.

**Improvement:**
```python
from datetime import datetime, timedelta
import math

def time_decay_weight(timestamp, half_life_days=14):
    """Exponential decay - interactions lose half their weight every 14 days"""
    age_days = (datetime.now(timestamp.tzinfo) - timestamp).days
    return math.exp(-0.693 * age_days / half_life_days)
```

### 3. Content Type Diversity (Medium Priority)

**Current Issue:** Feed may be dominated by one content type.

**Improvement:** Implement diversity scoring to ensure mix of:
- Shops/Products (20-30%)
- Events (15-20%)
- Content Creators (15-20%)
- Services (15-20%)
- Communities (10-15%)
- Local Discovery (10-15%)

```python
# Diversify by business type
type_quotas = {
    "marketplace": 0.25,
    "events": 0.15,
    "creator": 0.15,
    "services": 0.20,
    "community": 0.15,
    "local": 0.10,
}
```

### 4. Collaborative Filtering (Medium Priority)

**Current Issue:** Only uses content-based filtering.

**Improvement:** Add user-to-user similarity:
```python
# Find similar users based on interaction patterns
# "Users who liked X also liked Y"
```

### 5. Trending/Viral Content (Medium Priority)

**For social features:**
```python
# Calculate trending score based on recent interaction velocity
def calculate_trending_score(business_id, hours=24):
    recent_interactions = get_interactions_since(business_id, hours)
    velocity = len(recent_interactions) / hours
    return velocity * recency_bonus
```

### 6. Event Time Proximity (High Priority)

**Current Issue:** Events don't consider timing.

**Improvement:**
```python
# Boost events happening soon
def event_time_bonus(event_date):
    days_until = (event_date - datetime.now()).days
    if 0 <= days_until <= 3:
        return 0.5  # High boost for imminent events
    elif 3 < days_until <= 7:
        return 0.3
    elif 7 < days_until <= 14:
        return 0.2
    return 0.1
```

### 7. API Enhancements (High Priority)

Add new endpoints and parameters:

```python
# Filter by business type
@app.get("/recommend/{user_id}")
async def get_recommendations(
    user_id: int,
    content_type: Optional[str] = None,  # marketplace, events, creator, etc.
    category: Optional[str] = None,
    exclude_seen: bool = True,
    time_range: Optional[str] = None,  # for events: today, this_week, this_month
    page: int = 1,
    page_size: int = 20,
    ...
)

# Trending endpoint
@app.get("/trending")
async def get_trending(
    content_type: Optional[str] = None,
    location: Optional[str] = None,
    time_range: str = "24h",  # 1h, 6h, 24h, 7d
    ...
)

# Similar items endpoint
@app.get("/similar/{business_id}")
async def get_similar(business_id: int, limit: int = 10)

# For You feed (mixed content)
@app.get("/feed/{user_id}")
async def get_feed(user_id: int, page: int = 1)
```

### 8. Database Schema Additions

```sql
-- Add metadata for events
ALTER TABLE businesses ADD COLUMN event_date TIMESTAMP WITH TIME ZONE;
ALTER TABLE businesses ADD COLUMN event_end_date TIMESTAMP WITH TIME ZONE;
ALTER TABLE businesses ADD COLUMN is_virtual BOOLEAN DEFAULT FALSE;

-- Add follower count for creators
ALTER TABLE businesses ADD COLUMN follower_count INTEGER DEFAULT 0;

-- Add price range for marketplace
ALTER TABLE businesses ADD COLUMN price_min DECIMAL(10,2);
ALTER TABLE businesses ADD COLUMN price_max DECIMAL(10,2);

-- Add business hours
ALTER TABLE businesses ADD COLUMN operating_hours JSONB;

-- User social graph
CREATE TABLE user_follows (
    follower_id INTEGER REFERENCES users(id),
    following_id INTEGER REFERENCES users(id),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (follower_id, following_id)
);

-- User saved/bookmarks
CREATE TABLE user_bookmarks (
    user_id INTEGER REFERENCES users(id),
    business_id INTEGER REFERENCES businesses(id),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (user_id, business_id)
);
```

### 9. Caching Strategy Improvements

```python
# Tiered caching
CACHE_TIERS = {
    "trending": 60,          # 1 minute for trending
    "recommendations": 300,  # 5 minutes for personalized
    "business_details": 900, # 15 minutes for static content
    "user_features": 3600,   # 1 hour for computed features
}

# Cache invalidation on interaction
async def on_user_interaction(user_id, business_id):
    await redis_manager.invalidate_user_cache(user_id)
    await redis_manager.update_trending(business_id)
```

### 10. Analytics & A/B Testing

```python
# Log recommendation events for analysis
@app.get("/recommend/{user_id}")
async def get_recommendations(...):
    recommendations = await generate_recommendations(...)

    # Log for analytics
    await log_recommendation_event(
        user_id=user_id,
        algorithm_version="v1.1",
        experiment_group="control",
        recommendations=[r["business_id"] for r in recommendations],
        context=context_dict
    )

    return recommendations
```

### 11. Real-time Features

For a social super app, consider:
- WebSocket connections for live updates
- Push notifications for trending in your area
- Real-time event updates

## Implementation Priority

| Priority | Feature | Effort | Impact |
|----------|---------|--------|--------|
| 1 | Interaction-weighted scoring | Low | High |
| 2 | Time decay function | Low | High |
| 3 | API enhancements (filters, pagination) | Medium | High |
| 4 | Event time proximity | Low | Medium |
| 5 | Content type diversity | Medium | Medium |
| 6 | Trending endpoint | Medium | High |
| 7 | Collaborative filtering | High | High |
| 8 | Database schema additions | Medium | Medium |
| 9 | Analytics & A/B testing | Medium | Medium |
| 10 | Real-time features | High | Medium |

## Quick Wins

1. Add interaction weight usage to scoring
2. Implement time decay
3. Add content type filter to API
4. Add pagination support
5. Create trending endpoint

## Testing the Data

Use the generated test data:

```bash
# Generate 6 months of data
make hti-data

# Or run directly
docker-compose exec recommender python scripts/hti_social_marketplace_generator.py

# Quick seed for testing
docker-compose exec postgres psql -U recommender -d recommender_db -f /app/scripts/hti_seed_data.sql

# Test recommendations
curl http://localhost:8000/recommend/1
curl http://localhost:8000/recommend/500
curl "http://localhost:8000/recommend/1?max_results=20"
```
