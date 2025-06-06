"""
Statistics router
The Scribe's Performance Analytics
"""

from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, text
from pydantic import BaseModel
from typing import List, Dict, Any
from datetime import datetime, timedelta, date

from database.connection import get_database
from models.user import User
from models.statistics import CallStatistics
from models.session import CommunicationSession
from routers.auth import get_current_user

router = APIRouter()

class DailyStatistics(BaseModel):
    date: str
    total_calls: int
    total_duration_seconds: int
    positive_interactions: int
    negative_interactions: int
    total_sms_sent: int
    total_sms_received: int

class OverallStatistics(BaseModel):
    total_calls: int
    total_duration_seconds: int
    positive_interactions: int
    negative_interactions: int
    positive_percentage: float
    negative_percentage: float
    average_call_duration: float

@router.get("/dashboard", response_model=OverallStatistics)
async def get_dashboard_statistics(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_database)
):
    """
    Get overall dashboard statistics
    The Scribe's Performance Overview
    """
    try:
        # Get aggregated statistics
        result = await db.execute(
            select(
                func.sum(CallStatistics.total_calls).label("total_calls"),
                func.sum(CallStatistics.total_duration_seconds).label("total_duration"),
                func.sum(CallStatistics.positive_interactions).label("positive"),
                func.sum(CallStatistics.negative_interactions).label("negative"),
                func.sum(CallStatistics.total_sms_sent).label("sms_sent"),
                func.sum(CallStatistics.total_sms_received).label("sms_received")
            ).where(CallStatistics.user_id == current_user.id)
        )
        
        stats = result.first()
        
        total_calls = stats.total_calls or 0
        total_duration = stats.total_duration or 0
        positive = stats.positive or 0
        negative = stats.negative or 0
        
        total_interactions = positive + negative
        positive_percentage = (positive / total_interactions * 100) if total_interactions > 0 else 0
        negative_percentage = (negative / total_interactions * 100) if total_interactions > 0 else 0
        average_duration = (total_duration / total_calls) if total_calls > 0 else 0
        
        return OverallStatistics(
            total_calls=total_calls,
            total_duration_seconds=total_duration,
            positive_interactions=positive,
            negative_interactions=negative,
            positive_percentage=round(positive_percentage, 1),
            negative_percentage=round(negative_percentage, 1),
            average_call_duration=round(average_duration, 1)
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail="Failed to get dashboard statistics")

@router.get("/daily", response_model=List[DailyStatistics])
async def get_daily_statistics(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_database),
    days: int = 30
):
    """
    Get daily statistics for the past N days
    The Scribe's Daily Performance
    """
    try:
        since_date = date.today() - timedelta(days=days)
        
        result = await db.execute(
            select(CallStatistics).where(
                CallStatistics.user_id == current_user.id,
                CallStatistics.date >= since_date
            ).order_by(CallStatistics.date.desc())
        )
        
        statistics = result.scalars().all()
        
        return [
            DailyStatistics(
                date=stat.date.isoformat(),
                total_calls=stat.total_calls,
                total_duration_seconds=stat.total_duration_seconds,
                positive_interactions=stat.positive_interactions,
                negative_interactions=stat.negative_interactions,
                total_sms_sent=stat.total_sms_sent,
                total_sms_received=stat.total_sms_received
            )
            for stat in statistics
        ]
        
    except Exception as e:
        raise HTTPException(status_code=500, detail="Failed to get daily statistics")

