from django_celery_beat.models import PeriodicTask

from core.celeryapp import app


def get_all_active_tasks() -> dict:
    """
    Return all active tasks.

    return format: {hostname: [{task1: {"name": ..., }}]}
    """
    return app.control.inspect().active()


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


def get_all_periodic_task_full():
    res_p_tasks = {}
    p_task: PeriodicTask
    for p_task in get_all_periodic_tasks():
        tmp_p_task = {'task': p_task.task,
                      'name': p_task.name,
                      'args': p_task.args,
                      'kwargs': p_task.kwargs,
                      'enabled': p_task.enabled,
                      'one_off': p_task.one_off,
                      'priority': p_task.priority,
                      'total_run_count': p_task.total_run_count,
                      'start_time': p_task.start_time,
                      'expires': p_task.expires,
                      'date_changed': p_task.date_changed,
                      'last_run_at': p_task.last_run_at,}
        res_p_tasks[p_task.name] = tmp_p_task
    return res_p_tasks


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
