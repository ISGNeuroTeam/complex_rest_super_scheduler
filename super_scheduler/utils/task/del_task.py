from django_celery_beat.models import PeriodicTask
from typing import Optional, Tuple
from pydantic import validator

from plugins.super_scheduler.utils.kwargs_parser import KwargsParser, BaseFormat as BaseTaskFormat
from plugins.super_scheduler.utils.task.get_task import get_all_periodic_task_names, get_all_periodic_tasks


class TaskDeleteFormat(BaseTaskFormat):
    """
    Task delete format.
    """

    @validator('name', allow_reuse=True)
    def name_validator(cls, value: str) -> str:
        """
        Check exist task.
        """
        if value not in get_all_periodic_task_names():
            raise ValueError("Not exist periodic task name")
        return value


def check_schedule_in_another_tasks(schedule_subclass, task_name: str = None) -> bool:
    """
    Check schedule used another tasks.

    :param schedule_subclass: schedule subclass
    :param task_name: task name
    :return: success status
    """
    for task_iter in get_all_periodic_tasks():
        if (task_iter.schedule == schedule_subclass) and \
                ((task_name is None) or (task_name and task_iter.name != task_name)):
            return True
    return False


class DelPeriodicTask(KwargsParser):

    @classmethod
    def delete(cls, task_kwargs: dict) -> Tuple[bool, Optional[str]]:
        """
        Delete periodic task with unused schedules.

        :param task_kwargs: task kwargs
        :return: success status & optional error msg
        """

        task_kwargs, msg = cls.parse_kwargs(task_kwargs, TaskDeleteFormat)
        if task_kwargs is None:
            return False, msg

        task = PeriodicTask.objects.get(
            **task_kwargs
        )

        task.delete()
        return True, None
