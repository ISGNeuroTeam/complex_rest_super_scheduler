from django_celery_beat.models import PeriodicTask
from typing import Optional, Tuple
from pydantic import validator

from plugins.super_scheduler.utils.kwargs_parser import KwargsParser, BaseFormat as BaseParserFormat
from plugins.super_scheduler.utils.task.get_task import get_all_periodic_task_names, get_all_task_names
from plugins.super_scheduler.utils.schedule.get_schedule import get_schedule_name_by_schedule_class


class TaskCreateFormat(BaseParserFormat):
    """
    Task create format.
    See PeriodicTask doc for additional args.
    """
    task: str
    args: list = []
    kwargs: dict = {}
    one_off: bool = False

    @validator('name')
    def name_validator(cls, value: str) -> str:
        """
        Check duplicate periodic task name in django database.
        """
        if value in get_all_periodic_task_names():
            raise ValueError("Duplicate periodic task name")
        return value

    @validator('task')
    def task_exist(cls, value: str) -> str:
        """
        Check exist task.
        """
        if value not in get_all_task_names():
            raise ValueError("Not exist task name")
        return value


class AddPeriodicTask(KwargsParser):

    @classmethod
    def _get_schedule_name_by_schedule_class(cls, schedule) -> Tuple[Optional[str], Optional[str]]:
        """
        Find schedule name by schedule class.

        :param schedule: schedule class from super_scheduler.schedule.SCHEDULES global variable
        :return: schedule name & None | None & msg error
        """
        schedule_name = get_schedule_name_by_schedule_class(schedule)
        if schedule is None:
            return None, "Not correct schedule name in 'SCHEDULES'"
        return schedule_name, None

    @classmethod
    def create(cls, schedule, task_kwargs: dict) -> Tuple[bool, Optional[str]]:
        """
        Add periodic task to django database.

        :param schedule: schedule class from super_scheduler.schedule.SCHEDULES
        :param task_kwargs: task kwargs
        :return: success status & optional error msg
        """

        task_kwargs, msg = cls.parse_kwargs(task_kwargs, TaskCreateFormat)
        if task_kwargs is None:
            return False, msg

        schedule_name, msg = cls._get_schedule_name_by_schedule_class(schedule)
        if schedule_name is None:
            return False, msg

        PeriodicTask.objects.get_or_create(
            **{schedule_name: schedule},
            **task_kwargs,
        )

        return True, None
