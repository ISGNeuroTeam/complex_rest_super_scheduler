from django_celery_beat.models import IntervalSchedule
from pydantic import validator
from pydantic.fields import Field

from .base import BaseScheduleFormat


class IntervalFormat(BaseScheduleFormat):

    every: int = Field(
        description="run every N * time range",
        example="--every 10"
    )
    period: str = Field(
        description="time range",
        example="--period minutes"
    )

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
