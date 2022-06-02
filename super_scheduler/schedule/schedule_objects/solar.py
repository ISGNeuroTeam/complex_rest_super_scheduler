from django_celery_beat.models import SolarSchedule, SOLAR_SCHEDULES
from typing import Union
from pydantic import validator

from .base import BaseScheduleFormat


class SolarFormat(BaseScheduleFormat):
    event: str
    latitude: Union[int, float]
    longitude: Union[int, float]

    @validator("event")
    def event_check(cls, value):
        """
        Check solar event.
        """
        solar_events = (event[0] for event in SOLAR_SCHEDULES)
        if value not in solar_events:
            raise ValueError(f"Not correct 'event' param. Available events: {solar_events}")
        return value

    @validator("latitude")
    def latitude_check(cls, value):
        """
        Check latitude min and max value.
        """
        if not -180 <= value <= 180:
            raise ValueError("'Latitude' param must be >= -180 and <= 180")
        return value

    @validator("longitude")
    def longitude_check(cls, value):
        """
        Check longitude min and max value.
        """
        if not -180 <= value <= 180:
            raise ValueError("'Longitude' param must be >= -180 and <= 180")
        return value


SolarDjangoSchedule = SolarSchedule
