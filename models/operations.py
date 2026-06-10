from sqlalchemy import Column, Integer, String, Boolean, Numeric, DateTime, ForeignKey, Index, text
from database import Base
from sqlalchemy.sql import func

class Ticket(Base):
    __tablename__ = "tickets"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"))
    reward_id = Column(Integer, ForeignKey("reward.id", ondelete="SET NULL"))
    status = Column(String(50), server_default="unresolved_backlog")
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    resolved_at = Column(DateTime(timezone=True))

class PaymentInstrument(Base):
    __tablename__ = "payment_instruments"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"))
    instrument_type = Column(String(50), nullable=False)
    instrument_id = Column(String(255), nullable=False)
    is_primary = Column(Boolean, server_default=text("false"))
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # This enforces the Partial Unique Index we discussed
    __table_args__ = (
        Index(
            'unique_primary_per_user', 
            'user_id', 
            unique=True, 
            postgresql_where=(is_primary == True)
        ),
    )

class Notification(Base):
    __tablename__ = "notifications"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"))
    is_read = Column(Boolean, server_default=text("false"))
    created_at = Column(DateTime(timezone=True), server_default=func.now())