@router.get("/trends")
async def get_statistics_trends(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_database),
    days: int = 7
):
    """
    Get statistics trends and comparisons
    The Scribe's Performance Trends
    """
    try:
        # Get current period stats
        current_start = date.today() - timedelta(days=days)
        current_result = await db.execute(
            select(
                func.sum(CallStatistics.total_calls).label("calls"),
                func.sum(CallStatistics.positive_interactions).label("positive"),
                func.sum(CallStatistics.negative_interactions).label("negative"),
                func.sum(CallStatistics.total_duration_seconds).label("duration")
            ).where(
                CallStatistics.user_id == current_user.id,
                CallStatistics.date >= current_start
            )
        )
        current_stats = current_result.first()
        
        # Get previous period stats for comparison
        previous_start = current_start - timedelta(days=days)
        previous_end = current_start
        previous_result = await db.execute(
            select(
                func.sum(CallStatistics.total_calls).label("calls"),
                func.sum(CallStatistics.positive_interactions).label("positive"),
                func.sum(CallStatistics.negative_interactions).label("negative"),
                func.sum(CallStatistics.total_duration_seconds).label("duration")
            ).where(
                CallStatistics.user_id == current_user.id,
                CallStatistics.date >= previous_start,
                CallStatistics.date < previous_end
            )
        )
        previous_stats = previous_result.first()
        
        # Calculate trends
        def calculate_trend(current, previous):
            if previous and previous > 0:
                return round(((current or 0) - previous) / previous * 100, 1)
            return 0
        
        current_calls = current_stats.calls or 0
        previous_calls = previous_stats.calls or 0
        current_positive = current_stats.positive or 0
        previous_positive = previous_stats.positive or 0
        current_duration = current_stats.duration or 0
        previous_duration = previous_stats.duration or 0
        
        return {
            "period_days": days,
            "current_period": {
                "calls": current_calls,
                "positive_interactions": current_positive,
                "total_duration": current_duration
            },
            "previous_period": {
                "calls": previous_calls,
                "positive_interactions": previous_positive,
                "total_duration": previous_duration
            },
            "trends": {
                "calls_change_percent": calculate_trend(current_calls, previous_calls),
                "positive_change_percent": calculate_trend(current_positive, previous_positive),
                "duration_change_percent": calculate_trend(current_duration, previous_duration)
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail="Failed to get statistics trends")

@router.get("/hourly-distribution")
async def get_hourly_distribution(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_database),
    days: int = 7
):
    """
    Get hourly distribution of calls
    The Scribe's Activity Patterns
    """
    try:
        since_date = datetime.utcnow() - timedelta(days=days)
        
        # Get sessions grouped by hour
        result = await db.execute(text("""
            SELECT 
                EXTRACT(HOUR FROM started_at) as hour,
                COUNT(*) as call_count,
                AVG(duration_seconds) as avg_duration
            FROM communication_sessions 
            WHERE user_id = :user_id 
                AND started_at >= :since_date
                AND status = 'completed'
            GROUP BY EXTRACT(HOUR FROM started_at)
            ORDER BY hour
        """), {
            "user_id": current_user.id,
            "since_date": since_date
        })
        
        hourly_data = {}
        for row in result:
            hour = int(row[0])
            call_count = row[1]
            avg_duration = float(row[2]) if row[2] else 0
            
            hourly_data[hour] = {
                "call_count": call_count,
                "average_duration": round(avg_duration, 1)
            }
        
        # Fill in missing hours with zero data
        complete_hourly_data = []
        for hour in range(24):
            data = hourly_data.get(hour, {"call_count": 0, "average_duration": 0})
            complete_hourly_data.append({
                "hour": hour,
                "call_count": data["call_count"],
                "average_duration": data["average_duration"]
            })
        
        return {
            "period_days": days,
            "hourly_distribution": complete_hourly_data
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail="Failed to get hourly distribution")

@router.get("/outcome-analysis")
async def get_outcome_analysis(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_database),
    days: int = 30
):
    """
    Get detailed outcome analysis
    The Scribe's Success Analysis
    """
    try:
        since_date = datetime.utcnow() - timedelta(days=days)
        
        # Get outcome distribution
        result = await db.execute(text("""
            SELECT 
                outcome,
                session_type,
                COUNT(*) as count,
                AVG(duration_seconds) as avg_duration
            FROM communication_sessions 
            WHERE user_id = :user_id 
                AND started_at >= :since_date
                AND outcome IS NOT NULL
            GROUP BY outcome, session_type
            ORDER BY outcome, session_type
        """), {
            "user_id": current_user.id,
            "since_date": since_date
        })
        
        outcome_data = {}
        for row in result:
            outcome = row[0]
            session_type = row[1]
            count = row[2]
            avg_duration = float(row[3]) if row[3] else 0
            
            if outcome not in outcome_data:
                outcome_data[outcome] = {}
            
            outcome_data[outcome][session_type] = {
                "count": count,
                "average_duration": round(avg_duration, 1)
            }
        
        return {
            "period_days": days,
            "outcome_analysis": outcome_data
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail="Failed to get outcome analysis")