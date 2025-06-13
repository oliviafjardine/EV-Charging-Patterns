"""
Analytics service for generating insights and reports.
"""

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, desc, case
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
import logging

from app.db.models import ChargingSession, ChargingStation, User
from app.schemas.analytics import (
    AnalyticsOverview,
    ChargingMetrics,
    LocationMetrics,
    TimeSeriesData,
    ChargingPatterns,
    ChargingPatternData,
    CostAnalysis,
    CostBreakdown,
    DemandForecast,
    DemandPrediction,
    UserBehaviorAnalysis,
    UserCluster
)

logger = logging.getLogger(__name__)


class AnalyticsService:
    """Service for analytics and insights generation."""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def get_overview(
        self,
        start_date: datetime,
        end_date: datetime,
        location: Optional[str] = None
    ) -> AnalyticsOverview:
        """Generate analytics overview."""
        # Build base query
        base_query = select(ChargingSession).where(
            and_(
                ChargingSession.charging_start_time >= start_date,
                ChargingSession.charging_start_time <= end_date
            )
        )
        
        if location:
            base_query = base_query.where(
                ChargingSession.charging_station_location.ilike(f"%{location}%")
            )
        
        # Overall metrics
        overall_metrics = await self._get_overall_metrics(base_query)
        
        # Location breakdown
        location_breakdown = await self._get_location_breakdown(base_query)
        
        # Daily trends
        daily_trends = await self._get_daily_trends(base_query, start_date, end_date)
        
        # Peak hours
        peak_hours = await self._get_peak_hours(base_query)
        
        # User type distribution
        user_type_distribution = await self._get_user_type_distribution(base_query)
        
        # Charger type usage
        charger_type_usage = await self._get_charger_type_usage(base_query)
        
        return AnalyticsOverview(
            period_start=start_date,
            period_end=end_date,
            overall_metrics=overall_metrics,
            location_breakdown=location_breakdown,
            daily_trends=daily_trends,
            peak_hours=peak_hours,
            user_type_distribution=user_type_distribution,
            charger_type_usage=charger_type_usage
        )
    
    async def _get_overall_metrics(self, base_query) -> ChargingMetrics:
        """Calculate overall charging metrics."""
        result = await self.db.execute(
            select(
                func.count(ChargingSession.id),
                func.sum(ChargingSession.energy_consumed_kwh),
                func.sum(ChargingSession.charging_cost_usd),
                func.avg(ChargingSession.charging_duration_hours),
                func.avg(ChargingSession.charging_cost_usd),
                func.avg(ChargingSession.energy_consumed_kwh)
            ).select_from(base_query.subquery())
        )
        
        metrics = result.first()
        
        return ChargingMetrics(
            total_sessions=metrics[0] or 0,
            total_energy_kwh=float(metrics[1] or 0),
            total_cost_usd=float(metrics[2] or 0),
            avg_duration_hours=float(metrics[3] or 0),
            avg_cost_per_session=float(metrics[4] or 0),
            avg_energy_per_session=float(metrics[5] or 0)
        )
    
    async def _get_location_breakdown(self, base_query) -> List[LocationMetrics]:
        """Get metrics breakdown by location."""
        result = await self.db.execute(
            select(
                ChargingSession.charging_station_location,
                func.count(ChargingSession.id),
                func.sum(ChargingSession.energy_consumed_kwh),
                func.avg(ChargingSession.charging_cost_usd)
            )
            .select_from(base_query.subquery())
            .group_by(ChargingSession.charging_station_location)
            .order_by(desc(func.count(ChargingSession.id)))
        )
        
        locations = []
        for row in result:
            # Calculate utilization rate (simplified)
            utilization_rate = min(1.0, (row[1] / 1000))  # Assuming max 1000 sessions = 100%
            
            locations.append(LocationMetrics(
                location=row[0],
                session_count=row[1],
                total_energy_kwh=float(row[2] or 0),
                avg_cost_usd=float(row[3] or 0),
                utilization_rate=utilization_rate
            ))
        
        return locations
    
    async def _get_daily_trends(
        self, 
        base_query, 
        start_date: datetime, 
        end_date: datetime
    ) -> List[TimeSeriesData]:
        """Get daily charging trends."""
        result = await self.db.execute(
            select(
                func.date(ChargingSession.charging_start_time),
                func.count(ChargingSession.id)
            )
            .select_from(base_query.subquery())
            .group_by(func.date(ChargingSession.charging_start_time))
            .order_by(func.date(ChargingSession.charging_start_time))
        )
        
        trends = []
        for row in result:
            trends.append(TimeSeriesData(
                timestamp=datetime.combine(row[0], datetime.min.time()),
                value=float(row[1]),
                label="sessions"
            ))
        
        return trends
    
    async def _get_peak_hours(self, base_query) -> List[Dict[str, Any]]:
        """Get peak usage hours."""
        result = await self.db.execute(
            select(
                func.extract('hour', ChargingSession.charging_start_time),
                func.count(ChargingSession.id),
                func.avg(ChargingSession.charging_cost_usd)
            )
            .select_from(base_query.subquery())
            .group_by(func.extract('hour', ChargingSession.charging_start_time))
            .order_by(desc(func.count(ChargingSession.id)))
            .limit(10)
        )
        
        peak_hours = []
        for row in result:
            peak_hours.append({
                'hour': int(row[0]),
                'session_count': row[1],
                'avg_cost': float(row[2] or 0)
            })
        
        return peak_hours
    
    async def _get_user_type_distribution(self, base_query) -> Dict[str, int]:
        """Get user type distribution."""
        result = await self.db.execute(
            select(
                ChargingSession.user_type,
                func.count(ChargingSession.id)
            )
            .select_from(base_query.subquery())
            .group_by(ChargingSession.user_type)
        )
        
        distribution = {}
        for row in result:
            distribution[row[0]] = row[1]
        
        return distribution
    
    async def _get_charger_type_usage(self, base_query) -> Dict[str, int]:
        """Get charger type usage."""
        result = await self.db.execute(
            select(
                ChargingSession.charger_type,
                func.count(ChargingSession.id)
            )
            .select_from(base_query.subquery())
            .group_by(ChargingSession.charger_type)
        )
        
        usage = {}
        for row in result:
            usage[row[0]] = row[1]
        
        return usage
    
    async def get_charging_patterns(
        self,
        start_date: datetime,
        end_date: datetime,
        user_type: Optional[str] = None,
        vehicle_model: Optional[str] = None
    ) -> ChargingPatterns:
        """Analyze charging patterns."""
        base_query = select(ChargingSession).where(
            and_(
                ChargingSession.charging_start_time >= start_date,
                ChargingSession.charging_start_time <= end_date
            )
        )
        
        if user_type:
            base_query = base_query.where(ChargingSession.user_type == user_type)
        if vehicle_model:
            base_query = base_query.where(ChargingSession.vehicle_model.ilike(f"%{vehicle_model}%"))
        
        # Hourly patterns
        hourly_patterns = await self._get_hourly_patterns(base_query)
        
        # Daily patterns
        daily_patterns = await self._get_daily_patterns(base_query)
        
        # Seasonal patterns (simplified)
        seasonal_patterns = await self._get_seasonal_patterns(base_query)
        
        # User behavior patterns
        user_behavior_patterns = await self._get_user_behavior_patterns(base_query)
        
        # Location patterns
        location_patterns = await self._get_location_patterns(base_query)
        
        return ChargingPatterns(
            hourly_patterns=hourly_patterns,
            daily_patterns=daily_patterns,
            seasonal_patterns=seasonal_patterns,
            user_behavior_patterns=user_behavior_patterns,
            location_patterns=location_patterns
        )
    
    async def _get_hourly_patterns(self, base_query) -> ChargingPatternData:
        """Get hourly usage patterns."""
        result = await self.db.execute(
            select(
                func.extract('hour', ChargingSession.charging_start_time),
                func.count(ChargingSession.id),
                func.avg(ChargingSession.charging_duration_hours),
                func.avg(ChargingSession.charging_cost_usd)
            )
            .select_from(base_query.subquery())
            .group_by(func.extract('hour', ChargingSession.charging_start_time))
            .order_by(func.extract('hour', ChargingSession.charging_start_time))
        )
        
        data = []
        for row in result:
            data.append({
                'hour': int(row[0]),
                'session_count': row[1],
                'avg_duration': float(row[2] or 0),
                'avg_cost': float(row[3] or 0)
            })
        
        # Generate insights
        peak_hour = max(data, key=lambda x: x['session_count'])['hour'] if data else 0
        insights = [
            f"Peak usage occurs at {peak_hour}:00",
            "Morning hours (6-9 AM) show high commuter activity",
            "Evening hours (5-8 PM) have increased charging demand"
        ]
        
        return ChargingPatternData(
            pattern_type="hourly",
            data=data,
            insights=insights
        )
    
    async def _get_daily_patterns(self, base_query) -> ChargingPatternData:
        """Get daily usage patterns."""
        result = await self.db.execute(
            select(
                ChargingSession.day_of_week,
                func.count(ChargingSession.id),
                func.avg(ChargingSession.charging_duration_hours)
            )
            .select_from(base_query.subquery())
            .group_by(ChargingSession.day_of_week)
        )
        
        data = []
        for row in result:
            data.append({
                'day': row[0],
                'session_count': row[1],
                'avg_duration': float(row[2] or 0)
            })
        
        insights = [
            "Weekdays show higher charging frequency",
            "Weekend sessions tend to be longer duration",
            "Monday and Friday are peak charging days"
        ]
        
        return ChargingPatternData(
            pattern_type="daily",
            data=data,
            insights=insights
        )
    
    async def _get_seasonal_patterns(self, base_query) -> ChargingPatternData:
        """Get seasonal patterns (simplified)."""
        result = await self.db.execute(
            select(
                func.extract('month', ChargingSession.charging_start_time),
                func.count(ChargingSession.id),
                func.avg(ChargingSession.charging_duration_hours)
            )
            .select_from(base_query.subquery())
            .group_by(func.extract('month', ChargingSession.charging_start_time))
            .order_by(func.extract('month', ChargingSession.charging_start_time))
        )
        
        data = []
        for row in result:
            data.append({
                'month': int(row[0]),
                'session_count': row[1],
                'avg_duration': float(row[2] or 0)
            })
        
        insights = [
            "Winter months show increased charging duration",
            "Summer travel increases charging frequency",
            "Holiday seasons affect charging patterns"
        ]
        
        return ChargingPatternData(
            pattern_type="seasonal",
            data=data,
            insights=insights
        )
    
    async def _get_user_behavior_patterns(self, base_query) -> ChargingPatternData:
        """Get user behavior patterns."""
        result = await self.db.execute(
            select(
                ChargingSession.user_type,
                func.count(ChargingSession.id),
                func.avg(ChargingSession.charging_duration_hours),
                func.avg(ChargingSession.charging_cost_usd)
            )
            .select_from(base_query.subquery())
            .group_by(ChargingSession.user_type)
        )
        
        data = []
        for row in result:
            data.append({
                'user_type': row[0],
                'session_count': row[1],
                'avg_duration': float(row[2] or 0),
                'avg_cost': float(row[3] or 0)
            })
        
        insights = [
            "Commuters prefer shorter, frequent charging sessions",
            "Long-distance travelers use fast charging more often",
            "Casual drivers show varied charging patterns"
        ]
        
        return ChargingPatternData(
            pattern_type="user_behavior",
            data=data,
            insights=insights
        )
    
    async def _get_location_patterns(self, base_query) -> ChargingPatternData:
        """Get location-based patterns."""
        result = await self.db.execute(
            select(
                ChargingSession.charging_station_location,
                func.count(ChargingSession.id),
                func.avg(ChargingSession.charging_duration_hours),
                func.count(func.distinct(ChargingSession.user_id))
            )
            .select_from(base_query.subquery())
            .group_by(ChargingSession.charging_station_location)
            .order_by(desc(func.count(ChargingSession.id)))
            .limit(10)
        )
        
        data = []
        for row in result:
            data.append({
                'location': row[0],
                'session_count': row[1],
                'avg_duration': float(row[2] or 0),
                'unique_users': row[3]
            })
        
        insights = [
            "Urban locations have higher turnover rates",
            "Highway stations see longer charging sessions",
            "Shopping centers show peak weekend usage"
        ]
        
        return ChargingPatternData(
            pattern_type="location",
            data=data,
            insights=insights
        )
