from typing import Tuple, Optional
from pydantic import validator

from plugins.super_scheduler.schedule import SCHEDULES
from plugins.super_scheduler.utils.kwargs_parser import KwargsParser, BaseFormat as BaseParserFormat


class ScheduleCreateFormat(BaseParserFormat):
    """
    Parse main required params to identify schedule format.
    """

    @validator('name', allow_reuse=True)
    def name_validator(cls, value: str) -> str:
        """
        Check duplicated names in django database.
        """
        if value not in SCHEDULES:
            raise ValueError(f"Not exist schedule with name: {value}")
        return value


class AddSchedule(KwargsParser):

    @classmethod
    def _get_schedule_main_params(cls, schedule_name_dict: dict) -> tuple:
        """
        Get schedule_name_dict with 'name' key and return schedules class with kwargs format.

        :param schedule_name_dict:
        :return: schedule class & schedule format
        """
        schedule_name = schedule_name_dict['name']
        schedule_class, schedule_format = SCHEDULES[schedule_name]
        return schedule_class, schedule_format

    @classmethod
    def create(cls, schedule_kwargs: dict) -> Tuple[any, Optional[str]]:
        """
        Create schedule class with validation format.

        :param schedule_kwargs: schedule kwargs
        :return: schedule class & None | None & error msg
        """

        schedule_name_dict, msg = cls.parse_kwargs(schedule_kwargs, ScheduleCreateFormat)
        if schedule_name_dict is None:
            return None, msg

        schedule_class, schedule_format = cls._get_schedule_main_params(schedule_name_dict)

        schedule_kwargs, msg = cls.parse_kwargs(schedule_kwargs, schedule_format)
        if schedule_kwargs is None:
            return None, msg

        schedule, created = schedule_class.objects.get_or_create(
            **schedule_kwargs,
        )

        return None if schedule is False else schedule, created
