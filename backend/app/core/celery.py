"""
Celery configuration for background tasks.
"""

from celery import Celery
from celery.schedules import crontab
import logging

from app.core.config import settings

logger = logging.getLogger(__name__)

# Create Celery instance
celery_app = Celery(
    "ev_charging_analytics",
    broker=settings.CELERY_BROKER_URL,
    backend=settings.CELERY_RESULT_BACKEND,
    include=[
        "app.tasks.data_processing",
        "app.tasks.ml_training",
        "app.tasks.analytics",
    ]
)

# Celery configuration
celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    task_time_limit=30 * 60,  # 30 minutes
    task_soft_time_limit=25 * 60,  # 25 minutes
    worker_prefetch_multiplier=1,
    worker_max_tasks_per_child=1000,
)

# Periodic tasks schedule
celery_app.conf.beat_schedule = {
    # Retrain ML models daily
    "retrain-models": {
        "task": "app.tasks.ml_training.retrain_all_models",
        "schedule": crontab(hour=2, minute=0),  # 2 AM daily
    },
    
    # Process new data every hour
    "process-data": {
        "task": "app.tasks.data_processing.process_new_data",
        "schedule": crontab(minute=0),  # Every hour
    },
    
    # Generate analytics reports daily
    "generate-analytics": {
        "task": "app.tasks.analytics.generate_daily_report",
        "schedule": crontab(hour=6, minute=0),  # 6 AM daily
    },
    
    # Clean up old cache entries
    "cleanup-cache": {
        "task": "app.tasks.data_processing.cleanup_cache",
        "schedule": crontab(hour=3, minute=0),  # 3 AM daily
    },
    
    # Health check for models
    "model-health-check": {
        "task": "app.tasks.ml_training.model_health_check",
        "schedule": crontab(minute="*/30"),  # Every 30 minutes
    },
}

# Task routes
celery_app.conf.task_routes = {
    "app.tasks.ml_training.*": {"queue": "ml_queue"},
    "app.tasks.data_processing.*": {"queue": "data_queue"},
    "app.tasks.analytics.*": {"queue": "analytics_queue"},
}


@celery_app.task(bind=True)
def debug_task(self):
    """Debug task for testing Celery."""
    print(f"Request: {self.request!r}")
    return "Celery is working!"


if __name__ == "__main__":
    celery_app.start()
