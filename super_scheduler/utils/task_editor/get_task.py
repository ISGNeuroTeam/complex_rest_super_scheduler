from django_celery_beat.models import PeriodicTask

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
