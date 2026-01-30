# Project Structure

## Overview

This is a standalone **Recommendation Engine** microservice built with FastAPI. It's designed to run independently and communicate with your Django backend (XO Black) via REST API.

```
recommendation_engine/
├── app/                        # Main application code
│   ├── __init__.py
│   ├── main.py                 # FastAPI routes & recommendation logic
│   ├── config.py               # Environment configuration
│   ├── models.py               # SQLAlchemy ORM models
│   ├── database.py             # Async database connection
│   └── redis_client.py         # Redis cache manager
│
├── scripts/
│   └── seed_data.py            # Database seeder for test data
│
├── docker-compose.yml          # Container orchestration
├── Dockerfile                  # Container build instructions
├── Makefile                    # Development commands
├── init-db.sql                 # Database schema initialization
├── pyproject.toml              # Python dependencies (UV)
├── .env                        # Local environment variables
├── .env.docker                 # Docker environment variables
├── CLAUDE.md                   # AI assistant instructions
└── STRUCTURE.md                # This file
```

---

## File Purposes

### `/app` - Application Code

| File | Purpose |
|------|---------|
| `main.py` | FastAPI application entry point. Contains all API routes (`/recommend/{user_id}`, `/health`, etc.) and the recommendation algorithm logic. |
| `config.py` | Centralized configuration using environment variables. Database URLs, Redis settings, cache TTL, etc. |
| `models.py` | SQLAlchemy ORM models: `User`, `Business`, `UserInteraction`. Defines database schema. |
| `database.py` | Async database engine setup using `asyncpg`. Connection pooling and session management. |
| `redis_client.py` | Redis singleton manager for caching recommendations and user features. |

### `/scripts` - Utilities

| File | Purpose |
|------|---------|
| `seed_data.py` | Generates test data (businesses, users, interactions). Run with `make seed`. |

### Root Files

| File | Purpose |
|------|---------|
| `docker-compose.yml` | Defines 3 services: `recommender` (FastAPI), `postgres` (database), `redis` (cache) |
| `Dockerfile` | Builds the FastAPI container with UV package manager |
| `Makefile` | Shortcuts: `make up`, `make seed`, `make logs`, etc. |
| `init-db.sql` | Creates database tables, indexes, and triggers on first startup |
| `pyproject.toml` | Python dependencies managed by UV |
| `.env` / `.env.docker` | Environment variables for local and Docker environments |

---

## Django Integration Guide

### Architecture

```
┌─────────────────────┐         HTTP/REST          ┌──────────────────────┐
│                     │ ◄──────────────────────────►│                      │
│   XO Black Django   │                            │  Recommendation      │
│   (Main Backend)    │   POST /sync/user          │  Engine (FastAPI)    │
│                     │   POST /sync/business      │                      │
│   Port: 8001        │   POST /interaction        │  Port: 8000          │
│                     │   GET  /recommend/{id}     │                      │
└─────────────────────┘                            └──────────────────────┘
         │                                                   │
         │                                                   │
         ▼                                                   ▼
┌─────────────────────┐                            ┌──────────────────────┐
│  Django Database    │                            │  Recommender DB      │
│  (PostgreSQL)       │                            │  (PostgreSQL)        │
└─────────────────────┘                            └──────────────────────┘
```

### Option 1: REST API Integration (Recommended)

Django calls the recommendation engine via HTTP requests.

#### Step 1: Add API endpoints to Recommendation Engine

Add these endpoints to `app/main.py`:

