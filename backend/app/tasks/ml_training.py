"""
Celery tasks for machine learning model training.
"""

from celery import current_task
import pandas as pd
import logging
from sqlalchemy import select
from datetime import datetime, timedelta
import json
import os

from app.core.celery import celery_app
from app.core.database import AsyncSessionLocal
from app.db.models import ChargingSession, MLModel
from app.ml.models import DurationPredictionModel, CostOptimizationModel
from app.core.config import settings

logger = logging.getLogger(__name__)


@celery_app.task(bind=True)
def retrain_model(self, model_name: str, config: dict = None):
    """Retrain a specific ML model."""
    try:
        logger.info(f"Starting training for model: {model_name}")
        
        # Update task state
        self.update_state(
            state='PROGRESS',
            meta={'progress': 10, 'status': 'Loading data...'}
        )
        
        # Load training data
        training_data = load_training_data()
        if training_data.empty:
            raise ValueError("No training data available")
        
        self.update_state(
            state='PROGRESS',
            meta={'progress': 30, 'status': 'Preparing model...'}
        )
        
        # Initialize model
        if model_name == "duration_prediction":
            model = DurationPredictionModel()
        elif model_name == "cost_optimization":
            model = CostOptimizationModel()
        else:
            raise ValueError(f"Unknown model: {model_name}")
        
        self.update_state(
            state='PROGRESS',
            meta={'progress': 50, 'status': 'Training model...'}
        )
        
        # Train model
        metrics = model.train(training_data)
        
        self.update_state(
            state='PROGRESS',
            meta={'progress': 80, 'status': 'Saving model...'}
        )
        
        # Save model
        version = datetime.now().strftime("%Y%m%d_%H%M%S")
        model_file = model.save_model(version)
        
        # Save model metadata to database
        save_model_metadata(model_name, version, model_file, metrics, len(training_data))
        
        self.update_state(
            state='PROGRESS',
            meta={'progress': 100, 'status': 'Training completed'}
        )
        
        logger.info(f"Model {model_name} training completed successfully")
        return {
            'model_name': model_name,
            'version': version,
            'metrics': metrics,
            'training_data_size': len(training_data),
            'model_file': model_file
        }
        
    except Exception as e:
        logger.error(f"Error training model {model_name}: {e}")
        self.update_state(
            state='FAILURE',
            meta={'error': str(e)}
        )
        raise


@celery_app.task(bind=True)
def retrain_all_models(self, force: bool = False):
    """Retrain all ML models."""
    try:
        models_to_train = ["duration_prediction", "cost_optimization"]
        results = {}
        
        for i, model_name in enumerate(models_to_train):
            progress = int((i / len(models_to_train)) * 100)
            self.update_state(
                state='PROGRESS',
                meta={'progress': progress, 'status': f'Training {model_name}...'}
            )
            
            # Check if model needs retraining
            if not force and not should_retrain_model(model_name):
                logger.info(f"Skipping {model_name} - no retraining needed")
                results[model_name] = "skipped"
                continue
            
            # Train model
            try:
                result = retrain_model.delay(model_name)
                results[model_name] = result.get(timeout=1800)  # 30 minutes timeout
            except Exception as e:
                logger.error(f"Error training {model_name}: {e}")
                results[model_name] = f"error: {str(e)}"
        
        return results
        
    except Exception as e:
        logger.error(f"Error in retrain_all_models: {e}")
        raise


@celery_app.task
def model_health_check():
    """Check health of all ML models."""
    try:
        health_status = {}
        
        # Check each model
        models = ["duration_prediction", "cost_optimization"]
        for model_name in models:
            try:
                # Check if model file exists
                model_record = get_active_model(model_name)
                if not model_record:
                    health_status[model_name] = "no_active_model"
                    continue
                
                if not os.path.exists(model_record['file_path']):
                    health_status[model_name] = "file_missing"
                    continue
                
                # Check model performance
                if model_record['performance_metrics']:
                    metrics = json.loads(model_record['performance_metrics'])
                    test_r2 = metrics.get('test_r2', 0)
                    
                    if test_r2 < settings.MODEL_PERFORMANCE_THRESHOLD:
                        health_status[model_name] = "performance_degraded"
                    else:
                        health_status[model_name] = "healthy"
                else:
                    health_status[model_name] = "no_metrics"
                    
            except Exception as e:
                logger.error(f"Error checking {model_name}: {e}")
                health_status[model_name] = f"error: {str(e)}"
        
        logger.info(f"Model health check completed: {health_status}")
        return health_status
        
    except Exception as e:
        logger.error(f"Error in model health check: {e}")
        raise


