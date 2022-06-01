from django_celery_beat.models import PeriodicTask
from typing import Optional, Tuple
from pydantic import validator

from plugins.super_scheduler.utils.kwargs_parser import KwargsParser, BaseFormat as BaseParserFormat
from plugins.super_scheduler.utils.task.get_task import get_all_periodic_task_names, get_all_task_names
from plugins.super_scheduler.utils.schedule.del_schedule import DelSchedule
from plugins.super_scheduler.utils.schedule.get_schedule import get_schedule_name_by_schedule_class
from plugins.super_scheduler.utils.task.del_task import check_schedule_in_another_tasks
from plugins.super_scheduler.schedule import SCHEDULES
from plugins.super_scheduler.utils.task.add_task import TaskCreateFormat


class TaskModFormat(TaskCreateFormat):

    @validator('name')
    def name_validator(cls, value: str) -> str:
        """
        Check exist periodic task name in django database.

        :param value: exist task name
        :return: this value
        """
        if value not in get_all_periodic_task_names():
            raise ValueError(f"Not exist periodic task with name: {value}")
        return value


# EXAMPLE:
# def update_task(periodic_task_name: str, params):
#     task = PeriodicTask.objects.get(name="test_logger")
#     task.args = func_args
#     task.save()
#     pass


class ModPeriodicTask(KwargsParser):

    @classmethod
    def modify(cls, task_kwargs: dict, schedule=None) -> Tuple[bool, Optional[str]]:
        """
        Modify periodic task in django database, optional update schedule.

        :param task_kwargs: task kwargs
        :param schedule: schedule class from super_scheduler.schedule.SCHEDULES
        :return: status & optional error msg
        """

        task_kwargs, msg = cls.parse_kwargs(task_kwargs, TaskModFormat)
        if task_kwargs is None:
            return False, msg

        task: PeriodicTask = PeriodicTask.objects.get(name="test_logger")

        # ТАК ДЕЛАТЬ НЕЛЬЗЯ, ИНАЧЕ УДАЛИТСЯ ЗАДАЧА!
        # if schedule:
        #     if schedule.schedule != task.schedule:
        #         schedule_name = get_schedule_name_by_schedule_class(schedule)
        #         DelSchedule.delete_by_schedule_subclass(schedule_name, task.schedule)

        task.save()

        return True, None


