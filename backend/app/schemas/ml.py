"""
Machine Learning schemas for API requests and responses.
"""

from pydantic import BaseModel, Field, validator
from typing import Optional, Dict, Any, List
from datetime import datetime
from enum import Enum


class ChargerType(str, Enum):
    """Charger type enumeration."""
    LEVEL_1 = "Level 1"
    LEVEL_2 = "Level 2"
    DC_FAST_CHARGER = "DC Fast Charger"


class UserType(str, Enum):
    """User type enumeration."""
    COMMUTER = "Commuter"
    CASUAL_DRIVER = "Casual Driver"
    LONG_DISTANCE_TRAVELER = "Long-Distance Traveler"


class TimeOfDay(str, Enum):
    """Time of day enumeration."""
    MORNING = "Morning"
    AFTERNOON = "Afternoon"
    EVENING = "Evening"
    NIGHT = "Night"


class DurationPredictionRequest(BaseModel):
    """Request schema for charging duration prediction."""
    vehicle_model: str = Field(..., description="Vehicle model")
    battery_capacity_kwh: float = Field(..., gt=0, description="Battery capacity in kWh")
    state_of_charge_start_percent: float = Field(..., ge=0, le=100, description="Starting state of charge")
    state_of_charge_target_percent: float = Field(..., ge=0, le=100, description="Target state of charge")
    charger_type: ChargerType = Field(..., description="Type of charger")
    temperature_celsius: float = Field(..., description="Ambient temperature")
    vehicle_age_years: float = Field(..., ge=0, description="Vehicle age in years")
    
    @validator('state_of_charge_target_percent')
    def target_must_be_greater_than_start(cls, v, values):
        if 'state_of_charge_start_percent' in values and v <= values['state_of_charge_start_percent']:
            raise ValueError('Target state of charge must be greater than starting state of charge')
        return v


class DurationPredictionResponse(BaseModel):
    """Response schema for charging duration prediction."""
    predicted_duration_hours: float = Field(..., description="Predicted charging duration in hours")
    confidence_score: float = Field(..., ge=0, le=1, description="Prediction confidence score")
    estimated_energy_kwh: float = Field(..., description="Estimated energy consumption")
    factors_analysis: Dict[str, float] = Field(..., description="Feature importance analysis")
    model_version: str = Field(..., description="Model version used")


class CostPredictionRequest(BaseModel):
    """Request schema for charging cost prediction."""
    location: str = Field(..., description="Charging location")
    charger_type: ChargerType = Field(..., description="Type of charger")
    energy_needed_kwh: float = Field(..., gt=0, description="Energy needed in kWh")
    time_of_day: TimeOfDay = Field(..., description="Time of day for charging")
    day_of_week: str = Field(..., description="Day of the week")
    user_type: UserType = Field(..., description="User type")
    duration_hours: Optional[float] = Field(None, gt=0, description="Expected duration in hours")


class CostPredictionResponse(BaseModel):
    """Response schema for charging cost prediction."""
    predicted_cost_usd: float = Field(..., description="Predicted charging cost in USD")
    cost_per_kwh: float = Field(..., description="Cost per kWh")
    confidence_score: float = Field(..., ge=0, le=1, description="Prediction confidence score")
    cost_breakdown: Dict[str, float] = Field(..., description="Cost breakdown by factors")
    optimization_suggestions: List[str] = Field(..., description="Cost optimization suggestions")
    model_version: str = Field(..., description="Model version used")


class ModelStatus(BaseModel):
    """Model status information."""
    model_name: str = Field(..., description="Model name")
    model_type: str = Field(..., description="Model type")
    version: str = Field(..., description="Model version")
    is_active: bool = Field(..., description="Whether model is active")
    training_date: datetime = Field(..., description="Last training date")
    performance_score: Optional[float] = Field(None, description="Model performance score")
    training_data_size: Optional[int] = Field(None, description="Training data size")
    status: str = Field(..., description="Model status (healthy, degraded, failed)")


class ModelPerformance(BaseModel):
    """Model performance metrics."""
    model_name: str = Field(..., description="Model name")
    version: str = Field(..., description="Model version")
    metrics: Dict[str, float] = Field(..., description="Performance metrics")
    validation_score: float = Field(..., description="Validation score")
    test_score: Optional[float] = Field(None, description="Test score")
    feature_importance: Dict[str, float] = Field(..., description="Feature importance scores")
    training_history: List[Dict[str, Any]] = Field(..., description="Training history")
    last_evaluation_date: datetime = Field(..., description="Last evaluation date")


class TrainingRequest(BaseModel):
    """Request schema for model training."""
    retrain_from_scratch: bool = Field(False, description="Whether to retrain from scratch")
    data_start_date: Optional[datetime] = Field(None, description="Training data start date")
    data_end_date: Optional[datetime] = Field(None, description="Training data end date")
    hyperparameters: Optional[Dict[str, Any]] = Field(None, description="Custom hyperparameters")
    validation_split: float = Field(0.2, ge=0.1, le=0.5, description="Validation data split ratio")


class TrainingResponse(BaseModel):
    """Response schema for model training."""
    task_id: str = Field(..., description="Training task ID")
    model_name: str = Field(..., description="Model name")
    status: str = Field(..., description="Training status")
    message: str = Field(..., description="Status message")
    estimated_completion_time: Optional[datetime] = Field(None, description="Estimated completion time")


class PredictionInput(BaseModel):
    """Generic prediction input."""
    features: Dict[str, Any] = Field(..., description="Input features")
    model_name: str = Field(..., description="Model to use for prediction")


class PredictionOutput(BaseModel):
    """Generic prediction output."""
    prediction: Any = Field(..., description="Prediction result")
    confidence: Optional[float] = Field(None, description="Prediction confidence")
    model_version: str = Field(..., description="Model version used")
    processing_time_ms: float = Field(..., description="Processing time in milliseconds")
