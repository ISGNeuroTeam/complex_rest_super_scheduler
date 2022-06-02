from django_celery_beat.models import PeriodicTask
from typing import Optional
from pydantic import validator

from ..kwargs_parser import KwargsParser, BaseFormat as BaseTaskFormat
from .get_task import get_all_periodic_task_names, get_all_periodic_tasks


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
            raise ValueError(f"Periodic task name {value} does not exist")
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
    def delete(cls, task_kwargs: dict) -> Optional[str]:
        """
        Delete periodic task with unused schedules.

        :param task_kwargs: task kwargs
        :return: optional error msg
        """

        task_kwargs, msg = cls.parse_kwargs(task_kwargs, TaskDeleteFormat)
        if task_kwargs is None:
            return msg

        task = PeriodicTask.objects.get(
            **task_kwargs
        )

        task.delete()
        return None
