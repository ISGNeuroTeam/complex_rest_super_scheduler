from django_celery_beat.models import PeriodicTask as DjangoPeriodicTask
from typing import Optional, Tuple

from ..utils.get_schedule import get_schedule_name_by_schedule_class
from ..utils.kwargs_parser import KwargsParser

from .format import TaskCreateFormat, TaskDeleteFormat


class PeriodicTask:

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
    def get_or_create(cls, schedule, task_kwargs: dict) -> Optional[str]:
        """
        Add periodic task to django database.

        :param schedule: schedule class from super_scheduler.schedule.SCHEDULES
        :param task_kwargs: task kwargs
        :return: optional error msg
        """

        task_kwargs, msg = KwargsParser.parse_kwargs(task_kwargs, TaskCreateFormat)
        if task_kwargs is None:
            return msg

        schedule_name, msg = cls._get_schedule_name_by_schedule_class(schedule)
        if schedule_name is None:
            return msg

        DjangoPeriodicTask.objects.get_or_create(
            **{schedule_name: schedule},
            **task_kwargs,
        )

        return None

    @classmethod
    def delete(cls, task_kwargs: dict) -> Optional[str]:
        """
        Delete periodic task with unused schedules.

        :param task_kwargs: task kwargs
        :return: optional error msg
        """

        task_kwargs, msg = KwargsParser.parse_kwargs(task_kwargs, TaskDeleteFormat)
        if task_kwargs is None:
            return msg

        task = DjangoPeriodicTask.objects.get(
            **task_kwargs
        )

        task.delete()
        return None
