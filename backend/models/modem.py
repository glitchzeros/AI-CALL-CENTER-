"""
GSM modem and SMS models
The Scribe's Communication Hardware
"""

from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from database.connection import Base

class GSMModem(Base):
    __tablename__ = "gsm_modems"
    
    id = Column(Integer, primary_key=True, index=True)
    device_id = Column(String(50), unique=True, nullable=False)  # Physical device identifier
    control_port = Column(String(50))  # /dev/ttyUSBX for AT commands
    audio_port = Column(String(50))  # /dev/snd/pcmCYDX for audio
    phone_number = Column(String(20), unique=True)
    status = Column(String(20), default="offline")  # offline, idle, busy, error
    signal_strength = Column(Integer)
    last_seen = Column(DateTime, default=func.now())
    assigned_user_id = Column(Integer, ForeignKey("users.id"))
    created_at = Column(DateTime, default=func.now())
    
    # Relationships
    sms_messages = relationship("SMSMessage", back_populates="modem")

class SMSMessage(Base):
    __tablename__ = "sms_messages"
    
    id = Column(Integer, primary_key=True, index=True)
    modem_id = Column(Integer, ForeignKey("gsm_modems.id"))
    direction = Column(String(10), nullable=False)  # incoming, outgoing
    from_number = Column(String(20))
    to_number = Column(String(20))
    content = Column(Text, nullable=False)
    status = Column(String(20), default="pending")  # pending, sent, delivered, failed
    session_id = Column(Integer, ForeignKey("communication_sessions.id"))
    sent_at = Column(DateTime)
    received_at = Column(DateTime, default=func.now())
    metadata = Column(JSON)
    
    # Relationships
    modem = relationship("GSMModem", back_populates="sms_messages")
    session = relationship("CommunicationSession")