from django_celery_beat.models import CrontabSchedule

from .base import BaseScheduleFormat


class CrontabFormat(BaseScheduleFormat):
    minute: str = '*'
    hour: str = '*'
    day_of_week: str = '*'
    day_of_month: str = '*'
    month_of_year: str = '*'


CrontabDjangoSchedule = CrontabSchedule
