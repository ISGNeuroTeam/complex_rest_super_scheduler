from django_celery_beat.models import IntervalSchedule
from pydantic import validator

from .base import BaseScheduleFormat


class IntervalFormat(BaseScheduleFormat):
    every: int
    period: str

    @validator("every")
    def every_check_interval(cls, value):
        """
        Check valid every param.
        """
        if value <= 0:
            raise ValueError("'Every' param must be > 0")
        return value

    @validator("period")
    def interval_transformer(cls, value):
        """
        Transform string to IntervalSchedule time period.
        """
        period_formats = [
            IntervalSchedule.MICROSECONDS,
            IntervalSchedule.SECONDS,
            IntervalSchedule.MINUTES,
            IntervalSchedule.HOURS,
            IntervalSchedule.DAYS
        ]
        if value not in period_formats:
            raise ValueError(f"Not correct 'period' param. Available period formats: {period_formats}")
        return value


IntervalDjangoSchedule = IntervalSchedule
