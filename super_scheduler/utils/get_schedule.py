from typing import Optional, Union, Dict

from django_celery_beat.models import PeriodicTask

from ..schedule.schedule_objects import SCHEDULES, schedule_name2class, schedule_name2format
from .get_task import get_all_periodic_tasks


def get_schedule_subclass(schedule):
    """
    Get schedule class and return schedule subclass.

    :param schedule: schedule class
    :return: schedule subclass
    """
    return schedule.schedule


def get_all_schedules() -> set:
    """
    Return all schedules classes from django model merged into one set.
    """
    res_set = set()
    for schedule_class, schedule_format in SCHEDULES.values():
        res_set = res_set.union(set(schedule_class.objects.all()))

    return res_set


def get_all_schedules_subclasses(schedule_classes: Optional[Union[set, list, tuple]] = None) -> list:
    """
    Optional get schedules classes
    and return all schedules subclasses in string format from django model merged into one list, unhashable types.

    :param schedule_classes: optional schedule classes
    :returns: list with schedules subclasses
    """
    if schedule_classes is None:
        schedule_classes = get_all_schedules()
    return [schedule_class.schedule for schedule_class in schedule_classes]  # unhashable type: 'schedule'


def get_schedule_name_by_schedule_class(schedule) -> Optional[str]:
    """
    Find schedule name by schedule class.

    :param schedule: schedule class from super_scheduler.schedule.SCHEDULES global variable
    :return: optional schedule name
    """
    # нужно что-то более оптимизированное и лаконичное
    # не удается получить доступ ко внутреннему классу Meta, у которого есть название типа расписания
    # При попытке обратиться к Meta: AttributeError: type object 'IntervalSchedule' has no attribute 'Meta'
    for key, (schedule_class, schedule_format) in SCHEDULES.items():
        if issubclass(type(schedule), schedule_class):
            return key
    return None


def get_schedule_name_from_task(task: PeriodicTask):
    """

    :param task: PeriodicTask object
    :return: schedule class (django model)
    """
    # similar to PeriodicTask.schedule because this method returns subclass, not schedule class!
    if task.crontab:
        schedule_name = 'crontab'
    elif task.interval:
        schedule_name = 'interval'
    elif task.solar:
        schedule_name = 'solar'
    elif task.clocked:
        schedule_name = 'clocked'
    else:
        raise ValueError("No schedule in 'task'. Check 'SCHEDULES' variable and 'PeriodicTask.schedule' method.")

    assert schedule_name in SCHEDULES, ValueError(f"{schedule_name} not in 'SCHEDULES'")

    return schedule_name


def filter_unused_schedules_in_tasks(schedule_dict: Dict[str, any]) -> Dict[str, any]:
    """
    Remove from dict schedules which is used in periodic tasks.

    :param schedule_dict: dict with schedule subclass (str) and schedule class
    :return: schedule_dict without used schedules in periodic tasks, can be empty
    """
    all_tasks = get_all_periodic_tasks()
    for task in all_tasks:
        # task: PeriodicTask
        task_schedule_str = str(task.schedule)
        if task_schedule_str in schedule_dict:
            del schedule_dict[task_schedule_str]
    return schedule_dict


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


def get_schedule_class_and_format_by_name(schedule_name: str) -> tuple:
    """
    Get schedule name and return schedule class with kwargs format.

    :param schedule_name: schedule name
    :return: schedule class & schedule format
    """
    return schedule_name2class(schedule_name), schedule_name2format(schedule_name)
