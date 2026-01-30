from contextlib import asynccontextmanager
from fastapi import FastAPI, Depends, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, text
from pydantic import BaseModel
import hashlib
import json
from typing import Optional, List

from .database import get_db_session, engine, Base
from .redis_client import redis_manager
from .models import User, Business, UserInteraction
from .config import settings


# =============================================================================
# Request/Response Models (for Django integration)
# =============================================================================

class UserSync(BaseModel):
    """Model for syncing users from Django"""
    id: int
    username: str
    email: str
    interests: List[str] = []
    location: Optional[dict] = None


class BusinessSync(BaseModel):
    """Model for syncing businesses from Django"""
    id: int
    name: str
    description: Optional[str] = None
    categories: List[str] = []
    tags: List[str] = []
    location: Optional[dict] = None
    popularity_score: float = 0.0
    rating: float = 0.0
    rating_count: int = 0


class InteractionCreate(BaseModel):
    """Model for recording interactions from Django"""
    user_id: int
    business_id: int
    interaction_type: str  # view, like, save, purchase, share
    weight: float = 1.0

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan context manager for startup/shutdown events"""
    # Startup
    await redis_manager.initialize()
    
    # Create tables in development (use Alembic in production)
    if settings.ENVIRONMENT == "development":
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
    
    yield
    
    # Shutdown
    await redis_manager.close()

app = FastAPI(
    title="Recommendation Engine",
    description="Personalized feed generator for social marketplace",
    version="1.0.0",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Restrict in production!
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["*"],
)

# Health check endpoint
@app.get("/")
async def root():
    return {
        "service": "recommendation-engine",
        "version": "1.0.0",
        "status": "operational"
    }

@app.get("/health")
async def health_check(db: AsyncSession = Depends(get_db_session)):
    """Comprehensive health check"""
    health_status = {
        "status": "healthy",
        "services": {}
    }
    
    # Check database
    try:
        result = await db.execute(text("SELECT 1"))
        health_status["services"]["database"] = "connected"
    except Exception as e:
        health_status["services"]["database"] = f"error: {str(e)}"
        health_status["status"] = "degraded"
    
    # Check Redis
    try:
        client = await redis_manager.get_client()
        await client.ping()
        health_status["services"]["redis"] = "connected"
    except Exception as e:
        health_status["services"]["redis"] = f"error: {str(e)}"
        health_status["status"] = "degraded"
    
    return health_status

# Main recommendation endpoint
@app.get("/recommend/{user_id}")
async def get_recommendations(
    user_id: int,
    context: Optional[str] = Query(
        default='{"location": null, "time_of_day": null}',
        description="JSON context for recommendations"
    ),
    max_results: int = Query(default=10, ge=1, le=50),
    use_cache: bool = Query(default=True),
    db: AsyncSession = Depends(get_db_session)
):
    """
    Get personalized recommendations for a user.
    
    Workflow:
    1. Check cache if enabled
    2. Fetch user data from database
    3. Generate recommendations
    4. Cache results for future requests
    """
    
    # Parse context and create hash for cache key
    try:
        context_dict = json.loads(context)
        context_hash = hashlib.md5(context.encode()).hexdigest()[:8]
    except json.JSONDecodeError:
        raise HTTPException(status_code=400, detail="Invalid context JSON")
    
    # Step 1: Check cache
    if use_cache:
        cached_recs = await redis_manager.get_recommendations(user_id, context_hash)
        if cached_recs:
            return {
                "source": "cache",
                "user_id": user_id,
                "recommendations": cached_recs[:max_results],
                "count": len(cached_recs[:max_results])
            }
    
    # Step 2: Fetch user from database
    result = await db.execute(
        select(User).where(User.id == user_id)
    )
    user = result.scalar_one_or_none()
    
    if not user:
        raise HTTPException(status_code=404, detail=f"User {user_id} not found")
    
    # Step 3: Fetch user interactions
    interactions_result = await db.execute(
        select(UserInteraction)
        .where(UserInteraction.user_id == user_id)
        .order_by(UserInteraction.timestamp.desc())
        .limit(100)
    )
    interactions = interactions_result.scalars().all()
    
    # Step 4: Fetch candidate businesses
    # In production, this would use more sophisticated filtering
    businesses_result = await db.execute(
        select(Business)
        .order_by(Business.popularity_score.desc())
        .limit(200)
    )
    businesses = businesses_result.scalars().all()
    
    # Step 5: Generate recommendations
    recommendations = await generate_recommendations(
        user=user,
        interactions=interactions,
        businesses=businesses,
        context=context_dict,
        max_results=max_results
    )
    
    # Step 6: Cache results
    if use_cache and recommendations:
        await redis_manager.set_recommendations(user_id, context_hash, recommendations)
    
    return {
        "source": "database",
        "user_id": user_id,
        "recommendations": recommendations,
        "count": len(recommendations)
    }

# Recommendation logic placeholder
async def generate_recommendations(user, interactions, businesses, context, max_results):
    """
    Placeholder for your recommendation algorithms.
    Replace with actual ML models (content-based, collaborative, etc.)
    """
    recommendations = []
    
    # Simple content-based scoring based on user interests
    user_interests = set(user.interests or [])
    
    for business in businesses[:50]:  # Consider top 50 businesses
        # Calculate match score
        business_categories = set(business.categories or [])
        business_tags = set(business.tags or [])
        
        # Content similarity
        category_match = len(user_interests & business_categories)
        tag_match = len(user_interests & business_tags)
        
        # Simple scoring formula
        content_score = (category_match * 0.6) + (tag_match * 0.4)
        popularity_score = business.popularity_score * 0.1
        
        # Location bonus if provided
        location_bonus = 0.0
        if context.get("location") and business.location:
            # Simple location check (implement proper distance calculation)
            location_bonus = 0.2
        
        total_score = content_score + popularity_score + location_bonus
        
        if total_score > 0:  # Only include if there's some match
            recommendations.append({
                "business_id": business.id,
                "name": business.name,
                "categories": business.categories,
                "score": round(total_score, 3),
                "type": "content_based",
                "location": business.location
            })
    
    # Sort by score and limit
    recommendations.sort(key=lambda x: x["score"], reverse=True)
    return recommendations[:max_results]

# Admin/development endpoints
@app.post("/cache/clear/{user_id}")
async def clear_user_cache(user_id: int):
    """Clear cache for a specific user"""
    try:
        # This would need pattern matching in production
        client = await redis_manager.get_client()
        
        # Get all cache keys for this user
        pattern = f"*{user_id}*"
        keys = await client.keys(pattern)
        
        if keys:
            await client.delete(*keys)
        
        return {
            "status": "success",
            "message": f"Cleared {len(keys)} cache entries for user {user_id}"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/user/{user_id}/interactions")
async def get_user_interactions(
    user_id: int,
    limit: int = Query(default=20, ge=1, le=100),
    db: AsyncSession = Depends(get_db_session)
):
    """Get user interactions for debugging"""
    result = await db.execute(
        select(UserInteraction)
        .where(UserInteraction.user_id == user_id)
        .order_by(UserInteraction.timestamp.desc())
        .limit(limit)
    )
    interactions = result.scalars().all()

    return {
        "user_id": user_id,
        "interactions_count": len(interactions),
        "interactions": [
            {
                "business_id": i.business_id,
                "type": i.interaction_type,
                "timestamp": i.timestamp.isoformat(),
                "weight": i.weight
            }
            for i in interactions
        ]
    }


# =============================================================================
# Django Integration Endpoints
# =============================================================================

@app.post("/sync/user")
async def sync_user(user: UserSync, db: AsyncSession = Depends(get_db_session)):
    """
    Sync user from Django to recommendation engine.
    Creates or updates user record.
    """
    try:
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

        # Invalidate user cache
        client = await redis_manager.get_client()
        keys = await client.keys(f"recs:{user.id}:*")
        if keys:
            await client.delete(*keys)

        return {"status": "synced", "user_id": user.id}
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/sync/business")
async def sync_business(business: BusinessSync, db: AsyncSession = Depends(get_db_session)):
    """
    Sync business from Django to recommendation engine.
    Creates or updates business record.
    """
    try:
        await db.execute(
            text("""
                INSERT INTO businesses (id, name, description, categories, tags, location, popularity_score, rating, rating_count)
                VALUES (:id, :name, :description, :categories, :tags, :location, :popularity_score, :rating, :rating_count)
                ON CONFLICT (id) DO UPDATE SET
                    name = EXCLUDED.name,
                    description = EXCLUDED.description,
                    categories = EXCLUDED.categories,
                    tags = EXCLUDED.tags,
                    location = EXCLUDED.location,
                    popularity_score = EXCLUDED.popularity_score,
                    rating = EXCLUDED.rating,
                    rating_count = EXCLUDED.rating_count,
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
                "rating_count": business.rating_count,
            }
        )
        await db.commit()
        return {"status": "synced", "business_id": business.id}
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/interaction")
async def record_interaction(interaction: InteractionCreate, db: AsyncSession = Depends(get_db_session)):
    """
    Record user interaction from Django.
    Used to track views, likes, saves, purchases, shares.
    """
    # Validate interaction type
    valid_types = {'view', 'like', 'save', 'purchase', 'share'}
    if interaction.interaction_type not in valid_types:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid interaction_type. Must be one of: {valid_types}"
        )

    try:
        await db.execute(
            text("""
                INSERT INTO user_interactions (user_id, business_id, interaction_type, weight)
                VALUES (:user_id, :business_id, :interaction_type, :weight)
                ON CONFLICT (user_id, business_id, interaction_type)
                DO UPDATE SET
                    weight = EXCLUDED.weight,
                    timestamp = CURRENT_TIMESTAMP
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
        client = await redis_manager.get_client()
        keys = await client.keys(f"recs:{interaction.user_id}:*")
        if keys:
            await client.delete(*keys)

        return {
            "status": "recorded",
            "user_id": interaction.user_id,
            "business_id": interaction.business_id,
            "interaction_type": interaction.interaction_type
        }
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=str(e))


@app.delete("/sync/user/{user_id}")
async def delete_user(user_id: int, db: AsyncSession = Depends(get_db_session)):
    """Delete user and their interactions (for GDPR compliance, etc.)"""
    try:
        # Delete interactions first (cascade should handle this, but explicit is safer)
        await db.execute(
            text("DELETE FROM user_interactions WHERE user_id = :user_id"),
            {"user_id": user_id}
        )

        # Delete user
        result = await db.execute(
            text("DELETE FROM users WHERE id = :user_id RETURNING id"),
            {"user_id": user_id}
        )
        deleted = result.fetchone()
        await db.commit()

        if not deleted:
            raise HTTPException(status_code=404, detail=f"User {user_id} not found")

        # Clear cache
        client = await redis_manager.get_client()
        keys = await client.keys(f"*{user_id}*")
        if keys:
            await client.delete(*keys)

        return {"status": "deleted", "user_id": user_id}
    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=str(e))


@app.delete("/sync/business/{business_id}")
async def delete_business(business_id: int, db: AsyncSession = Depends(get_db_session)):
    """Delete business and related interactions"""
    try:
        # Delete interactions first
        await db.execute(
            text("DELETE FROM user_interactions WHERE business_id = :business_id"),
            {"business_id": business_id}
        )

        # Delete business
        result = await db.execute(
            text("DELETE FROM businesses WHERE id = :business_id RETURNING id"),
            {"business_id": business_id}
        )
        deleted = result.fetchone()
        await db.commit()

        if not deleted:
            raise HTTPException(status_code=404, detail=f"Business {business_id} not found")

        return {"status": "deleted", "business_id": business_id}
    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=str(e))