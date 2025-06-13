"""
Analytics API endpoints.
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional, List
from datetime import datetime, timedelta
import logging

from app.core.database import get_db
from app.core.redis import cache, get_cache_key
from app.core.config import settings
from app.services.analytics_service import AnalyticsService
from app.schemas.analytics import (
    AnalyticsOverview,
    ChargingPatterns,
    CostAnalysis,
    DemandForecast,
    UserBehaviorAnalysis
)

router = APIRouter()
logger = logging.getLogger(__name__)


@router.get("/overview", response_model=AnalyticsOverview)
async def get_analytics_overview(
    start_date: Optional[datetime] = Query(None, description="Start date for analysis"),
    end_date: Optional[datetime] = Query(None, description="End date for analysis"),
    location: Optional[str] = Query(None, description="Filter by location"),
    db: AsyncSession = Depends(get_db)
):
    """Get analytics overview dashboard data."""
    try:
        # Set default date range if not provided
        if not end_date:
            end_date = datetime.utcnow()
        if not start_date:
            start_date = end_date - timedelta(days=30)
        
        # Generate cache key
        cache_key = await get_cache_key(
            "analytics_overview", 
            start_date.isoformat(), 
            end_date.isoformat(), 
            location or "all"
        )
        
        # Try to get from cache
        cached_result = await cache.get(cache_key)
        if cached_result:
            return cached_result
        
        # Get analytics service
        analytics_service = AnalyticsService(db)
        
        # Generate overview
        overview = await analytics_service.get_overview(
            start_date=start_date,
            end_date=end_date,
            location=location
        )
        
        # Cache result
        await cache.set(cache_key, overview.dict(), ttl=settings.CACHE_TTL_MEDIUM)
        
        return overview
        
    except Exception as e:
        logger.error(f"Error getting analytics overview: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/patterns", response_model=ChargingPatterns)
async def get_charging_patterns(
    start_date: Optional[datetime] = Query(None),
    end_date: Optional[datetime] = Query(None),
    user_type: Optional[str] = Query(None, description="Filter by user type"),
    vehicle_model: Optional[str] = Query(None, description="Filter by vehicle model"),
    db: AsyncSession = Depends(get_db)
):
    """Get charging patterns analysis."""
    try:
        # Set default date range
        if not end_date:
            end_date = datetime.utcnow()
        if not start_date:
            start_date = end_date - timedelta(days=30)
        
        cache_key = await get_cache_key(
            "charging_patterns",
            start_date.isoformat(),
            end_date.isoformat(),
            user_type or "all",
            vehicle_model or "all"
        )
        
        cached_result = await cache.get(cache_key)
        if cached_result:
            return cached_result
        
        analytics_service = AnalyticsService(db)
        patterns = await analytics_service.get_charging_patterns(
            start_date=start_date,
            end_date=end_date,
            user_type=user_type,
            vehicle_model=vehicle_model
        )
        
        await cache.set(cache_key, patterns.dict(), ttl=settings.CACHE_TTL_MEDIUM)
        return patterns
        
    except Exception as e:
        logger.error(f"Error getting charging patterns: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/costs", response_model=CostAnalysis)
async def get_cost_analysis(
    start_date: Optional[datetime] = Query(None),
    end_date: Optional[datetime] = Query(None),
    location: Optional[str] = Query(None),
    charger_type: Optional[str] = Query(None),
    db: AsyncSession = Depends(get_db)
):
    """Get cost analysis data."""
    try:
        if not end_date:
            end_date = datetime.utcnow()
        if not start_date:
            start_date = end_date - timedelta(days=30)
        
        cache_key = await get_cache_key(
            "cost_analysis",
            start_date.isoformat(),
            end_date.isoformat(),
            location or "all",
            charger_type or "all"
        )
        
        cached_result = await cache.get(cache_key)
        if cached_result:
            return cached_result
        
        analytics_service = AnalyticsService(db)
        cost_analysis = await analytics_service.get_cost_analysis(
            start_date=start_date,
            end_date=end_date,
            location=location,
            charger_type=charger_type
        )
        
        await cache.set(cache_key, cost_analysis.dict(), ttl=settings.CACHE_TTL_MEDIUM)
        return cost_analysis
        
    except Exception as e:
        logger.error(f"Error getting cost analysis: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/demand-forecast", response_model=DemandForecast)
async def get_demand_forecast(
    location: Optional[str] = Query(None),
    forecast_days: int = Query(7, ge=1, le=30, description="Number of days to forecast"),
    db: AsyncSession = Depends(get_db)
):
    """Get demand forecast for charging stations."""
    try:
        cache_key = await get_cache_key(
            "demand_forecast",
            location or "all",
            forecast_days
        )
        
        cached_result = await cache.get(cache_key)
        if cached_result:
            return cached_result
        
        analytics_service = AnalyticsService(db)
        forecast = await analytics_service.get_demand_forecast(
            location=location,
            forecast_days=forecast_days
        )
        
        await cache.set(cache_key, forecast.dict(), ttl=settings.CACHE_TTL_LONG)
        return forecast
        
    except Exception as e:
        logger.error(f"Error getting demand forecast: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/user-behavior", response_model=UserBehaviorAnalysis)
async def get_user_behavior_analysis(
    start_date: Optional[datetime] = Query(None),
    end_date: Optional[datetime] = Query(None),
    user_type: Optional[str] = Query(None),
    db: AsyncSession = Depends(get_db)
):
    """Get user behavior analysis."""
    try:
        if not end_date:
            end_date = datetime.utcnow()
        if not start_date:
            start_date = end_date - timedelta(days=30)
        
        cache_key = await get_cache_key(
            "user_behavior",
            start_date.isoformat(),
            end_date.isoformat(),
            user_type or "all"
        )
        
        cached_result = await cache.get(cache_key)
        if cached_result:
            return cached_result
        
        analytics_service = AnalyticsService(db)
        behavior_analysis = await analytics_service.get_user_behavior_analysis(
            start_date=start_date,
            end_date=end_date,
            user_type=user_type
        )
        
        await cache.set(cache_key, behavior_analysis.dict(), ttl=settings.CACHE_TTL_MEDIUM)
        return behavior_analysis
        
    except Exception as e:
        logger.error(f"Error getting user behavior analysis: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.post("/refresh-cache")
async def refresh_analytics_cache():
    """Refresh analytics cache."""
    try:
        # Delete all analytics cache keys
        cache_keys = await cache.keys("analytics_*")
        cache_keys.extend(await cache.keys("charging_patterns*"))
        cache_keys.extend(await cache.keys("cost_analysis*"))
        cache_keys.extend(await cache.keys("demand_forecast*"))
        cache_keys.extend(await cache.keys("user_behavior*"))
        
        for key in cache_keys:
            await cache.delete(key)
        
        return {"message": f"Refreshed {len(cache_keys)} cache entries"}
        
    except Exception as e:
        logger.error(f"Error refreshing analytics cache: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")
