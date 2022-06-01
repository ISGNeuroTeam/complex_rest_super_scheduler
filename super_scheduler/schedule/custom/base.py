from pydantic import BaseModel as BaseModelFormat
from celery.schedules import BaseSchedule

from django.db import models
from django_celery_beat.models import MICROSECONDS, SECONDS, MINUTES, HOURS, DAYS, PERIOD_CHOICES, SINGULAR_PERIODS

from ..base import BaseFormat


class BaseCelerySchedule(BaseSchedule):

    def remaining_estimate(self, last_run_at):
        raise NotImplementedError()

    def is_due(self, last_run_at):
        raise NotImplementedError()


class BaseDjangoSchedule(models.Model):

    class Meta:
        app_label = 'BaseDjangoSchedule'

    @property
    def schedule(self):
        raise NotImplementedError()

    @classmethod
    def from_schedule(cls, schedule, *args):
        raise NotImplementedError()

    def __str__(self):
        raise NotImplementedError()
