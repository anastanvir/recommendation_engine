from sqlalchemy import Column, Integer, String, Float, JSON, DateTime, ForeignKey, Index
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from .database import Base

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    interests = Column(JSON, default=[])  # ["food", "fashion", "tech"]
    location = Column(JSON)  # {"lat": 40.7128, "lon": -74.0060}
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    interactions = relationship("UserInteraction", back_populates="user")
    
class Business(Base):
    __tablename__ = "businesses"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    categories = Column(JSON)  # ["restaurant", "italian", "pizza"]
    tags = Column(JSON)  # ["romantic", "family-friendly", "vegan"]
    location = Column(JSON)
    popularity_score = Column(Float, default=0.0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
class UserInteraction(Base):
    __tablename__ = "user_interactions"
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), index=True)
    business_id = Column(Integer, ForeignKey("businesses.id"), index=True)
    interaction_type = Column(String)  # "view", "like", "save", "purchase"
    weight = Column(Float, default=1.0)  # Weight of this interaction
    timestamp = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    user = relationship("User", back_populates="interactions")
    business = relationship("Business")
    
    # Index for fast queries
    __table_args__ = (
        Index('idx_user_interaction', 'user_id', 'timestamp'),
        Index('idx_user_business', 'user_id', 'business_id'),
    )