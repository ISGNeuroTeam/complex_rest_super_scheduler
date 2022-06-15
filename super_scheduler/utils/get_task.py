from django_celery_beat.models import PeriodicTask
from inspect import getmembers, isfunction

from .. import tasks
from core.celeryapp import app


def get_all_periodic_tasks() -> set:
    """
    Return all periodic tasks from django model.
    """
    return set(PeriodicTask.objects.all())


def get_all_periodic_task_names() -> list:
    """
    Return all periodic task names from django model.
    """
    return [periodic_task.name for periodic_task in get_all_periodic_tasks()]


def get_all_task_names() -> set:
    """
    Return all task names.
    """
    return set(app.tasks.keys())
    # set_app_tasks = set(app.tasks.keys())
    # set_file_tasks = get_all_task_names_in_file()
    # return set_file_tasks
    # set_res = set_app_tasks.union(set_file_tasks)
    # return set_res


# def get_all_task_names_in_file() -> set:
#     """
#     Return all function task names from file 'tasks.py'.
#     """
#     return set(f"super_scheduler.tasks.{member}" for member in getmembers(tasks, isfunction))