def load_training_data() -> pd.DataFrame:
    """Load training data from database."""
    try:
        # Use synchronous database connection for Celery tasks
        from sqlalchemy import create_engine
        from sqlalchemy.orm import sessionmaker
        
        # Create synchronous engine
        sync_db_url = settings.DATABASE_URL.replace("postgresql+asyncpg://", "postgresql://")
        engine = create_engine(sync_db_url)
        SessionLocal = sessionmaker(bind=engine)
        
        with SessionLocal() as db:
            # Load charging sessions
            query = select(ChargingSession)
            result = db.execute(query)
            sessions = result.scalars().all()
            
            # Convert to DataFrame
            data = []
            for session in sessions:
                data.append({
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
                })
            
            df = pd.DataFrame(data)
            logger.info(f"Loaded {len(df)} training records")
            return df
            
    except Exception as e:
        logger.error(f"Error loading training data: {e}")
        return pd.DataFrame()


def save_model_metadata(model_name: str, version: str, file_path: str, metrics: dict, data_size: int):
    """Save model metadata to database."""
    try:
        from sqlalchemy import create_engine
        from sqlalchemy.orm import sessionmaker
        
        sync_db_url = settings.DATABASE_URL.replace("postgresql+asyncpg://", "postgresql://")
        engine = create_engine(sync_db_url)
        SessionLocal = sessionmaker(bind=engine)
        
        with SessionLocal() as db:
            # Deactivate existing models
            db.query(MLModel).filter(
                MLModel.model_name == model_name
            ).update({'is_active': False})
            
            # Create new model record
            model_record = MLModel(
                model_name=model_name,
                model_type=model_name,
                version=version,
                file_path=file_path,
                training_data_size=data_size,
                training_date=datetime.utcnow(),
                performance_metrics=json.dumps(metrics),
                is_active=True
            )
            
            db.add(model_record)
            db.commit()
            
            logger.info(f"Saved model metadata for {model_name} v{version}")
            
    except Exception as e:
        logger.error(f"Error saving model metadata: {e}")


def should_retrain_model(model_name: str) -> bool:
    """Check if model should be retrained."""
    try:
        model_record = get_active_model(model_name)
        if not model_record:
            return True
        
        # Check if model is older than retrain interval
        last_training = model_record['training_date']
        hours_since_training = (datetime.utcnow() - last_training).total_seconds() / 3600
        
        return hours_since_training > settings.RETRAIN_INTERVAL_HOURS
        
    except Exception as e:
        logger.error(f"Error checking retrain status for {model_name}: {e}")
        return True


def get_active_model(model_name: str) -> dict:
    """Get active model metadata."""
    try:
        from sqlalchemy import create_engine
        from sqlalchemy.orm import sessionmaker
        
        sync_db_url = settings.DATABASE_URL.replace("postgresql+asyncpg://", "postgresql://")
        engine = create_engine(sync_db_url)
        SessionLocal = sessionmaker(bind=engine)
        
        with SessionLocal() as db:
            model = db.query(MLModel).filter(
                MLModel.model_name == model_name,
                MLModel.is_active == True
            ).first()
            
            if model:
                return {
                    'id': model.id,
                    'model_name': model.model_name,
                    'version': model.version,
                    'file_path': model.file_path,
                    'training_date': model.training_date,
                    'performance_metrics': model.performance_metrics
                }
            
            return None
            
    except Exception as e:
        logger.error(f"Error getting active model {model_name}: {e}")
        return None
