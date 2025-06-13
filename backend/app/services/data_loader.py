"""
Data loading service for initial data setup.
"""

import pandas as pd
import logging
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import Dict, Any
import os

from app.core.database import AsyncSessionLocal
from app.db.models import ChargingSession, ChargingStation, Vehicle, User
from app.core.config import settings

logger = logging.getLogger(__name__)


async def load_initial_data():
    """Load initial data from CSV files if database is empty."""
    async with AsyncSessionLocal() as db:
        try:
            # Check if data already exists
            result = await db.execute(select(ChargingSession).limit(1))
            if result.scalar_one_or_none():
                logger.info("Data already exists, skipping initial load")
                return

            # Load data from CSV file
            csv_path = os.path.join(settings.DATA_PATH, "sample_data.csv")
            if not os.path.exists(csv_path):
                # Try alternative path
                csv_path = os.path.join("data", "sample_data.csv")
                if not os.path.exists(csv_path):
                    logger.warning(f"CSV file not found at {csv_path}")
                    return

            logger.info("Loading initial data from CSV...")
            df = pd.read_csv(csv_path)

            # Process and load data
            await load_charging_sessions(db, df)
            await load_stations_from_sessions(db, df)
            await load_vehicles_from_sessions(db, df)
            await load_users_from_sessions(db, df)

            await db.commit()
            logger.info(f"Successfully loaded {len(df)} charging sessions")

        except Exception as e:
            logger.error(f"Error loading initial data: {e}")
            await db.rollback()


async def load_charging_sessions(db: AsyncSession, df: pd.DataFrame):
    """Load charging sessions from DataFrame."""
    sessions = []

    for _, row in df.iterrows():
        try:
            session = ChargingSession(
                user_id=str(row['User ID']),
                vehicle_model=str(row['Vehicle Model']),
                battery_capacity_kwh=float(row['Battery Capacity (kWh)']),
                charging_station_id=str(row['Charging Station ID']),
                charging_station_location=str(
                    row['Charging Station Location']),
                charging_start_time=pd.to_datetime(row['Charging Start Time']),
                charging_end_time=pd.to_datetime(row['Charging End Time']),
                energy_consumed_kwh=float(
                    row.get('Energy Consumed (kWh)', 0)) or None,
                charging_duration_hours=float(
                    row['Charging Duration (hours)']),
                charging_rate_kw=float(
                    row.get('Charging Rate (kW)', 0)) or None,
                charging_cost_usd=float(row['Charging Cost (USD)']),
                time_of_day=str(row['Time of Day']),
                day_of_week=str(row['Day of Week']),
                state_of_charge_start_percent=float(
                    row['State of Charge (Start %)']),
                state_of_charge_end_percent=float(
                    row['State of Charge (End %)']),
                distance_driven_km=float(
                    row.get('Distance Driven (km)', 0)) or None,
                temperature_celsius=float(row['Temperature (Celsius)']),
                vehicle_age_years=float(row['Vehicle Age (years)']),
                charger_type=str(row['Charger Type']),
                user_type=str(row['User Type'])
            )
            sessions.append(session)

        except Exception as e:
            logger.warning(f"Error processing row {row.name}: {e}")
            continue

    db.add_all(sessions)
    logger.info(f"Added {len(sessions)} charging sessions")


async def load_stations_from_sessions(db: AsyncSession, df: pd.DataFrame):
    """Extract and load unique charging stations."""
    stations_data = df[['Charging Station ID',
                        'Charging Station Location', 'Charger Type']].drop_duplicates()
    stations = []

    for _, row in stations_data.iterrows():
        try:
            station = ChargingStation(
                station_id=str(row['Charging Station ID']),
                location=str(row['Charging Station Location']),
                charger_types=str(row['Charger Type']),  # Simplified for now
                is_active=True
            )
            stations.append(station)

        except Exception as e:
            logger.warning(
                f"Error processing station {row['Charging Station ID']}: {e}")
            continue

    db.add_all(stations)
    logger.info(f"Added {len(stations)} charging stations")


async def load_vehicles_from_sessions(db: AsyncSession, df: pd.DataFrame):
    """Extract and load unique vehicles."""
    vehicles_data = df[['Vehicle Model',
                        'Battery Capacity (kWh)']].drop_duplicates()
    vehicles = []

    for _, row in vehicles_data.iterrows():
        try:
            # Extract manufacturer from model (simplified)
            model = str(row['Vehicle Model'])
            manufacturer = model.split()[0] if ' ' in model else 'Unknown'

            vehicle = Vehicle(
                model=model,
                manufacturer=manufacturer,
                battery_capacity_kwh=float(row['Battery Capacity (kWh)']),
            )
            vehicles.append(vehicle)

        except Exception as e:
            logger.warning(
                f"Error processing vehicle {row['Vehicle Model']}: {e}")
            continue

    db.add_all(vehicles)
    logger.info(f"Added {len(vehicles)} vehicles")


async def load_users_from_sessions(db: AsyncSession, df: pd.DataFrame):
    """Extract and load unique users."""
    users_data = df[['User ID', 'User Type']].drop_duplicates()
    users = []

    for _, row in users_data.iterrows():
        try:
            user = User(
                user_id=str(row['User ID']),
                user_type=str(row['User Type'])
            )
            users.append(user)

        except Exception as e:
            logger.warning(f"Error processing user {row['User ID']}: {e}")
            continue

    db.add_all(users)
    logger.info(f"Added {len(users)} users")
