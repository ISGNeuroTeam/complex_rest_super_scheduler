from typing import Optional, Tuple
from pydantic import validator

from ...schedule import SCHEDULES, schedule_name2class
from ..kwargs_parser import KwargsParser, BaseFormat as BaseTaskFormat
from .get_schedule import (get_all_schedules_subclasses,
                           get_all_schedules,
                           filter_unused_schedules_in_tasks)
from .add_schedule import AddSchedule


def del_unused_schedules():
    """
    Delete unused schedules.
    """
    all_schedule_classes = list(get_all_schedules())
    all_schedule_subclasses = list(get_all_schedules_subclasses(all_schedule_classes))
    schedule_dict = {str(subclass_): class_
                     for class_, subclass_ in zip(all_schedule_classes, all_schedule_subclasses)}

    # delete used schedules from dict
    schedule_dict = filter_unused_schedules_in_tasks(schedule_dict)

    # delete unused schedules
    for key, val in schedule_dict.items():
        val.delete()


class ScheduleDeleteFormat(BaseTaskFormat):
    """
    Schedule delete format.
    """

    @validator('name', allow_reuse=True)
    def name_validator(cls, value: str) -> str:
        """
        Check exist schedule type.
        """
        if value not in SCHEDULES:
            raise ValueError(f"Schedule name {value} does not exist")
        return value


class DelSchedule(KwargsParser):

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

        schedule_kwargs, msg = cls.parse_kwargs(schedule_kwargs, ScheduleDeleteFormat)
        if schedule_kwargs is None:
            return msg

        schedule, msg = AddSchedule.create(schedule_kwargs)
        if schedule is None:
            return msg

        schedule.delete()
        return None

