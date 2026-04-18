from celery import Celery

from app.core.config import settings
from app.core.vault_loader import load_config

# Note: redis and task_progress utilities are imported lazily by tasks that need them
# to avoid circular imports during module initialization

load_config()

celery_app = Celery(
    "worker",
    broker=settings.CELERY_BROKER_URL,
    backend=settings.CELERY_RESULT_BACKEND,
    include=["app.jobs.tasks"],  # Explicitly include tasks module
)

# Configure Celery settings for better timeout handling
celery_app.conf.update(
    # Task timeout settings
    task_soft_time_limit=30000,
    task_time_limit=60000,
    # Worker settings
    worker_prefetch_multiplier=1,
    task_acks_late=True,
    worker_max_tasks_per_child=50,
    # Retry settings
    task_default_retry_delay=60,
    task_max_retries=3,
)

# Setup logging for Celery worker - import here to avoid circular imports
# This will only be executed when celery_worker is imported as a module
try:
    from app.modules.common.utils.logging import logger, setup_logging

    setup_logging(settings.LOG_LEVEL)
    logger.info("Configuration and logging initialized for Celery worker.")
    logger.info(f"Celery Broker URL: {settings.CELERY_BROKER_URL}")
except ImportError:
    # In case logging is not yet available, continue without logging
    pass
