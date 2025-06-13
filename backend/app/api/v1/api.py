"""
API v1 router configuration.
"""

from fastapi import APIRouter

from app.api.v1.endpoints import (
    analytics,
    data,
    ml,
    stations,
    users,
    vehicles
)

api_router = APIRouter()

# Include all endpoint routers
api_router.include_router(
    analytics.router, 
    prefix="/analytics", 
    tags=["analytics"]
)

api_router.include_router(
    data.router, 
    prefix="/data", 
    tags=["data"]
)

api_router.include_router(
    ml.router, 
    prefix="/ml", 
    tags=["machine-learning"]
)

api_router.include_router(
    stations.router, 
    prefix="/stations", 
    tags=["charging-stations"]
)

api_router.include_router(
    users.router, 
    prefix="/users", 
    tags=["users"]
)

api_router.include_router(
    vehicles.router, 
    prefix="/vehicles", 
    tags=["vehicles"]
)
