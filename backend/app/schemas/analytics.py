"""
Analytics schemas for API responses.
"""

from pydantic import BaseModel, Field
from typing import List, Dict, Optional, Any
from datetime import datetime


class ChargingMetrics(BaseModel):
    """Basic charging metrics."""
    total_sessions: int = Field(..., description="Total number of charging sessions")
    total_energy_kwh: float = Field(..., description="Total energy consumed in kWh")
    total_cost_usd: float = Field(..., description="Total cost in USD")
    avg_duration_hours: float = Field(..., description="Average charging duration in hours")
    avg_cost_per_session: float = Field(..., description="Average cost per session")
    avg_energy_per_session: float = Field(..., description="Average energy per session")


class LocationMetrics(BaseModel):
    """Location-based metrics."""
    location: str = Field(..., description="Location name")
    session_count: int = Field(..., description="Number of sessions")
    total_energy_kwh: float = Field(..., description="Total energy consumed")
    avg_cost_usd: float = Field(..., description="Average cost")
    utilization_rate: float = Field(..., description="Station utilization rate")


class TimeSeriesData(BaseModel):
    """Time series data point."""
    timestamp: datetime = Field(..., description="Data timestamp")
    value: float = Field(..., description="Data value")
    label: Optional[str] = Field(None, description="Data label")


class AnalyticsOverview(BaseModel):
    """Analytics overview response."""
    period_start: datetime = Field(..., description="Analysis period start")
    period_end: datetime = Field(..., description="Analysis period end")
    overall_metrics: ChargingMetrics = Field(..., description="Overall charging metrics")
    location_breakdown: List[LocationMetrics] = Field(..., description="Metrics by location")
    daily_trends: List[TimeSeriesData] = Field(..., description="Daily trend data")
    peak_hours: List[Dict[str, Any]] = Field(..., description="Peak usage hours")
    user_type_distribution: Dict[str, int] = Field(..., description="Distribution by user type")
    charger_type_usage: Dict[str, int] = Field(..., description="Usage by charger type")


class ChargingPatternData(BaseModel):
    """Charging pattern data."""
    pattern_type: str = Field(..., description="Type of pattern")
    data: List[Dict[str, Any]] = Field(..., description="Pattern data")
    insights: List[str] = Field(..., description="Key insights")


class ChargingPatterns(BaseModel):
    """Charging patterns analysis response."""
    hourly_patterns: ChargingPatternData = Field(..., description="Hourly usage patterns")
    daily_patterns: ChargingPatternData = Field(..., description="Daily usage patterns")
    seasonal_patterns: ChargingPatternData = Field(..., description="Seasonal patterns")
    user_behavior_patterns: ChargingPatternData = Field(..., description="User behavior patterns")
    location_patterns: ChargingPatternData = Field(..., description="Location-based patterns")


class CostBreakdown(BaseModel):
    """Cost breakdown data."""
    category: str = Field(..., description="Cost category")
    amount: float = Field(..., description="Amount in USD")
    percentage: float = Field(..., description="Percentage of total")
    sessions: int = Field(..., description="Number of sessions")


class CostAnalysis(BaseModel):
    """Cost analysis response."""
    total_cost: float = Field(..., description="Total cost in USD")
    avg_cost_per_kwh: float = Field(..., description="Average cost per kWh")
    cost_by_location: List[CostBreakdown] = Field(..., description="Cost breakdown by location")
    cost_by_charger_type: List[CostBreakdown] = Field(..., description="Cost by charger type")
    cost_by_time_of_day: List[CostBreakdown] = Field(..., description="Cost by time of day")
    cost_trends: List[TimeSeriesData] = Field(..., description="Cost trend over time")
    cost_optimization_suggestions: List[str] = Field(..., description="Cost optimization tips")


class DemandPrediction(BaseModel):
    """Demand prediction data."""
    timestamp: datetime = Field(..., description="Prediction timestamp")
    predicted_demand: float = Field(..., description="Predicted demand level")
    confidence_interval_lower: float = Field(..., description="Lower confidence bound")
    confidence_interval_upper: float = Field(..., description="Upper confidence bound")
    location: Optional[str] = Field(None, description="Location if location-specific")


class DemandForecast(BaseModel):
    """Demand forecast response."""
    forecast_period_days: int = Field(..., description="Forecast period in days")
    predictions: List[DemandPrediction] = Field(..., description="Demand predictions")
    peak_demand_times: List[Dict[str, Any]] = Field(..., description="Predicted peak times")
    capacity_recommendations: List[str] = Field(..., description="Capacity recommendations")
    model_accuracy: float = Field(..., description="Model accuracy score")


class UserCluster(BaseModel):
    """User behavior cluster."""
    cluster_id: int = Field(..., description="Cluster identifier")
    cluster_name: str = Field(..., description="Cluster name/description")
    user_count: int = Field(..., description="Number of users in cluster")
    characteristics: Dict[str, Any] = Field(..., description="Cluster characteristics")
    avg_sessions_per_month: float = Field(..., description="Average sessions per month")
    avg_cost_per_month: float = Field(..., description="Average cost per month")


class UserBehaviorAnalysis(BaseModel):
    """User behavior analysis response."""
    total_users: int = Field(..., description="Total number of users analyzed")
    user_clusters: List[UserCluster] = Field(..., description="User behavior clusters")
    retention_metrics: Dict[str, float] = Field(..., description="User retention metrics")
    usage_frequency_distribution: Dict[str, int] = Field(..., description="Usage frequency distribution")
    loyalty_analysis: Dict[str, Any] = Field(..., description="User loyalty analysis")
    churn_risk_analysis: Dict[str, Any] = Field(..., description="Churn risk analysis")
