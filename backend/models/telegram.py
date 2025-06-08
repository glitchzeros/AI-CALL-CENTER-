"""
Telegram integration models
The Scribe's Telegram Gateway
"""

from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, BigInteger
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from database.connection import Base

class TelegramChat(Base):
    __tablename__ = "telegram_chats"
    
    id = Column(Integer, primary_key=True, index=True)
    chat_id = Column(BigInteger, unique=True, nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"))
    username = Column(String(255))
    first_name = Column(String(255))
    last_name = Column(String(255))
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=func.now())
    
    # Relationships - temporarily disabled to avoid issues
    # user = relationship("User")