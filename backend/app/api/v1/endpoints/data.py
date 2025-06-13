"""
Data management API endpoints.
"""

from fastapi import APIRouter, Depends, HTTPException, Query, UploadFile, File
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional, List
from datetime import datetime
import pandas as pd
import io
import logging

from app.core.database import get_db
from app.core.redis import cache, get_cache_key
from app.core.config import settings
from app.services.data_service import DataService
from app.schemas.data import (
    ChargingSessionResponse,
    ChargingSessionCreate,
    DataUploadResponse,
    DataExportResponse
)

router = APIRouter()
logger = logging.getLogger(__name__)


@router.get("/sessions", response_model=List[ChargingSessionResponse])
async def get_charging_sessions(
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Number of records to return"),
    start_date: Optional[datetime] = Query(None, description="Filter by start date"),
    end_date: Optional[datetime] = Query(None, description="Filter by end date"),
    location: Optional[str] = Query(None, description="Filter by location"),
    user_type: Optional[str] = Query(None, description="Filter by user type"),
    vehicle_model: Optional[str] = Query(None, description="Filter by vehicle model"),
    db: AsyncSession = Depends(get_db)
):
    """Get charging sessions with optional filters."""
    try:
        data_service = DataService(db)
        sessions = await data_service.get_charging_sessions(
            skip=skip,
            limit=limit,
            start_date=start_date,
            end_date=end_date,
            location=location,
            user_type=user_type,
            vehicle_model=vehicle_model
        )
        return sessions
        
    except Exception as e:
        logger.error(f"Error getting charging sessions: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve charging sessions")


@router.post("/sessions", response_model=ChargingSessionResponse)
async def create_charging_session(
    session_data: ChargingSessionCreate,
    db: AsyncSession = Depends(get_db)
):
    """Create a new charging session."""
    try:
        data_service = DataService(db)
        session = await data_service.create_charging_session(session_data)
        return session
        
    except Exception as e:
        logger.error(f"Error creating charging session: {e}")
        raise HTTPException(status_code=500, detail="Failed to create charging session")


