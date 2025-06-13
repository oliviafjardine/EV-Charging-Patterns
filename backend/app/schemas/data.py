"""
Data schemas for API requests and responses.
"""

from pydantic import BaseModel, Field, validator
from typing import Optional, Dict, Any, List
from datetime import datetime


class ChargingSessionBase(BaseModel):
    """Base charging session schema."""
    user_id: str = Field(..., description="User identifier")
    vehicle_model: str = Field(..., description="Vehicle model")
    battery_capacity_kwh: float = Field(..., gt=0, description="Battery capacity in kWh")
    charging_station_id: str = Field(..., description="Charging station identifier")
    charging_station_location: str = Field(..., description="Charging station location")
    charging_start_time: datetime = Field(..., description="Charging start time")
    charging_end_time: datetime = Field(..., description="Charging end time")
    energy_consumed_kwh: Optional[float] = Field(None, ge=0, description="Energy consumed in kWh")
    charging_duration_hours: float = Field(..., gt=0, description="Charging duration in hours")
    charging_rate_kw: Optional[float] = Field(None, gt=0, description="Charging rate in kW")
    charging_cost_usd: float = Field(..., ge=0, description="Charging cost in USD")
    time_of_day: str = Field(..., description="Time of day category")
    day_of_week: str = Field(..., description="Day of the week")
    state_of_charge_start_percent: float = Field(..., ge=0, le=100, description="Starting state of charge")
    state_of_charge_end_percent: float = Field(..., ge=0, le=100, description="Ending state of charge")
    distance_driven_km: Optional[float] = Field(None, ge=0, description="Distance driven since last charge")
    temperature_celsius: float = Field(..., description="Ambient temperature")
    vehicle_age_years: float = Field(..., ge=0, description="Vehicle age in years")
    charger_type: str = Field(..., description="Type of charger")
    user_type: str = Field(..., description="User type category")
    
    @validator('charging_end_time')
    def end_time_after_start_time(cls, v, values):
        if 'charging_start_time' in values and v <= values['charging_start_time']:
            raise ValueError('Charging end time must be after start time')
        return v
    
    @validator('state_of_charge_end_percent')
    def end_charge_greater_than_start(cls, v, values):
        if 'state_of_charge_start_percent' in values and v <= values['state_of_charge_start_percent']:
            raise ValueError('End state of charge must be greater than start state of charge')
        return v


class ChargingSessionCreate(ChargingSessionBase):
    """Schema for creating a charging session."""
    pass


class ChargingSessionResponse(ChargingSessionBase):
    """Schema for charging session response."""
    id: int = Field(..., description="Session ID")
    created_at: datetime = Field(..., description="Record creation time")
    updated_at: datetime = Field(..., description="Record last update time")
    
    class Config:
        from_attributes = True


class ChargingSessionUpdate(BaseModel):
    """Schema for updating a charging session."""
    energy_consumed_kwh: Optional[float] = Field(None, ge=0)
    charging_rate_kw: Optional[float] = Field(None, gt=0)
    charging_cost_usd: Optional[float] = Field(None, ge=0)
    distance_driven_km: Optional[float] = Field(None, ge=0)
    
    class Config:
        from_attributes = True


class DataUploadResponse(BaseModel):
    """Response schema for data upload."""
    filename: str = Field(..., description="Uploaded filename")
    records_processed: int = Field(..., description="Total records processed")
    records_created: int = Field(..., description="Records successfully created")
    records_updated: int = Field(..., description="Records updated")
    records_failed: int = Field(..., description="Records that failed to process")
    message: str = Field(..., description="Upload status message")
    errors: Optional[List[str]] = Field(None, description="List of errors encountered")


class DataExportResponse(BaseModel):
    """Response schema for data export."""
    filename: str = Field(..., description="Export filename")
    format: str = Field(..., description="Export format")
    record_count: int = Field(..., description="Number of records exported")
    file_size_bytes: int = Field(..., description="File size in bytes")
    download_url: str = Field(..., description="Download URL")
    expires_at: datetime = Field(..., description="Download link expiration")


