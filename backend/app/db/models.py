"""
Database models for EV charging analytics.
"""

from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean, Text, ForeignKey, Index
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from datetime import datetime
from typing import Optional

from app.core.database import Base


class ChargingSession(Base):
    """Charging session data model."""
    
    __tablename__ = "charging_sessions"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String, index=True, nullable=False)
    vehicle_model = Column(String, nullable=False)
    battery_capacity_kwh = Column(Float, nullable=False)
    charging_station_id = Column(String, index=True, nullable=False)
    charging_station_location = Column(String, nullable=False)
    charging_start_time = Column(DateTime, nullable=False)
    charging_end_time = Column(DateTime, nullable=False)
    energy_consumed_kwh = Column(Float, nullable=True)
    charging_duration_hours = Column(Float, nullable=False)
    charging_rate_kw = Column(Float, nullable=True)
    charging_cost_usd = Column(Float, nullable=False)
    time_of_day = Column(String, nullable=False)
    day_of_week = Column(String, nullable=False)
    state_of_charge_start_percent = Column(Float, nullable=False)
    state_of_charge_end_percent = Column(Float, nullable=False)
    distance_driven_km = Column(Float, nullable=True)
    temperature_celsius = Column(Float, nullable=False)
    vehicle_age_years = Column(Float, nullable=False)
    charger_type = Column(String, nullable=False)
    user_type = Column(String, nullable=False)
    
    # Metadata
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    # Indexes for better query performance
    __table_args__ = (
        Index('idx_charging_sessions_user_time', 'user_id', 'charging_start_time'),
        Index('idx_charging_sessions_station_time', 'charging_station_id', 'charging_start_time'),
        Index('idx_charging_sessions_location_time', 'charging_station_location', 'charging_start_time'),
    )


class ChargingStation(Base):
    """Charging station information."""
    
    __tablename__ = "charging_stations"
    
    id = Column(Integer, primary_key=True, index=True)
    station_id = Column(String, unique=True, index=True, nullable=False)
    location = Column(String, nullable=False)
    latitude = Column(Float, nullable=True)
    longitude = Column(Float, nullable=True)
    charger_types = Column(Text, nullable=True)  # JSON string
    max_power_kw = Column(Float, nullable=True)
    num_connectors = Column(Integer, nullable=True)
    operator = Column(String, nullable=True)
    pricing_model = Column(String, nullable=True)
    is_active = Column(Boolean, default=True)
    
    # Metadata
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())


class Vehicle(Base):
    """Vehicle information."""
    
    __tablename__ = "vehicles"
    
    id = Column(Integer, primary_key=True, index=True)
    model = Column(String, nullable=False)
    manufacturer = Column(String, nullable=True)
    battery_capacity_kwh = Column(Float, nullable=False)
    max_charging_rate_kw = Column(Float, nullable=True)
    range_km = Column(Float, nullable=True)
    efficiency_kwh_per_100km = Column(Float, nullable=True)
    vehicle_type = Column(String, nullable=True)  # sedan, suv, etc.
    
    # Metadata
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())


class User(Base):
    """User information."""
    
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String, unique=True, index=True, nullable=False)
    user_type = Column(String, nullable=False)  # Commuter, Casual Driver, etc.
    registration_date = Column(DateTime, nullable=True)
    preferred_charging_locations = Column(Text, nullable=True)  # JSON string
    avg_daily_distance_km = Column(Float, nullable=True)
    home_location = Column(String, nullable=True)
    
    # Metadata
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())


class MLModel(Base):
    """ML model metadata and performance tracking."""
    
    __tablename__ = "ml_models"
    
    id = Column(Integer, primary_key=True, index=True)
    model_name = Column(String, nullable=False)
    model_type = Column(String, nullable=False)  # duration_prediction, cost_optimization, etc.
    version = Column(String, nullable=False)
    file_path = Column(String, nullable=False)
    training_data_size = Column(Integer, nullable=True)
    training_date = Column(DateTime, nullable=False)
    performance_metrics = Column(Text, nullable=True)  # JSON string
    is_active = Column(Boolean, default=True)
    
    # Metadata
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())


class Prediction(Base):
    """Store prediction results for analysis."""
    
    __tablename__ = "predictions"
    
    id = Column(Integer, primary_key=True, index=True)
    model_id = Column(Integer, ForeignKey("ml_models.id"), nullable=False)
    prediction_type = Column(String, nullable=False)
    input_features = Column(Text, nullable=False)  # JSON string
    prediction_result = Column(Text, nullable=False)  # JSON string
    confidence_score = Column(Float, nullable=True)
    actual_result = Column(Text, nullable=True)  # JSON string for comparison
    
    # Relationships
    model = relationship("MLModel", backref="predictions")
    
    # Metadata
    created_at = Column(DateTime, default=func.now())


class AnalyticsReport(Base):
    """Store generated analytics reports."""
    
    __tablename__ = "analytics_reports"
    
    id = Column(Integer, primary_key=True, index=True)
    report_type = Column(String, nullable=False)
    report_date = Column(DateTime, nullable=False)
    data_period_start = Column(DateTime, nullable=False)
    data_period_end = Column(DateTime, nullable=False)
    report_data = Column(Text, nullable=False)  # JSON string
    file_path = Column(String, nullable=True)
    
    # Metadata
    created_at = Column(DateTime, default=func.now())
