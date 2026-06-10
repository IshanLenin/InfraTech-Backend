from sqlalchemy import Column, Integer, String, Boolean, Numeric, DateTime, ForeignKey, Index, text
from sqlalchemy.sql import func
from database import Base

class Brand(Base):
    __tablename__ = "brands"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    category = Column(String(100))
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class Deal(Base):
    __tablename__ = "deal"
    
    id = Column(Integer, primary_key=True, index=True)
    brand_id = Column(Integer, ForeignKey("brands.id", ondelete="CASCADE"))
    title = Column(String(255), nullable=False)
    status = Column(String(50), server_default="active")
    payout_percentage = Column(Numeric(5, 2), nullable=False, server_default=text("75.00"))
    has_seo_metadata = Column(Boolean, server_default=text("false"))
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class Banner(Base):
    __tablename__ = "banners"
    
    id = Column(Integer, primary_key=True, index=True)
    deal_id = Column(Integer, ForeignKey("deal.id", ondelete="CASCADE"))
    platform = Column(String(50), nullable=False)
    type = Column(String(50), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class Reward(Base):
    __tablename__ = "reward"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="RESTRICT"), index=True)
    deal_id = Column(Integer, ForeignKey("deal.id", ondelete="SET NULL"))
    banner_id = Column(Integer, ForeignKey("banners.id", ondelete="SET NULL"))
    type = Column(String(50), nullable=False, index=True)
    amount = Column(Numeric(10, 2), nullable=False, server_default=text("0.00"))
    receipt_uploaded = Column(Boolean, server_default=text("false"))
    created_at = Column(DateTime(timezone=True), server_default=func.now())