from django_celery_beat.models import CrontabSchedule
from typing import Optional
from pydantic import validator
from pydantic.fields import Field

from .base import BaseScheduleFormat


class CrontabFormat(BaseScheduleFormat):
    minute: str = Field(
        default="*",
        description="minute",
        example="--minute 50"
    )
    hour: str = Field(
        default="*",
        description="hour",
        example="--hour 10"
    )
    day_of_week: str = Field(
        default="*",
        description="day of week",
        example="--day_of_week mon,wed"
    )
    day_of_month: str = Field(
        default="*",
        description="day of month",
        example="--day_of_month 17,20"
    )
    month_of_year: str = Field(
        default="*",
        description="month of year",
        example="--month_of_year 1,3"
    )


CrontabDjangoSchedule = CrontabSchedule
