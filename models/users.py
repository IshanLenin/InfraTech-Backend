from sqlalchemy import Column, Integer, String, Boolean, Numeric, DateTime, ForeignKey, Index, text
from sqlalchemy.sql import func
from database import Base

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255))
    email = Column(String(255), unique=True, index=True)
    status = Column(String(50), server_default="active")
    is_verified = Column(Boolean, server_default=text("false"))
    refer_code = Column(String(50), unique=True, nullable=False)
    referrer_id = Column(String(50)) 
    pp_points = Column(Integer, server_default=text("0"))
    latest_pp_point = Column(Integer, server_default=text("0"))
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class UserFollow(Base):
    __tablename__ = "userfollow"
    
    follower_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), primary_key=True)
    following_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), primary_key=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
