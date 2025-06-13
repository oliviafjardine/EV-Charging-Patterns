"""
Machine Learning API endpoints.
"""

from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
import logging

from app.core.database import get_db
from app.core.redis import cache, get_cache_key
from app.core.config import settings
from app.services.ml_service import MLService
from app.schemas.ml import (
    DurationPredictionRequest,
    DurationPredictionResponse,
    CostPredictionRequest,
    CostPredictionResponse,
    ModelStatus,
    ModelPerformance,
    TrainingRequest,
    TrainingResponse
)
from app.tasks.ml_training import retrain_model

router = APIRouter()
logger = logging.getLogger(__name__)


@router.post("/predict/duration", response_model=DurationPredictionResponse)
async def predict_charging_duration(
    request: DurationPredictionRequest,
    db: AsyncSession = Depends(get_db)
):
    """Predict charging duration based on input parameters."""
    try:
        ml_service = MLService(db)
        prediction = await ml_service.predict_duration(request)
        return prediction
        
    except Exception as e:
        logger.error(f"Error predicting charging duration: {e}")
        raise HTTPException(status_code=500, detail="Prediction failed")


@router.post("/predict/cost", response_model=CostPredictionResponse)
async def predict_charging_cost(
    request: CostPredictionRequest,
    db: AsyncSession = Depends(get_db)
):
    """Predict charging cost based on input parameters."""
    try:
        ml_service = MLService(db)
        prediction = await ml_service.predict_cost(request)
        return prediction
        
    except Exception as e:
        logger.error(f"Error predicting charging cost: {e}")
        raise HTTPException(status_code=500, detail="Prediction failed")


@router.get("/models/status", response_model=List[ModelStatus])
async def get_model_status(db: AsyncSession = Depends(get_db)):
    """Get status of all ML models."""
    try:
        cache_key = await get_cache_key("model_status")
        cached_result = await cache.get(cache_key)
        if cached_result:
            return cached_result
        
        ml_service = MLService(db)
        status = await ml_service.get_model_status()
        
        await cache.set(cache_key, [s.dict() for s in status], ttl=settings.CACHE_TTL_SHORT)
        return status
        
    except Exception as e:
        logger.error(f"Error getting model status: {e}")
        raise HTTPException(status_code=500, detail="Failed to get model status")


@router.get("/models/{model_name}/performance", response_model=ModelPerformance)
async def get_model_performance(
    model_name: str,
    db: AsyncSession = Depends(get_db)
):
    """Get performance metrics for a specific model."""
    try:
        cache_key = await get_cache_key("model_performance", model_name)
        cached_result = await cache.get(cache_key)
        if cached_result:
            return cached_result
        
        ml_service = MLService(db)
        performance = await ml_service.get_model_performance(model_name)
        
        if not performance:
            raise HTTPException(status_code=404, detail="Model not found")
        
        await cache.set(cache_key, performance.dict(), ttl=settings.CACHE_TTL_MEDIUM)
        return performance
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting model performance: {e}")
        raise HTTPException(status_code=500, detail="Failed to get model performance")


@router.post("/models/{model_name}/train", response_model=TrainingResponse)
async def train_model(
    model_name: str,
    request: TrainingRequest,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db)
):
    """Trigger model training."""
    try:
        ml_service = MLService(db)
        
        # Validate model name
        valid_models = ["duration_prediction", "cost_optimization", "demand_forecast", "user_clustering"]
        if model_name not in valid_models:
            raise HTTPException(
                status_code=400, 
                detail=f"Invalid model name. Valid options: {valid_models}"
            )
        
        # Start training in background
        task = retrain_model.delay(model_name, request.dict())
        
        return TrainingResponse(
            task_id=task.id,
            model_name=model_name,
            status="started",
            message="Training started in background"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error starting model training: {e}")
        raise HTTPException(status_code=500, detail="Failed to start training")


@router.get("/models/{model_name}/train/{task_id}")
async def get_training_status(model_name: str, task_id: str):
    """Get training task status."""
    try:
        from app.core.celery import celery_app
        
        task = celery_app.AsyncResult(task_id)
        
        if task.state == "PENDING":
            response = {
                "task_id": task_id,
                "model_name": model_name,
                "status": "pending",
                "message": "Training is pending"
            }
        elif task.state == "PROGRESS":
            response = {
                "task_id": task_id,
                "model_name": model_name,
                "status": "in_progress",
                "message": "Training in progress",
                "progress": task.info.get("progress", 0)
            }
        elif task.state == "SUCCESS":
            response = {
                "task_id": task_id,
                "model_name": model_name,
                "status": "completed",
                "message": "Training completed successfully",
                "result": task.result
            }
        else:  # FAILURE
            response = {
                "task_id": task_id,
                "model_name": model_name,
                "status": "failed",
                "message": "Training failed",
                "error": str(task.info)
            }
        
        return response
        
    except Exception as e:
        logger.error(f"Error getting training status: {e}")
        raise HTTPException(status_code=500, detail="Failed to get training status")


@router.post("/models/retrain-all")
async def retrain_all_models(
    background_tasks: BackgroundTasks,
    force: bool = False
):
    """Trigger retraining of all models."""
    try:
        from app.tasks.ml_training import retrain_all_models
        
        task = retrain_all_models.delay(force=force)
        
        return {
            "task_id": task.id,
            "status": "started",
            "message": "Retraining all models started in background"
        }
        
    except Exception as e:
        logger.error(f"Error starting model retraining: {e}")
        raise HTTPException(status_code=500, detail="Failed to start retraining")


@router.delete("/models/{model_name}")
async def delete_model(
    model_name: str,
    db: AsyncSession = Depends(get_db)
):
    """Delete a model."""
    try:
        ml_service = MLService(db)
        success = await ml_service.delete_model(model_name)
        
        if not success:
            raise HTTPException(status_code=404, detail="Model not found")
        
        # Clear related cache
        cache_keys = await cache.keys(f"*{model_name}*")
        for key in cache_keys:
            await cache.delete(key)
        
        return {"message": f"Model {model_name} deleted successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting model: {e}")
        raise HTTPException(status_code=500, detail="Failed to delete model")


@router.post("/models/{model_name}/activate")
async def activate_model(
    model_name: str,
    version: Optional[str] = None,
    db: AsyncSession = Depends(get_db)
):
    """Activate a specific model version."""
    try:
        ml_service = MLService(db)
        success = await ml_service.activate_model(model_name, version)
        
        if not success:
            raise HTTPException(status_code=404, detail="Model or version not found")
        
        # Clear model status cache
        await cache.delete(await get_cache_key("model_status"))
        
        return {"message": f"Model {model_name} version {version or 'latest'} activated"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error activating model: {e}")
        raise HTTPException(status_code=500, detail="Failed to activate model")
