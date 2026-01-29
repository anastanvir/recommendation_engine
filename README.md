## Project Overview

A FastAPI-based recommendation engine for a social marketplace platform. Provides personalized business/product recommendations based on user interests, interaction history, location context, and popularity scores.

**Tech Stack:** FastAPI, PostgreSQL 15 (async via asyncpg/SQLAlchemy), Redis 7 (caching), UV (package management), Docker

## Common Commands

```bash
# Development
make up                 # Start all services (postgres, redis, recommender)
make up-dev             # Start with development overrides (hot reload)
make down               # Stop all services
make logs               # View all logs
make logs-api           # View API logs only
make restart            # Restart all services

# Testing
make test               # Run pytest in container

# Database
make db-shell           # Open PostgreSQL CLI
make seed               # Seed database with init-db.sql

# Other
make redis-shell        # Open Redis CLI
make health             # Check health endpoint
make clean              # Remove containers, volumes, prune
```

## Architecture

### Services (docker-compose.yml)
- **recommender** (port 8000) - FastAPI application
- **postgres** (port 5432) - PostgreSQL database
- **redis** (port 6379) - Recommendation cache

### Code Structure (`/app`)
- `main.py` - FastAPI app, routes, recommendation algorithm
- `config.py` - Environment configuration (Pydantic Settings)
- `models.py` - SQLAlchemy ORM models (User, Business, UserInteraction)
- `database.py` - Async database engine and session management
- `redis_client.py` - RedisManager singleton for caching

### Recommendation Algorithm
Located in `app/main.py`. Content-based filtering with:
- Category matching (60% weight)
- Tag matching (40% weight)
- Popularity score boost (10%)
- Location bonus (20% if user location matches business)

### Caching Strategy
- Cache key pattern: `recs:{user_id}:{context_hash}`
- Default TTL: 300 seconds (configurable via `CACHE_TTL`)
- User features cached separately with 1-hour TTL
- Toggle caching per-request with `use_cache` query param

### Database Schema
- `users` - profiles with interests (JSON array) and location (JSON)
- `businesses` - listings with categories/tags (JSON arrays), popularity_score
- `user_interactions` - tracks view/like/save/purchase/share with weights

## Key API Endpoints

| Endpoint | Description |
|----------|-------------|
| `GET /recommend/{user_id}` | Get personalized recommendations |
| `GET /health` | Health check (DB + Redis connectivity) |
| `POST /cache/clear/{user_id}` | Clear user's recommendation cache |
| `GET /user/{user_id}/interactions` | Get user interaction history |

## Environment Variables

Key settings in `.env` / `.env.docker`:
- `DATABASE_URL` - PostgreSQL async connection string
- `REDIS_URL` - Redis connection
- `CACHE_TTL` - Cache time-to-live in seconds
- `MAX_RECOMMENDATIONS` - Limit on returned recommendations
- `ALLOWED_ORIGINS` - CORS origins (currently allows all, needs restriction for production)