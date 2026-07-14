import os

from celery import Celery
from celery.beat import crontab

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "shop_api.settings")

app = Celery("shop_api")

app.config_from_object("django.conf:settings", namespace="CELERY")

app.autodiscover_tasks()

app.conf.beat_schedule = {
    "send_report": {
        "task": "users.tasks.send_report",
        "schedule": crontab(minute="*/5"),
    },
}