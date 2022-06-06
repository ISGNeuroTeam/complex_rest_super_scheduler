from typing import Tuple, Optional

from ..utils.get_schedule import get_schedule_class_and_format_by_name, get_all_schedules_subclasses
from ..utils.kwargs_parser import KwargsParser

from .format import ScheduleCreateFormat, ScheduleDeleteFormat
from .schedule_objects import SCHEDULES, schedule_name2class


class Schedule:

    @classmethod
    def get_or_create(cls, schedule_kwargs: dict) -> Tuple[any, Optional[str]]:
        """
        Create schedule class with validation format.

        :param schedule_kwargs: schedule kwargs
        :return: schedule class & None | None & error msg
        """

        schedule_name_dict, msg = KwargsParser.parse_kwargs(schedule_kwargs, ScheduleCreateFormat)
        if schedule_name_dict is None:
            return None, msg

        schedule_class, schedule_format = get_schedule_class_and_format_by_name(schedule_name_dict['name'])

        schedule_kwargs, msg = KwargsParser.parse_kwargs(schedule_kwargs, schedule_format)
        if schedule_kwargs is None:
            return None, msg

        schedule, created = schedule_class.objects.get_or_create(
            **schedule_kwargs,
        )

        return None if schedule is False else schedule, None if isinstance(created, bool) else "Can't create schedule"

    @classmethod
    def delete_by_schedule_subclass(cls, schedule_name: str, schedule_subclass) -> Tuple[bool, Optional[str]]:
        """
        Delete schedule class by schedule subclass.

        :param schedule_name: schedule type (ex.: crontab, clocked, interval, solar)
        :param schedule_subclass: schedule subclass
        :return: success status & optional error msg
        """

        if schedule_name not in SCHEDULES:
            return False, f"Not exist schedule with name: {schedule_name}"

        if schedule_subclass not in get_all_schedules_subclasses():
            return False, f"Not exist schedule with schedule_subclass: {schedule_subclass}"

        schedule_name2class(schedule_name).from_schedule(schedule_subclass).delete()
        return True, None

    @classmethod
    def delete(cls, schedule_kwargs: dict) -> Optional[str]:
        """
        Delete schedule by schedule kwargs.

        :param schedule_kwargs: schedule kwargs
        :return: optional error msg
        """

        schedule_kwargs, msg = KwargsParser.parse_kwargs(schedule_kwargs, ScheduleDeleteFormat)
        if schedule_kwargs is None:
            return msg

        schedule_class, schedule_format = get_schedule_class_and_format_by_name(schedule_kwargs['name'])

        schedule_kwargs, msg = KwargsParser.parse_kwargs(schedule_kwargs, schedule_format)
        if schedule_kwargs is None:
            return msg

        schedule = schedule_class.objects.get(
            **schedule_kwargs,
        )
        schedule.delete()
        return None
