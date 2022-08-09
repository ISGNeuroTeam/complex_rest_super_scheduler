from typing import Optional
import ast

from django_celery_beat.models import PeriodicTask
import celery

import logging


logger = logging.getLogger("super_scheduler")


def get_periodic_task_names_by_task_kwargs(task_kwargs: dict) -> Optional[str]:
    return task_kwargs.get('name', None)


def get_periodic_task_names_by_task_name(
        task_name: str,
        args: Optional[list] = None,
        kwargs: Optional[dict] = None,
) -> Optional[list]:
    if not args:
        args = []
    if not kwargs:
        kwargs = {}
    all_periodic_tasks = PeriodicTask.objects.values('name', 'task', 'args', 'kwargs')
    p_task_names = []
    for p_task in all_periodic_tasks:
        if p_task['task'] == task_name and \
                ast.literal_eval(p_task['args']) == args and \
                ast.literal_eval(p_task['kwargs']) == kwargs:
            logger.info(f"Found periodic task {p_task['task']} with name {p_task['name']}")
            p_task_names += [p_task['name']]
    return p_task_names if p_task_names else None


def get_task_id_by_class(task_class: celery.Task) -> str:
    return task_class.request.id


def get_task_name_by_class(task_class: celery.Task) -> str:
    return task_class.request.task