```python
from pydantic import BaseModel
from typing import List, Optional

# Request models
class UserSync(BaseModel):
    id: int
    username: str
    email: str
    interests: List[str] = []
    location: Optional[dict] = None

class BusinessSync(BaseModel):
    id: int
    name: str
    description: Optional[str] = None
    categories: List[str] = []
    tags: List[str] = []
    location: Optional[dict] = None
    popularity_score: float = 0.0
    rating: float = 0.0

class InteractionCreate(BaseModel):
    user_id: int
    business_id: int
    interaction_type: str  # view, like, save, purchase, share
    weight: float = 1.0

# Sync endpoints
@app.post("/sync/user")
async def sync_user(user: UserSync, db: AsyncSession = Depends(get_db_session)):
    """Sync user from Django to recommendation engine"""
    await db.execute(
        text("""
            INSERT INTO users (id, username, email, interests, location)
            VALUES (:id, :username, :email, :interests, :location)
            ON CONFLICT (id) DO UPDATE SET
                username = EXCLUDED.username,
                email = EXCLUDED.email,
                interests = EXCLUDED.interests,
                location = EXCLUDED.location,
                updated_at = CURRENT_TIMESTAMP
        """),
        {
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "interests": json.dumps(user.interests),
            "location": json.dumps(user.location) if user.location else None,
        }
    )
    await db.commit()
    return {"status": "synced", "user_id": user.id}

@app.post("/sync/business")
async def sync_business(business: BusinessSync, db: AsyncSession = Depends(get_db_session)):
    """Sync business from Django to recommendation engine"""
    await db.execute(
        text("""
            INSERT INTO businesses (id, name, description, categories, tags, location, popularity_score, rating)
            VALUES (:id, :name, :description, :categories, :tags, :location, :popularity_score, :rating)
            ON CONFLICT (id) DO UPDATE SET
                name = EXCLUDED.name,
                description = EXCLUDED.description,
                categories = EXCLUDED.categories,
                tags = EXCLUDED.tags,
                location = EXCLUDED.location,
                popularity_score = EXCLUDED.popularity_score,
                rating = EXCLUDED.rating,
                updated_at = CURRENT_TIMESTAMP
        """),
        {
            "id": business.id,
            "name": business.name,
            "description": business.description,
            "categories": json.dumps(business.categories),
            "tags": json.dumps(business.tags),
            "location": json.dumps(business.location) if business.location else None,
            "popularity_score": business.popularity_score,
            "rating": business.rating,
        }
    )
    await db.commit()
    return {"status": "synced", "business_id": business.id}

@app.post("/interaction")
async def record_interaction(interaction: InteractionCreate, db: AsyncSession = Depends(get_db_session)):
    """Record user interaction from Django"""
    await db.execute(
        text("""
            INSERT INTO user_interactions (user_id, business_id, interaction_type, weight)
            VALUES (:user_id, :business_id, :interaction_type, :weight)
            ON CONFLICT (user_id, business_id, interaction_type)
            DO UPDATE SET weight = EXCLUDED.weight, timestamp = CURRENT_TIMESTAMP
        """),
        {
            "user_id": interaction.user_id,
            "business_id": interaction.business_id,
            "interaction_type": interaction.interaction_type,
            "weight": interaction.weight,
        }
    )
    await db.commit()

    # Invalidate user's recommendation cache
    await redis_manager.cache_delete(f"recs:{interaction.user_id}:*")

    return {"status": "recorded"}
```

#### Step 2: Create Django client service

In your Django project, create `services/recommendation.py`:

