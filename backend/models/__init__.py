"""
Database models for Aetherium
The Scribe's Data Structures
"""

# Temporarily import only essential models to avoid relationship issues
from .subscription import SubscriptionTier
# from .user import User
# from .subscription import UserSubscription
# from .workflow import ScribeWorkflow
# from .session import CommunicationSession, SessionMessage
# from .statistics import CallStatistics
# from .modem import GSMModem, SMSMessage
# from .payment import PaymentTransaction
# from .telegram import TelegramChat
# from .dream_journal import ScribeDreamJournal
# from .company_number import CompanyNumberPool
# from .gsm_module import GSMModule, PaymentSession
# from .sms_verification import SMSVerificationSession

__all__ = [
    "SubscriptionTier",
    # "User",
    # "UserSubscription", 
    # "ScribeWorkflow",
    # "CommunicationSession",
    # "SessionMessage",
    # "CallStatistics",
    # "GSMModem",
    # "SMSMessage",
    # "PaymentTransaction",
    # "TelegramChat",
    # "ScribeDreamJournal",
    # "CompanyNumberPool",
    # "GSMModule",
    # "PaymentSession",
    # "SMSVerificationSession"
]