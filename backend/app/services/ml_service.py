"""
Machine Learning service for model management and predictions.
"""

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete
from typing import List, Optional, Dict, Any
import logging
import os
import glob
from datetime import datetime

from app.db.models import MLModel, Prediction
from app.ml.models import DurationPredictionModel, CostOptimizationModel
from app.schemas.ml import (
    DurationPredictionRequest,
    DurationPredictionResponse,
    CostPredictionRequest,
    CostPredictionResponse,
    ModelStatus,
    ModelPerformance
)
from app.core.config import settings

logger = logging.getLogger(__name__)


class MLService:
    """Service for machine learning operations."""
    
    def __init__(self, db: AsyncSession):
        self.db = db
        self._models = {}
        
    async def _load_model(self, model_name: str) -> Optional[Any]:
        """Load a model from disk."""
        if model_name in self._models:
            return self._models[model_name]
        
        # Get active model from database
        result = await self.db.execute(
            select(MLModel).where(
                MLModel.model_name == model_name,
                MLModel.is_active == True
            ).order_by(MLModel.training_date.desc())
        )
        model_record = result.scalar_one_or_none()
        
        if not model_record:
            logger.warning(f"No active model found for {model_name}")
            return None
        
        # Load the appropriate model class
        if model_name == "duration_prediction":
            model = DurationPredictionModel()
        elif model_name == "cost_optimization":
            model = CostOptimizationModel()
        else:
            logger.error(f"Unknown model type: {model_name}")
            return None
        
        # Load model from file
        if os.path.exists(model_record.file_path):
            if model.load_model(model_record.file_path):
                self._models[model_name] = model
                return model
        
        logger.error(f"Failed to load model from {model_record.file_path}")
        return None
    
    async def predict_duration(
        self, 
        request: DurationPredictionRequest
    ) -> DurationPredictionResponse:
        """Predict charging duration."""
        model = await self._load_model("duration_prediction")
        if not model:
            raise ValueError("Duration prediction model not available")
        
        # Convert request to features
        features = {
            'vehicle_model': request.vehicle_model,
            'battery_capacity_kwh': request.battery_capacity_kwh,
            'state_of_charge_start_percent': request.state_of_charge_start_percent,
            'state_of_charge_end_percent': request.state_of_charge_target_percent,
            'charger_type': request.charger_type.value,
            'temperature_celsius': request.temperature_celsius,
            'vehicle_age_years': request.vehicle_age_years,
            'time_of_day': 'Morning'  # Default, could be inferred from current time
        }
        
        # Make prediction
        prediction_result = model.predict(features)
        
        # Calculate estimated energy
        energy_needed = (
            request.battery_capacity_kwh * 
            (request.state_of_charge_target_percent - request.state_of_charge_start_percent) / 100
        )
        
        # Store prediction for analysis
        prediction_record = Prediction(
            model_id=1,  # Would get from model record
            prediction_type="duration",
            input_features=str(features),
            prediction_result=str(prediction_result),
            confidence_score=prediction_result['confidence_score']
        )
        self.db.add(prediction_record)
        await self.db.commit()
        
        return DurationPredictionResponse(
            predicted_duration_hours=prediction_result['predicted_duration_hours'],
            confidence_score=prediction_result['confidence_score'],
            estimated_energy_kwh=energy_needed,
            factors_analysis=prediction_result['feature_importance'],
            model_version="1.0"
        )
    
    async def predict_cost(
        self, 
        request: CostPredictionRequest
    ) -> CostPredictionResponse:
        """Predict charging cost."""
        model = await self._load_model("cost_optimization")
        if not model:
            raise ValueError("Cost optimization model not available")
        
        # Convert request to features
        features = {
            'charging_station_location': request.location,
            'charger_type': request.charger_type.value,
            'energy_consumed_kwh': request.energy_needed_kwh,
            'time_of_day': request.time_of_day.value,
            'day_of_week': request.day_of_week,
            'user_type': request.user_type.value,
            'charging_duration_hours': request.duration_hours or 1.0,
            'temperature_celsius': 20.0  # Default temperature
        }
        
        # Make prediction
        prediction_result = model.predict(features)
        
        # Calculate cost per kWh
        cost_per_kwh = prediction_result['predicted_cost_usd'] / request.energy_needed_kwh
        
        # Generate optimization suggestions
        suggestions = self._generate_cost_optimization_suggestions(request, prediction_result)
        
        # Store prediction
        prediction_record = Prediction(
            model_id=2,  # Would get from model record
            prediction_type="cost",
            input_features=str(features),
            prediction_result=str(prediction_result),
            confidence_score=prediction_result['confidence_score']
        )
        self.db.add(prediction_record)
        await self.db.commit()
        
        return CostPredictionResponse(
            predicted_cost_usd=prediction_result['predicted_cost_usd'],
            cost_per_kwh=cost_per_kwh,
            confidence_score=prediction_result['confidence_score'],
            cost_breakdown=prediction_result['feature_importance'],
            optimization_suggestions=suggestions,
            model_version="1.0"
        )
    
    def _generate_cost_optimization_suggestions(
        self, 
        request: CostPredictionRequest, 
        prediction_result: Dict[str, Any]
    ) -> List[str]:
        """Generate cost optimization suggestions."""
        suggestions = []
        
        # Time-based suggestions
        if request.time_of_day in ['Evening', 'Afternoon']:
            suggestions.append("Consider charging during off-peak hours (late night/early morning) for lower rates")
        
        # Charger type suggestions
        if request.charger_type == 'DC Fast Charger':
            suggestions.append("DC fast charging is convenient but more expensive. Use Level 2 charging when time permits")
        
        # Location suggestions
        suggestions.append("Compare prices at nearby charging stations before starting your session")
        
        # User type specific suggestions
        if request.user_type == 'Commuter':
            suggestions.append("Consider workplace charging or home charging for daily commuting needs")
        
        return suggestions
    
    async def get_model_status(self) -> List[ModelStatus]:
        """Get status of all models."""
        result = await self.db.execute(select(MLModel))
        models = result.scalars().all()
        
        status_list = []
        for model in models:
            # Determine model health
            status = "healthy"
            if not os.path.exists(model.file_path):
                status = "failed"
            elif model.performance_metrics:
                # Parse performance metrics (stored as JSON string)
                import json
                try:
                    metrics = json.loads(model.performance_metrics)
                    if metrics.get('test_r2', 0) < 0.7:
                        status = "degraded"
                except:
                    status = "unknown"
            
            status_list.append(ModelStatus(
                model_name=model.model_name,
                model_type=model.model_type,
                version=model.version,
                is_active=model.is_active,
                training_date=model.training_date,
                performance_score=None,  # Would extract from metrics
                training_data_size=model.training_data_size,
                status=status
            ))
        
        return status_list
    
    async def get_model_performance(self, model_name: str) -> Optional[ModelPerformance]:
        """Get performance metrics for a specific model."""
        result = await self.db.execute(
            select(MLModel).where(
                MLModel.model_name == model_name,
                MLModel.is_active == True
            )
        )
        model = result.scalar_one_or_none()
        
        if not model:
            return None
        
        # Parse performance metrics
        import json
        try:
            metrics = json.loads(model.performance_metrics) if model.performance_metrics else {}
        except:
            metrics = {}
        
        return ModelPerformance(
            model_name=model.model_name,
            version=model.version,
            metrics=metrics,
            validation_score=metrics.get('cv_r2_mean', 0.0),
            test_score=metrics.get('test_r2', 0.0),
            feature_importance={},  # Would load from model file
            training_history=[],  # Would store during training
            last_evaluation_date=model.training_date
        )
    
    async def delete_model(self, model_name: str) -> bool:
        """Delete a model."""
        result = await self.db.execute(
            delete(MLModel).where(MLModel.model_name == model_name)
        )
        await self.db.commit()
        
        # Remove from memory cache
        if model_name in self._models:
            del self._models[model_name]
        
        return result.rowcount > 0
    
    async def activate_model(self, model_name: str, version: Optional[str] = None) -> bool:
        """Activate a specific model version."""
        # Deactivate all versions of this model
        await self.db.execute(
            update(MLModel)
            .where(MLModel.model_name == model_name)
            .values(is_active=False)
        )
        
        # Activate the specified version
        query = update(MLModel).where(MLModel.model_name == model_name)
        if version:
            query = query.where(MLModel.version == version)
        else:
            # Activate the latest version
            subquery = select(MLModel.id).where(
                MLModel.model_name == model_name
            ).order_by(MLModel.training_date.desc()).limit(1)
            query = query.where(MLModel.id.in_(subquery))
        
        result = await self.db.execute(query.values(is_active=True))
        await self.db.commit()
        
        # Clear from memory cache to force reload
        if model_name in self._models:
            del self._models[model_name]
        
        return result.rowcount > 0
