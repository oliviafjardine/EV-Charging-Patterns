"""
Data service for managing charging session data.
"""

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, or_, desc
from sqlalchemy.orm import selectinload
from typing import List, Optional, Dict, Any
from datetime import datetime
import pandas as pd
import logging
import os
import json

from app.db.models import ChargingSession, ChargingStation, Vehicle, User
from app.schemas.data import (
    ChargingSessionResponse,
    ChargingSessionCreate,
    DataUploadResponse,
    DataExportResponse,
    DataStatistics,
    DataQualityReport,
    DataQualityMetric
)
from app.core.config import settings

logger = logging.getLogger(__name__)


class DataService:
    """Service for data management operations."""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def get_charging_sessions(
        self,
        skip: int = 0,
        limit: int = 100,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        location: Optional[str] = None,
        user_type: Optional[str] = None,
        vehicle_model: Optional[str] = None
    ) -> List[ChargingSessionResponse]:
        """Get charging sessions with optional filters."""
        query = select(ChargingSession)
        
        # Apply filters
        filters = []
        if start_date:
            filters.append(ChargingSession.charging_start_time >= start_date)
        if end_date:
            filters.append(ChargingSession.charging_start_time <= end_date)
        if location:
            filters.append(ChargingSession.charging_station_location.ilike(f"%{location}%"))
        if user_type:
            filters.append(ChargingSession.user_type == user_type)
        if vehicle_model:
            filters.append(ChargingSession.vehicle_model.ilike(f"%{vehicle_model}%"))
        
        if filters:
            query = query.where(and_(*filters))
        
        # Apply pagination and ordering
        query = query.order_by(desc(ChargingSession.charging_start_time)).offset(skip).limit(limit)
        
        result = await self.db.execute(query)
        sessions = result.scalars().all()
        
        return [ChargingSessionResponse.from_orm(session) for session in sessions]
    
    async def create_charging_session(
        self, 
        session_data: ChargingSessionCreate
    ) -> ChargingSessionResponse:
        """Create a new charging session."""
        session = ChargingSession(**session_data.dict())
        self.db.add(session)
        await self.db.commit()
        await self.db.refresh(session)
        
        return ChargingSessionResponse.from_orm(session)
    
    async def upload_charging_data(self, df: pd.DataFrame) -> Dict[str, int]:
        """Upload charging data from DataFrame."""
        created = 0
        updated = 0
        failed = 0
        
        for _, row in df.iterrows():
            try:
                # Check if session already exists
                existing_query = select(ChargingSession).where(
                    and_(
                        ChargingSession.user_id == str(row['user_id']),
                        ChargingSession.charging_start_time == pd.to_datetime(row['charging_start_time'])
                    )
                )
                result = await self.db.execute(existing_query)
                existing_session = result.scalar_one_or_none()
                
                if existing_session:
                    # Update existing session
                    for key, value in row.items():
                        if hasattr(existing_session, key):
                            setattr(existing_session, key, value)
                    updated += 1
                else:
                    # Create new session
                    session_data = self._row_to_session_dict(row)
                    session = ChargingSession(**session_data)
                    self.db.add(session)
                    created += 1
                    
            except Exception as e:
                logger.error(f"Error processing row: {e}")
                failed += 1
                continue
        
        await self.db.commit()
        
        return {
            'created': created,
            'updated': updated,
            'failed': failed
        }
    
    def _row_to_session_dict(self, row: pd.Series) -> Dict[str, Any]:
        """Convert DataFrame row to session dictionary."""
        return {
            'user_id': str(row['user_id']),
            'vehicle_model': str(row['vehicle_model']),
            'battery_capacity_kwh': float(row['battery_capacity_kwh']),
            'charging_station_id': str(row['charging_station_id']),
            'charging_station_location': str(row['charging_station_location']),
            'charging_start_time': pd.to_datetime(row['charging_start_time']),
            'charging_end_time': pd.to_datetime(row['charging_end_time']),
            'energy_consumed_kwh': float(row.get('energy_consumed_kwh', 0)) or None,
            'charging_duration_hours': float(row['charging_duration_hours']),
            'charging_rate_kw': float(row.get('charging_rate_kw', 0)) or None,
            'charging_cost_usd': float(row['charging_cost_usd']),
            'time_of_day': str(row['time_of_day']),
            'day_of_week': str(row['day_of_week']),
            'state_of_charge_start_percent': float(row['state_of_charge_start_percent']),
            'state_of_charge_end_percent': float(row['state_of_charge_end_percent']),
            'distance_driven_km': float(row.get('distance_driven_km', 0)) or None,
            'temperature_celsius': float(row['temperature_celsius']),
            'vehicle_age_years': float(row['vehicle_age_years']),
            'charger_type': str(row['charger_type']),
            'user_type': str(row['user_type'])
        }
    
    async def export_charging_data(
        self,
        format: str = "csv",
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        location: Optional[str] = None
    ) -> DataExportResponse:
        """Export charging data in specified format."""
        # Build query
        query = select(ChargingSession)
        
        filters = []
        if start_date:
            filters.append(ChargingSession.charging_start_time >= start_date)
        if end_date:
            filters.append(ChargingSession.charging_start_time <= end_date)
        if location:
            filters.append(ChargingSession.charging_station_location.ilike(f"%{location}%"))
        
        if filters:
            query = query.where(and_(*filters))
        
        result = await self.db.execute(query)
        sessions = result.scalars().all()
        
        # Convert to DataFrame
        data = []
        for session in sessions:
            data.append({
                'id': session.id,
                'user_id': session.user_id,
                'vehicle_model': session.vehicle_model,
                'battery_capacity_kwh': session.battery_capacity_kwh,
                'charging_station_id': session.charging_station_id,
                'charging_station_location': session.charging_station_location,
                'charging_start_time': session.charging_start_time,
                'charging_end_time': session.charging_end_time,
                'energy_consumed_kwh': session.energy_consumed_kwh,
                'charging_duration_hours': session.charging_duration_hours,
                'charging_rate_kw': session.charging_rate_kw,
                'charging_cost_usd': session.charging_cost_usd,
                'time_of_day': session.time_of_day,
                'day_of_week': session.day_of_week,
                'state_of_charge_start_percent': session.state_of_charge_start_percent,
                'state_of_charge_end_percent': session.state_of_charge_end_percent,
                'distance_driven_km': session.distance_driven_km,
                'temperature_celsius': session.temperature_celsius,
                'vehicle_age_years': session.vehicle_age_years,
                'charger_type': session.charger_type,
                'user_type': session.user_type,
                'created_at': session.created_at,
                'updated_at': session.updated_at
            })
        
        df = pd.DataFrame(data)
        
        # Generate filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"charging_data_{timestamp}.{format}"
        file_path = os.path.join(settings.DATA_PATH, "exports", filename)
        
        # Ensure export directory exists
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        
        # Export data
        if format == "csv":
            df.to_csv(file_path, index=False)
        elif format == "json":
            df.to_json(file_path, orient="records", date_format="iso")
        elif format == "parquet":
            df.to_parquet(file_path, index=False)
        else:
            raise ValueError(f"Unsupported format: {format}")
        
        # Get file size
        file_size = os.path.getsize(file_path)
        
        return DataExportResponse(
            filename=filename,
            format=format,
            record_count=len(df),
            file_size_bytes=file_size,
            download_url=f"/api/v1/data/download/{filename}",
            expires_at=datetime.now().replace(hour=23, minute=59, second=59)
        )
    
    async def get_data_statistics(self) -> DataStatistics:
        """Get basic data statistics."""
        # Total sessions
        total_sessions_result = await self.db.execute(
            select(func.count(ChargingSession.id))
        )
        total_sessions = total_sessions_result.scalar()
        
        # Total users
        total_users_result = await self.db.execute(
            select(func.count(func.distinct(ChargingSession.user_id)))
        )
        total_users = total_users_result.scalar()
        
        # Total stations
        total_stations_result = await self.db.execute(
            select(func.count(func.distinct(ChargingSession.charging_station_id)))
        )
        total_stations = total_stations_result.scalar()
        
        # Aggregated metrics
        metrics_result = await self.db.execute(
            select(
                func.sum(ChargingSession.energy_consumed_kwh),
                func.sum(ChargingSession.charging_cost_usd),
                func.avg(ChargingSession.charging_duration_hours),
                func.avg(ChargingSession.charging_cost_usd),
                func.min(ChargingSession.charging_start_time),
                func.max(ChargingSession.charging_start_time)
            )
        )
        metrics = metrics_result.first()
        
        # Most popular location
        popular_location_result = await self.db.execute(
            select(
                ChargingSession.charging_station_location,
                func.count(ChargingSession.id).label('count')
            )
            .group_by(ChargingSession.charging_station_location)
            .order_by(desc('count'))
            .limit(1)
        )
        popular_location = popular_location_result.first()
        
        # Most popular vehicle
        popular_vehicle_result = await self.db.execute(
            select(
                ChargingSession.vehicle_model,
                func.count(ChargingSession.id).label('count')
            )
            .group_by(ChargingSession.vehicle_model)
            .order_by(desc('count'))
            .limit(1)
        )
        popular_vehicle = popular_vehicle_result.first()
        
        return DataStatistics(
            total_sessions=total_sessions or 0,
            total_users=total_users or 0,
            total_stations=total_stations or 0,
            total_energy_kwh=float(metrics[0] or 0),
            total_cost_usd=float(metrics[1] or 0),
            date_range_start=metrics[4] or datetime.now(),
            date_range_end=metrics[5] or datetime.now(),
            avg_session_duration_hours=float(metrics[2] or 0),
            avg_session_cost_usd=float(metrics[3] or 0),
            most_popular_location=popular_location[0] if popular_location else "N/A",
            most_popular_vehicle_model=popular_vehicle[0] if popular_vehicle else "N/A"
        )
    
    async def get_data_quality_report(self) -> DataQualityReport:
        """Generate data quality report."""
        # Get total record count
        total_count_result = await self.db.execute(
            select(func.count(ChargingSession.id))
        )
        total_count = total_count_result.scalar() or 0
        
        if total_count == 0:
            return DataQualityReport(
                overall_score=0.0,
                metrics=[],
                missing_data_summary={},
                outlier_summary={},
                duplicate_records=0,
                data_freshness_days=0.0,
                recommendations=["No data available for quality assessment"]
            )
        
        # Calculate missing data percentages
        missing_data = {}
        nullable_fields = [
            'energy_consumed_kwh', 'charging_rate_kw', 'distance_driven_km'
        ]
        
        for field in nullable_fields:
            null_count_result = await self.db.execute(
                select(func.count(ChargingSession.id))
                .where(getattr(ChargingSession, field).is_(None))
            )
            null_count = null_count_result.scalar() or 0
            missing_data[field] = (null_count / total_count) * 100
        
        # Check for duplicates (simplified)
        duplicate_result = await self.db.execute(
            select(func.count())
            .select_from(
                select(
                    ChargingSession.user_id,
                    ChargingSession.charging_start_time
                )
                .group_by(
                    ChargingSession.user_id,
                    ChargingSession.charging_start_time
                )
                .having(func.count() > 1)
                .subquery()
            )
        )
        duplicate_count = duplicate_result.scalar() or 0
        
        # Data freshness
        latest_record_result = await self.db.execute(
            select(func.max(ChargingSession.created_at))
        )
        latest_record = latest_record_result.scalar()
        data_freshness_days = 0.0
        if latest_record:
            data_freshness_days = (datetime.utcnow() - latest_record).days
        
        # Generate quality metrics
        metrics = [
            DataQualityMetric(
                metric_name="Data Completeness",
                value=100 - sum(missing_data.values()) / len(missing_data),
                threshold=95.0,
                status="good" if sum(missing_data.values()) / len(missing_data) < 5 else "warning",
                description="Percentage of complete records"
            ),
            DataQualityMetric(
                metric_name="Duplicate Records",
                value=duplicate_count,
                threshold=0.0,
                status="good" if duplicate_count == 0 else "warning",
                description="Number of duplicate records found"
            ),
            DataQualityMetric(
                metric_name="Data Freshness",
                value=data_freshness_days,
                threshold=7.0,
                status="good" if data_freshness_days <= 7 else "warning",
                description="Days since last data update"
            )
        ]
        
        # Calculate overall score
        overall_score = sum(
            100 if metric.value >= metric.threshold else 
            max(0, (metric.value / metric.threshold) * 100)
            for metric in metrics
        ) / len(metrics)
        
        # Generate recommendations
        recommendations = []
        if sum(missing_data.values()) / len(missing_data) > 5:
            recommendations.append("Consider improving data collection for optional fields")
        if duplicate_count > 0:
            recommendations.append("Remove duplicate records to improve data quality")
        if data_freshness_days > 7:
            recommendations.append("Update data more frequently to maintain freshness")
        
        return DataQualityReport(
            overall_score=overall_score,
            metrics=metrics,
            missing_data_summary=missing_data,
            outlier_summary={},  # Would implement outlier detection
            duplicate_records=duplicate_count,
            data_freshness_days=data_freshness_days,
            recommendations=recommendations
        )
    
    async def delete_charging_session(self, session_id: int) -> bool:
        """Delete a charging session."""
        result = await self.db.execute(
            select(ChargingSession).where(ChargingSession.id == session_id)
        )
        session = result.scalar_one_or_none()
        
        if not session:
            return False
        
        await self.db.delete(session)
        await self.db.commit()
        return True
