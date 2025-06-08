"""
Landing Page API Router
Provides public information about features and pricing
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Any
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/landing", tags=["landing"])

class Feature(BaseModel):
    icon: str
    title: str
    description: str
    category: str

class PricingPlan(BaseModel):
    name: str
    price: str
    period: str
    description: str
    features: List[str]
    popular: bool
    color: str
    limits: Dict[str, Any]

class LandingInfo(BaseModel):
    features: List[Feature]
    pricing_plans: List[PricingPlan]
    company_info: Dict[str, Any]

@router.get("/info", response_model=LandingInfo)
async def get_landing_info():
    """Get comprehensive landing page information"""
    try:
        features = [
            Feature(
                icon="phone",
                title="AI-Powered Call Center",
                description="Advanced AI handles customer calls with natural conversation flow and intelligent responses.",
                category="core"
            ),
            Feature(
                icon="message-square",
                title="SMS Verification System",
                description="Secure SMS-based authentication with real GSM module integration and demo mode support.",
                category="security"
            ),
            Feature(
                icon="bar-chart-3",
                title="Real-time Analytics",
                description="Comprehensive statistics and insights into call performance, customer satisfaction, and system metrics.",
                category="analytics"
            ),
            Feature(
                icon="globe",
                title="Multi-language Support",
                description="Support for multiple languages with seamless translation capabilities for global reach.",
                category="localization"
            ),
            Feature(
                icon="shield",
                title="Enterprise Security",
                description="Bank-grade security with encrypted communications and secure payment processing.",
                category="security"
            ),
            Feature(
                icon="settings",
                title="GSM Module Management",
                description="Complete management of company GSM modules with bank card integration for payments.",
                category="management"
            )
        ]

        pricing_plans = [
            PricingPlan(
                name="Starter",
                price="$29",
                period="/month",
                description="Perfect for small businesses getting started",
                features=[
                    "Up to 100 calls/month",
                    "Basic SMS verification",
                    "Standard AI responses",
                    "Email support",
                    "Basic analytics"
                ],
                popular=False,
                color="coffee-tan",
                limits={
                    "calls_per_month": 100,
                    "sms_per_month": 50,
                    "gsm_modules": 1,
                    "support_level": "email"
                }
            ),
            PricingPlan(
                name="Professional",
                price="$99",
                period="/month",
                description="Ideal for growing businesses",
                features=[
                    "Up to 1,000 calls/month",
                    "Advanced SMS verification",
                    "Custom AI training",
                    "Priority support",
                    "Advanced analytics",
                    "Multi-language support",
                    "GSM module integration"
                ],
                popular=True,
                color="coffee-sienna",
                limits={
                    "calls_per_month": 1000,
                    "sms_per_month": 500,
                    "gsm_modules": 5,
                    "support_level": "priority"
                }
            ),
            PricingPlan(
                name="Enterprise",
                price="$299",
                period="/month",
                description="For large organizations",
                features=[
                    "Unlimited calls",
                    "Enterprise SMS system",
                    "Custom AI personalities",
                    "24/7 dedicated support",
                    "Real-time analytics",
                    "Full GSM management",
                    "Custom integrations",
                    "White-label solution"
                ],
                popular=False,
                color="coffee-brown",
                limits={
                    "calls_per_month": -1,  # unlimited
                    "sms_per_month": -1,    # unlimited
                    "gsm_modules": -1,      # unlimited
                    "support_level": "dedicated"
                }
            )
        ]

        company_info = {
            "name": "Aetherium",
            "tagline": "The Future of AI Communication",
            "description": "Transform your customer service with our advanced AI-powered call center system.",
            "founded": "2025",
            "headquarters": "Global",
            "contact": {
                "email": "contact@aetherium.ai",
                "phone": "+1-800-AETHERIUM",
                "support": "support@aetherium.ai"
            },
            "social": {
                "twitter": "@AetheriumAI",
                "linkedin": "company/aetherium-ai",
                "github": "aetherium-ai"
            }
        }

        return LandingInfo(
            features=features,
            pricing_plans=pricing_plans,
            company_info=company_info
        )

    except Exception as e:
        logger.error(f"Error getting landing info: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to get landing information")

@router.get("/features", response_model=List[Feature])
async def get_features():
    """Get all available features"""
    try:
        landing_info = await get_landing_info()
        return landing_info.features
    except Exception as e:
        logger.error(f"Error getting features: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to get features")

@router.get("/pricing", response_model=List[PricingPlan])
async def get_pricing():
    """Get all pricing plans"""
    try:
        landing_info = await get_landing_info()
        return landing_info.pricing_plans
    except Exception as e:
        logger.error(f"Error getting pricing: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to get pricing")

@router.get("/company", response_model=Dict[str, Any])
async def get_company_info():
    """Get company information"""
    try:
        landing_info = await get_landing_info()
        return landing_info.company_info
    except Exception as e:
        logger.error(f"Error getting company info: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to get company information")

@router.get("/stats")
async def get_public_stats():
    """Get public statistics for landing page"""
    try:
        # These would normally come from the database
        # For now, return mock data
        return {
            "total_calls_handled": 1250000,
            "active_customers": 5420,
            "countries_served": 45,
            "uptime_percentage": 99.9,
            "average_response_time": "0.3s",
            "customer_satisfaction": 4.8
        }
    except Exception as e:
        logger.error(f"Error getting public stats: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to get statistics")