@router.post("/upload", response_model=DataUploadResponse)
async def upload_data(
    file: UploadFile = File(..., description="CSV file with charging data"),
    db: AsyncSession = Depends(get_db)
):
    """Upload charging data from CSV file."""
    try:
        # Validate file type
        if not file.filename.endswith('.csv'):
            raise HTTPException(status_code=400, detail="Only CSV files are supported")
        
        # Read file content
        content = await file.read()
        df = pd.read_csv(io.StringIO(content.decode('utf-8')))
        
        # Validate required columns
        required_columns = [
            'user_id', 'vehicle_model', 'battery_capacity_kwh',
            'charging_station_id', 'charging_station_location',
            'charging_start_time', 'charging_end_time',
            'charging_duration_hours', 'charging_cost_usd'
        ]
        
        missing_columns = [col for col in required_columns if col not in df.columns]
        if missing_columns:
            raise HTTPException(
                status_code=400, 
                detail=f"Missing required columns: {missing_columns}"
            )
        
        # Process data
        data_service = DataService(db)
        result = await data_service.upload_charging_data(df)
        
        return DataUploadResponse(
            filename=file.filename,
            records_processed=len(df),
            records_created=result['created'],
            records_updated=result['updated'],
            records_failed=result['failed'],
            message="Data uploaded successfully"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error uploading data: {e}")
        raise HTTPException(status_code=500, detail="Failed to upload data")


@router.get("/export", response_model=DataExportResponse)
async def export_data(
    format: str = Query("csv", regex="^(csv|json|parquet)$", description="Export format"),
    start_date: Optional[datetime] = Query(None, description="Start date for export"),
    end_date: Optional[datetime] = Query(None, description="End date for export"),
    location: Optional[str] = Query(None, description="Filter by location"),
    db: AsyncSession = Depends(get_db)
):
    """Export charging data in specified format."""
    try:
        data_service = DataService(db)
        export_result = await data_service.export_charging_data(
            format=format,
            start_date=start_date,
            end_date=end_date,
            location=location
        )
        
        return export_result
        
    except Exception as e:
        logger.error(f"Error exporting data: {e}")
        raise HTTPException(status_code=500, detail="Failed to export data")


@router.get("/statistics")
async def get_data_statistics(db: AsyncSession = Depends(get_db)):
    """Get basic statistics about the data."""
    try:
        cache_key = await get_cache_key("data_statistics")
        cached_result = await cache.get(cache_key)
        if cached_result:
            return cached_result
        
        data_service = DataService(db)
        stats = await data_service.get_data_statistics()
        
        await cache.set(cache_key, stats, ttl=settings.CACHE_TTL_MEDIUM)
        return stats
        
    except Exception as e:
        logger.error(f"Error getting data statistics: {e}")
        raise HTTPException(status_code=500, detail="Failed to get data statistics")


@router.get("/quality-report")
async def get_data_quality_report(db: AsyncSession = Depends(get_db)):
    """Get data quality report."""
    try:
        cache_key = await get_cache_key("data_quality_report")
        cached_result = await cache.get(cache_key)
        if cached_result:
            return cached_result
        
        data_service = DataService(db)
        quality_report = await data_service.get_data_quality_report()
        
        await cache.set(cache_key, quality_report, ttl=settings.CACHE_TTL_LONG)
        return quality_report
        
    except Exception as e:
        logger.error(f"Error getting data quality report: {e}")
        raise HTTPException(status_code=500, detail="Failed to get data quality report")


@router.delete("/sessions/{session_id}")
async def delete_charging_session(
    session_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Delete a charging session."""
    try:
        data_service = DataService(db)
        success = await data_service.delete_charging_session(session_id)
        
        if not success:
            raise HTTPException(status_code=404, detail="Charging session not found")
        
        return {"message": "Charging session deleted successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting charging session: {e}")
        raise HTTPException(status_code=500, detail="Failed to delete charging session")


@router.post("/validate")
async def validate_data(
    file: UploadFile = File(..., description="CSV file to validate"),
):
    """Validate data format without uploading."""
    try:
        if not file.filename.endswith('.csv'):
            raise HTTPException(status_code=400, detail="Only CSV files are supported")
        
        content = await file.read()
        df = pd.read_csv(io.StringIO(content.decode('utf-8')))
        
        # Validate columns and data types
        validation_results = {
            "filename": file.filename,
            "total_rows": len(df),
            "total_columns": len(df.columns),
            "columns": df.columns.tolist(),
            "missing_values": df.isnull().sum().to_dict(),
            "data_types": df.dtypes.astype(str).to_dict(),
            "validation_errors": [],
            "warnings": []
        }
        
        # Check required columns
        required_columns = [
            'user_id', 'vehicle_model', 'battery_capacity_kwh',
            'charging_station_id', 'charging_station_location',
            'charging_start_time', 'charging_end_time'
        ]
        
        missing_columns = [col for col in required_columns if col not in df.columns]
        if missing_columns:
            validation_results["validation_errors"].append(
                f"Missing required columns: {missing_columns}"
            )
        
        # Check for negative values in numeric columns
        numeric_columns = ['battery_capacity_kwh', 'charging_duration_hours', 'charging_cost_usd']
        for col in numeric_columns:
            if col in df.columns and (df[col] < 0).any():
                validation_results["warnings"].append(
                    f"Negative values found in {col}"
                )
        
        # Check date format
        date_columns = ['charging_start_time', 'charging_end_time']
        for col in date_columns:
            if col in df.columns:
                try:
                    pd.to_datetime(df[col])
                except:
                    validation_results["validation_errors"].append(
                        f"Invalid date format in {col}"
                    )
        
        validation_results["is_valid"] = len(validation_results["validation_errors"]) == 0
        
        return validation_results
        
    except Exception as e:
        logger.error(f"Error validating data: {e}")
        raise HTTPException(status_code=500, detail="Failed to validate data")
