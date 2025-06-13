"""
Simplified main application for demo purposes.
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict, Any
import json
from datetime import datetime, timedelta
import random

# Create FastAPI app
app = FastAPI(
    title="EV Charging Analytics Platform API",
    description="Electric Vehicle Charging Analytics Platform - Demo Version",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Sample data
sample_sessions = [
    {
        "id": 1,
        "user_id": "U001",
        "vehicle_model": "Tesla Model 3",
        "battery_capacity_kwh": 75,
        "charging_station_location": "Downtown Mall",
        "charging_start_time": "2024-01-15T08:30:00",
        "charging_end_time": "2024-01-15T10:15:00",
        "energy_consumed_kwh": 45,
        "charging_duration_hours": 1.75,
        "charging_cost_usd": 12.50,
        "time_of_day": "Morning",
        "day_of_week": "Monday",
        "charger_type": "Level 2",
        "user_type": "Commuter"
    },
    {
        "id": 2,
        "user_id": "U002",
        "vehicle_model": "Nissan Leaf",
        "battery_capacity_kwh": 40,
        "charging_station_location": "Highway Rest Stop",
        "charging_start_time": "2024-01-15T14:20:00",
        "charging_end_time": "2024-01-15T14:50:00",
        "energy_consumed_kwh": 24,
        "charging_duration_hours": 0.5,
        "charging_cost_usd": 18.00,
        "time_of_day": "Afternoon",
        "day_of_week": "Monday",
        "charger_type": "DC Fast Charger",
        "user_type": "Long-Distance Traveler"
    }
]

# Pydantic models
class AnalyticsOverview(BaseModel):
    period_start: datetime
    period_end: datetime
    overall_metrics: Dict[str, Any]
    location_breakdown: List[Dict[str, Any]]
    daily_trends: List[Dict[str, Any]]
    peak_hours: List[Dict[str, Any]]
    user_type_distribution: Dict[str, int]
    charger_type_usage: Dict[str, int]

class DurationPredictionRequest(BaseModel):
    vehicle_model: str
    battery_capacity_kwh: float
    state_of_charge_start_percent: float
    state_of_charge_target_percent: float
    charger_type: str
    temperature_celsius: float
    vehicle_age_years: float

class DurationPredictionResponse(BaseModel):
    predicted_duration_hours: float
    confidence_score: float
    estimated_energy_kwh: float
    factors_analysis: Dict[str, float]
    model_version: str

# Routes
@app.get("/")
async def root():
    return {
        "message": "Welcome to EV Charging Analytics Platform API",
        "version": "1.0.0",
        "status": "running",
        "timestamp": datetime.now().isoformat()
    }

@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "services": {
            "api": "running",
            "database": "connected",
            "cache": "connected"
        }
    }

@app.get("/api/v1/analytics/overview")
async def get_analytics_overview():
    """Get analytics overview with sample data."""
    end_date = datetime.now()
    start_date = end_date - timedelta(days=30)
    
    # Generate sample analytics data
    overview = AnalyticsOverview(
        period_start=start_date,
        period_end=end_date,
        overall_metrics={
            "total_sessions": 127,
            "total_energy_kwh": 3450.5,
            "total_cost_usd": 1250.75,
            "avg_duration_hours": 2.3,
            "avg_cost_per_session": 9.85,
            "avg_energy_per_session": 27.2
        },
        location_breakdown=[
            {
                "location": "Downtown Mall",
                "session_count": 45,
                "total_energy_kwh": 1200.5,
                "avg_cost_usd": 8.50,
                "utilization_rate": 0.85
            },
            {
                "location": "Highway Rest Stop",
                "session_count": 32,
                "total_energy_kwh": 980.2,
                "avg_cost_usd": 12.30,
                "utilization_rate": 0.72
            },
            {
                "location": "Shopping Center",
                "session_count": 28,
                "total_energy_kwh": 750.8,
                "avg_cost_usd": 7.90,
                "utilization_rate": 0.68
            },
            {
                "location": "Office Complex",
                "session_count": 22,
                "total_energy_kwh": 519.0,
                "avg_cost_usd": 6.20,
                "utilization_rate": 0.55
            }
        ],
        daily_trends=[
            {
                "timestamp": (start_date + timedelta(days=i)).isoformat(),
                "value": random.randint(8, 25),
                "label": "sessions"
            } for i in range(30)
        ],
        peak_hours=[
            {"hour": 8, "session_count": 15, "avg_cost": 8.50},
            {"hour": 17, "session_count": 18, "avg_cost": 9.20},
            {"hour": 12, "session_count": 12, "avg_cost": 10.80},
            {"hour": 19, "session_count": 14, "avg_cost": 7.90},
            {"hour": 9, "session_count": 11, "avg_cost": 8.10}
        ],
        user_type_distribution={
            "Commuter": 65,
            "Casual Driver": 38,
            "Long-Distance Traveler": 24
        },
        charger_type_usage={
            "Level 2": 89,
            "DC Fast Charger": 28,
            "Level 1": 10
        }
    )
    
    return overview

@app.post("/api/v1/ml/predict/duration")
async def predict_duration(request: DurationPredictionRequest):
    """Predict charging duration with mock ML model."""
    # Simple mock prediction logic
    energy_needed = (
        request.battery_capacity_kwh * 
        (request.state_of_charge_target_percent - request.state_of_charge_start_percent) / 100
    )
    
    # Mock charging rate based on charger type
    charging_rates = {
        "Level 1": 1.4,
        "Level 2": 7.2,
        "DC Fast Charger": 50.0
    }
    
    charging_rate = charging_rates.get(request.charger_type, 7.2)
    predicted_duration = energy_needed / charging_rate
    
    # Add some randomness and factors
    temperature_factor = 1.0 + (20 - request.temperature_celsius) * 0.01
    age_factor = 1.0 + request.vehicle_age_years * 0.02
    
    predicted_duration *= temperature_factor * age_factor
    
    response = DurationPredictionResponse(
        predicted_duration_hours=round(predicted_duration, 2),
        confidence_score=0.87,
        estimated_energy_kwh=round(energy_needed, 1),
        factors_analysis={
            "charger_type": 0.45,
            "energy_needed": 0.35,
            "temperature": 0.12,
            "vehicle_age": 0.08
        },
        model_version="1.0-demo"
    )
    
    return response

@app.get("/api/v1/data/sessions")
async def get_charging_sessions():
    """Get charging sessions."""
    return sample_sessions

@app.get("/api/v1/data/statistics")
async def get_data_statistics():
    """Get data statistics."""
    return {
        "total_sessions": 127,
        "total_users": 45,
        "total_stations": 12,
        "total_energy_kwh": 3450.5,
        "total_cost_usd": 1250.75,
        "date_range_start": "2024-01-01T00:00:00",
        "date_range_end": "2024-01-31T23:59:59",
        "avg_session_duration_hours": 2.3,
        "avg_session_cost_usd": 9.85,
        "most_popular_location": "Downtown Mall",
        "most_popular_vehicle_model": "Tesla Model 3"
    }

@app.get("/api/v1/data/quality-report")
async def get_data_quality_report():
    """Get data quality report."""
    return {
        "overall_score": 92.5,
        "metrics": [
            {
                "metric_name": "Data Completeness",
                "value": 95.2,
                "threshold": 95.0,
                "status": "good",
                "description": "Percentage of complete records"
            },
            {
                "metric_name": "Duplicate Records",
                "value": 0,
                "threshold": 0.0,
                "status": "good",
                "description": "Number of duplicate records found"
            },
            {
                "metric_name": "Data Freshness",
                "value": 2.0,
                "threshold": 7.0,
                "status": "good",
                "description": "Days since last data update"
            }
        ],
        "missing_data_summary": {
            "energy_consumed_kwh": 2.1,
            "charging_rate_kw": 5.3,
            "distance_driven_km": 8.7
        },
        "outlier_summary": {},
        "duplicate_records": 0,
        "data_freshness_days": 2.0,
        "recommendations": [
            "Data quality is excellent",
            "Continue current data collection practices"
        ]
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