```python
import httpx
from django.conf import settings

RECOMMENDATION_URL = getattr(settings, 'RECOMMENDATION_ENGINE_URL', 'http://localhost:8000')

class RecommendationService:
    """Client for the Recommendation Engine microservice"""

    def __init__(self):
        self.base_url = RECOMMENDATION_URL
        self.timeout = 10.0

    async def get_recommendations(self, user_id: int, max_results: int = 10) -> list:
        """Get personalized recommendations for a user"""
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.base_url}/recommend/{user_id}",
                params={"max_results": max_results},
                timeout=self.timeout
            )
            response.raise_for_status()
            return response.json()["recommendations"]

    async def sync_user(self, user) -> dict:
        """Sync Django user to recommendation engine"""
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.base_url}/sync/user",
                json={
                    "id": user.id,
                    "username": user.username,
                    "email": user.email,
                    "interests": user.interests or [],
                    "location": user.location,
                },
                timeout=self.timeout
            )
            response.raise_for_status()
            return response.json()

    async def sync_business(self, business) -> dict:
        """Sync Django business to recommendation engine"""
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.base_url}/sync/business",
                json={
                    "id": business.id,
                    "name": business.name,
                    "description": business.description,
                    "categories": business.categories or [],
                    "tags": business.tags or [],
                    "location": business.location,
                    "popularity_score": business.popularity_score,
                    "rating": business.rating,
                },
                timeout=self.timeout
            )
            response.raise_for_status()
            return response.json()

    async def record_interaction(self, user_id: int, business_id: int,
                                  interaction_type: str, weight: float = 1.0) -> dict:
        """Record user interaction"""
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.base_url}/interaction",
                json={
                    "user_id": user_id,
                    "business_id": business_id,
                    "interaction_type": interaction_type,
                    "weight": weight,
                },
                timeout=self.timeout
            )
            response.raise_for_status()
            return response.json()

# Singleton instance
recommendation_service = RecommendationService()
```

#### Step 3: Use Django signals for auto-sync

```python
# signals.py
from django.db.models.signals import post_save
from django.dispatch import receiver
from asgiref.sync import async_to_sync
from .models import User, Business
from .services.recommendation import recommendation_service

@receiver(post_save, sender=User)
def sync_user_to_recommendations(sender, instance, **kwargs):
    """Auto-sync user changes to recommendation engine"""
    try:
        async_to_sync(recommendation_service.sync_user)(instance)
    except Exception as e:
        # Log error but don't block the save
        print(f"Failed to sync user {instance.id}: {e}")

@receiver(post_save, sender=Business)
def sync_business_to_recommendations(sender, instance, **kwargs):
    """Auto-sync business changes to recommendation engine"""
    try:
        async_to_sync(recommendation_service.sync_business)(instance)
    except Exception as e:
        print(f"Failed to sync business {instance.id}: {e}")
```

#### Step 4: Django settings

```python
# settings.py
RECOMMENDATION_ENGINE_URL = "http://localhost:8000"  # or Docker service name
```

---

### Option 2: Shared Database (Simpler but less scalable)

Both Django and the recommendation engine use the same PostgreSQL database.

#### Pros:
- No data sync needed
- Simpler setup

#### Cons:
- Tight coupling
- Can't scale independently
- Schema conflicts possible

#### Setup:
1. Point both services to the same database URL
2. Use Django migrations for schema management
3. Recommendation engine reads from Django tables

---

### Option 3: Message Queue (Production-ready)

Use Redis/RabbitMQ for async communication.

```
Django → Redis Queue → Recommendation Engine
         (events)      (consumes & processes)
```

This is more complex but better for high-traffic production systems.

---

## Quick Start with Django

1. **Start the recommendation engine:**
   ```bash
   cd recommendation_engine
   make up
   make seed
   ```

2. **Add to Django docker-compose (if using Docker):**
   ```yaml
   services:
     django:
       environment:
         - RECOMMENDATION_ENGINE_URL=http://recommender:8000
       depends_on:
         - recommender

     recommender:
       build: ../recommendation_engine
       ports:
         - "8000:8000"
   ```

3. **Test the connection:**
   ```python
   # Django shell
   from services.recommendation import recommendation_service
   import asyncio

   # Get recommendations
   recs = asyncio.run(recommendation_service.get_recommendations(user_id=1))
   print(recs)
   ```

---

## API Reference

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/recommend/{user_id}` | GET | Get personalized recommendations |
| `/health` | GET | Health check (DB + Redis) |
| `/sync/user` | POST | Sync user from Django |
| `/sync/business` | POST | Sync business from Django |
| `/interaction` | POST | Record user interaction |
| `/cache/clear/{user_id}` | POST | Clear user's cache |
| `/user/{user_id}/interactions` | GET | Get user's interaction history |
