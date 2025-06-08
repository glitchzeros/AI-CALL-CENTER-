"""
Company number pool models
The Scribe's Phone Number Registry
"""

from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from database.connection import Base

class CompanyNumberPool(Base):
    __tablename__ = "company_number_pool"
    
    id = Column(Integer, primary_key=True, index=True)
    phone_number = Column(String(20), unique=True, nullable=False)
    is_assigned = Column(Boolean, default=False)
    assigned_user_id = Column(Integer, ForeignKey("users.id"))
    assigned_at = Column(DateTime)
    created_at = Column(DateTime, default=func.now())
    
    # Relationships - temporarily disabled to avoid issues
    # assigned_user = relationship("User")