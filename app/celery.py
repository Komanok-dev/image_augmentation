from celery import Celery

from app.settings import celery_settings

celery_app = Celery(
    "image_augmentation",
    broker=celery_settings.url,
    backend=celery_settings.url,
)

celery_app.autodiscover_tasks(["app"])
