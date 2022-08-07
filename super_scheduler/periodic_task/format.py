from pydantic import validator
from typing import Optional
import json
import datetime

from dateutil.parser import parse
from dateutil.tz import gettz

from core.settings.base import TIME_ZONE

from ..utils.get_task import get_all_periodic_task_names, get_all_task_names
from ..utils.kwargs_parser import BaseFormat as BaseTaskParserFormat


class TaskCreateFormat(BaseTaskParserFormat):
    """
    Task create format.
    See PeriodicTask doc for additional args.
    """
    task: str
    args: list = []
    kwargs: dict = {}
    one_off: bool = False
    priority: Optional[int] = None
    enabled: bool = True
    start_time: Optional[str] = None

    @validator('name')
    def name_validator(cls, value: str) -> str:
        """
        Check duplicate periodic task name in django database.
        """
        if value in get_all_periodic_task_names():
            raise ValueError(f"Duplicate periodic task name {value}")
        return value

    @validator('task')
    def task_exist(cls, value: str) -> str:
        """
        Check exist task.
        """
        if value not in get_all_task_names():
            raise ValueError(f"Task name {value} does not exist")
        return value

    @validator('args')
    def args_transform(cls, value: str) -> str:
        """
        Transform args to correct Django format - string.
        """
        return json.dumps(value)

    @validator('kwargs')
    def kwargs_transform(cls, value: str) -> str:
        """
        Transform kwargs to correct Django format - string.
        """
        return json.dumps(value)

    @validator('priority')
    def priority_transform(cls, value: int) -> str:
        """
        Check range and transform priority to correct Django format - string.
        """
        if value and not 0 < value < 255:
            raise ValueError("Priority must be int and between 0 and 255. "
                             "Supported by: RabbitMQ, Redis (priority reversed, 0 is highest).")
        return json.dumps(value)

    @validator("start_time")
    def start_time_transform(cls, value: str) -> str:
        """
        Parse & transform start_time to correct Django format - string.
        """
        try:
            tzinfo = gettz(TIME_ZONE)
            value = parse(value, tzinfos={"PST": tzinfo, "PDT": tzinfo})
        except Exception as e:
            raise ValueError(f"Not correct 'start_time' param. Error: {e}")
        return json.dumps(value)


class TaskDeleteFormat(BaseTaskParserFormat):
    """
    Task delete format.
    """

    @validator('name', allow_reuse=True)
    def name_validator(cls, value: str) -> str:
        """
        Check exist task.
        """
        if value not in get_all_periodic_task_names():
            raise ValueError(f"Periodic task name {value} does not exist")
        return value
