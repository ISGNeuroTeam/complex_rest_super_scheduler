from django_celery_beat.models import ClockedSchedule
from pydantic import validator
from pydantic.fields import Field

from dateutil.parser import parse
from dateutil.tz import gettz

from core.settings.base import TIME_ZONE

from .base import BaseScheduleFormat


class ClockedFormat(BaseScheduleFormat):
    clocked_time: str = Field(
        description="datetime string",
        example="--clocked_time \"2023-11-28 01:01:01\""
    )

    @validator("clocked_time")
    def clocked_time_transformer(cls, value):
        """
        Transform string to datetime.
        """
        try:
            tzinfo = gettz(TIME_ZONE)
            value = parse(value, tzinfos={"PST": tzinfo, "PDT": tzinfo})
        except Exception as e:
            raise ValueError(f"Not correct 'clocked_time' param. Error: {e}")
        return value


ClockedDjangoSchedule = ClockedSchedule