class DataStatistics(BaseModel):
    """Data statistics schema."""
    total_sessions: int = Field(..., description="Total number of charging sessions")
    total_users: int = Field(..., description="Total number of unique users")
    total_stations: int = Field(..., description="Total number of charging stations")
    total_energy_kwh: float = Field(..., description="Total energy consumed")
    total_cost_usd: float = Field(..., description="Total charging costs")
    date_range_start: datetime = Field(..., description="Earliest session date")
    date_range_end: datetime = Field(..., description="Latest session date")
    avg_session_duration_hours: float = Field(..., description="Average session duration")
    avg_session_cost_usd: float = Field(..., description="Average session cost")
    most_popular_location: str = Field(..., description="Most popular charging location")
    most_popular_vehicle_model: str = Field(..., description="Most popular vehicle model")


class DataQualityMetric(BaseModel):
    """Data quality metric."""
    metric_name: str = Field(..., description="Name of the quality metric")
    value: float = Field(..., description="Metric value")
    threshold: float = Field(..., description="Quality threshold")
    status: str = Field(..., description="Status (good, warning, critical)")
    description: str = Field(..., description="Metric description")


class DataQualityReport(BaseModel):
    """Data quality report schema."""
    overall_score: float = Field(..., ge=0, le=100, description="Overall data quality score")
    metrics: List[DataQualityMetric] = Field(..., description="Individual quality metrics")
    missing_data_summary: Dict[str, float] = Field(..., description="Missing data percentages by column")
    outlier_summary: Dict[str, int] = Field(..., description="Number of outliers by column")
    duplicate_records: int = Field(..., description="Number of duplicate records")
    data_freshness_days: float = Field(..., description="Days since last data update")
    recommendations: List[str] = Field(..., description="Data quality improvement recommendations")


class ChargingStationBase(BaseModel):
    """Base charging station schema."""
    station_id: str = Field(..., description="Station identifier")
    location: str = Field(..., description="Station location")
    latitude: Optional[float] = Field(None, description="Latitude coordinate")
    longitude: Optional[float] = Field(None, description="Longitude coordinate")
    charger_types: Optional[str] = Field(None, description="Available charger types (JSON)")
    max_power_kw: Optional[float] = Field(None, gt=0, description="Maximum power output")
    num_connectors: Optional[int] = Field(None, gt=0, description="Number of connectors")
    operator: Optional[str] = Field(None, description="Station operator")
    pricing_model: Optional[str] = Field(None, description="Pricing model")
    is_active: bool = Field(True, description="Whether station is active")


class ChargingStationCreate(ChargingStationBase):
    """Schema for creating a charging station."""
    pass


class ChargingStationResponse(ChargingStationBase):
    """Schema for charging station response."""
    id: int = Field(..., description="Station database ID")
    created_at: datetime = Field(..., description="Record creation time")
    updated_at: datetime = Field(..., description="Record last update time")
    
    class Config:
        from_attributes = True


class VehicleBase(BaseModel):
    """Base vehicle schema."""
    model: str = Field(..., description="Vehicle model")
    manufacturer: Optional[str] = Field(None, description="Vehicle manufacturer")
    battery_capacity_kwh: float = Field(..., gt=0, description="Battery capacity")
    max_charging_rate_kw: Optional[float] = Field(None, gt=0, description="Maximum charging rate")
    range_km: Optional[float] = Field(None, gt=0, description="Vehicle range")
    efficiency_kwh_per_100km: Optional[float] = Field(None, gt=0, description="Energy efficiency")
    vehicle_type: Optional[str] = Field(None, description="Vehicle type (sedan, SUV, etc.)")


class VehicleCreate(VehicleBase):
    """Schema for creating a vehicle."""
    pass


class VehicleResponse(VehicleBase):
    """Schema for vehicle response."""
    id: int = Field(..., description="Vehicle database ID")
    created_at: datetime = Field(..., description="Record creation time")
    updated_at: datetime = Field(..., description="Record last update time")
    
    class Config:
        from_attributes = True
