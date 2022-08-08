import json
import logging
import ast
import os
import time
from typing import Optional
import celery
from redis import Redis
from pottery import RedisCounter
from django_celery_beat.models import PeriodicTask

import requests
from requests.exceptions import RequestException

from core.celeryapp import app
from core.settings.base import REDIS_CONNECTION_STRING
from .settings import \
    COMPLEX_REST_ADDRESS, JOBSMANAGER_TRANSIT, \
    MAX_RETRIES, RETRY_JITTER, MAX_RETRY_BACKOFF, AUTO_DISABLE
from .utils.del_schedule import del_unused_schedules


app.conf.update(result_extended=True)
logger = logging.getLogger('super_scheduler.tasks')


# os.getlogin() now work for WSL
def get_current_user() -> str:
    try:
        return os.getlogin()
    except:
        logger.warning("Not work os.getlogin, try os.getenv")
        return os.getenv('username')


def get_task_id_by_class(task_class: celery.Task) -> str:
    return task_class.request.id


def get_task_name_by_class(task_class: celery.Task) -> str:
    return task_class.request.task


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


def get_periodic_task_names_by_task_kwargs(task_kwargs: dict) -> Optional[str]:
    return task_kwargs.get('name', None)


class BaseTask(celery.Task):

    MAX_ERROR_COUNTER = MAX_RETRIES

    def _create_unique_task_name(self, args: list, kwargs: dict):
        task_name = get_task_name_by_class(self)
        return f'Task: {task_name}; args: {args}; kwargs: {kwargs}'

    def on_retry(self, exc: str, task_id: str, args: list, kwargs: dict, einfo: str):
        # logger.error('kwargs: ' + str(kwargs))
        p_task_name = get_periodic_task_names_by_task_kwargs(kwargs)
        # logger.error('p_task_name: ' + str(p_task_name))
        if p_task_name:
            p_task_names = [p_task_name]
        else:
            p_task_names: list = get_periodic_task_names_by_task_name(task_name=get_task_name_by_class(self),
                                                                      args=args)
        # logger.error('p_task_names: ' + str(p_task_names))
        if not p_task_names:
            logger.error(f"Can't find periodic task name with task {get_task_name_by_class(self)}, args {args} "
                         f"and kwargs {kwargs}")
            raise ValueError(f"Can't find periodic task name with task {get_task_name_by_class(self)}, args {args} "
                             f"and kwargs {kwargs}")

        unique_task_name = self._create_unique_task_name(args, kwargs)
        redis = Redis.from_url(REDIS_CONNECTION_STRING)
        c = RedisCounter(redis=redis, key=unique_task_name)
        c['errors_counter'] += 1
        logger.error('Exception text: ' + str(exc))
        logger.error(f"Errors number in tasks '{p_task_names}': {str(c['errors_counter'])}")
        if AUTO_DISABLE and c['errors_counter'] > self.MAX_ERROR_COUNTER:
            logger.error(f"Too many errors. Disable {unique_task_name}.")
            for p_task_name in p_task_names:
                p_task = PeriodicTask.objects.get(name=p_task_name)
                p_task.enabled = False
                p_task.save()
            c['errors_counter'] = 0

    def on_success(self, retval, task_id: str, args: list, kwargs: dict):
        unique_task_name = self._create_unique_task_name(args, kwargs)
        redis = Redis.from_url(REDIS_CONNECTION_STRING)
        c = RedisCounter(redis=redis, key=unique_task_name)
        c['errors_counter'] = 0


@app.task(bind=True)
def logger_msg(self, msg: str = None) -> None:
    sid = str(self.request.id)  # uuid.uuid4()
    logger.info(sid + ' ' + msg)


@app.task(bind=True)
def trash_cleaner(self, clean_old_schedule: bool = True,) -> None:
    """
    Clean trash in database: delete unused schedules.

    :param clean_old_schedule: delete unused schedules
    """
    sid = str(self.request.id)  # uuid.uuid4()
    logger.info(f'{sid} Trash cleaning...')

    if clean_old_schedule:
        del_unused_schedules()

    logger.info(f'{sid} Trash cleaned.')


# priority
@app.task(
    base=BaseTask,
    bind=True,  # use for more info in self param
    autoretry_for=(RequestException,),
    retry_backoff=True,
    result_extended=True,
    retry_kwargs={
        'max_retries': MAX_RETRIES,
        'retry_jitter': RETRY_JITTER,
        'retry_backoff_max': MAX_RETRY_BACKOFF,
        'result_extended': True,
    },
)
def otlmakejob(self, otl: str, complex_rest_address: str = COMPLEX_REST_ADDRESS,
               tws: int = 0, twf: int = 0, sid: Optional[str] = None, ttl: int = 100, timeout: int = 100,
               username: str = 'admin', **kwargs) -> None:
    """
    Run the OTL line on a schedule.
    For task.request: https://docs.celeryq.dev/en/stable/userguide/tasks.html#task-request-info.
    Frequently Asked Questions: https://docs.celeryq.dev/en/stable/faq.html#faq-acks-late-vs-retry.


    :param otl: OTL line
    :param complex_rest_address: complex_rest address 'host:port'
    :param sid: Search ID
    :param tws: Start search time (epoch)
    :param twf: End search time (epoch)
    :param ttl: timeout cache_ttl
    :param timeout: timeout
    :param username: username

    """

    def send_post_request_content_status(_url, _data, post=False, get=False) -> (requests.Response, Optional[str]):
        if post:
            content = requests.post(_url, data=_data)
        elif get:
            content = requests.get(_url, data=_data)
        else:
            return None, None
        job_status = json.loads(content.content)['status'] if content.status_code == 200 else None
        return content, job_status

    def makejob() -> requests.Response:
        logger.info(f'{sid} Sending request on url: {makejob_url}; data: {data}.')

        content, job_status = send_post_request_content_status(makejob_url, data, post=True)

        if content.status_code != 200:
            logger.error(f'{sid} Content text: {content.text}.')
            logger.error(f'{sid} Status code: {content.status_code}.')
            raise RequestException

        logger.info(f'{sid} Created job.')
        return content

    def checkjob() -> requests.Response:

        logger.info(f'{sid} Sending request on url: {checkjob_url}.')

        content, job_status = send_post_request_content_status(checkjob_url, data, get=True)

        time_start = time.time()
        while job_status == 'running':
            time.sleep(1)
            content, job_status = send_post_request_content_status(checkjob_url, data, get=True)
            if time.time() - time_start > 60:
                raise TimeoutError

        if content.status_code != 200:
            logger.error(f'{sid} Content text: {content.text}.')
            logger.error(f'{sid} Status code: {content.status_code}.')
            raise RequestException

        logger.info(f'{sid} Checked job.')
        return content

    sid = sid if sid else str(self.request.id)
    # sid = sid if sid else str(uuid.uuid4())

    if not JOBSMANAGER_TRANSIT:
        logger.error("Add plugin jobsmanager.")
        raise ImportError("Add plugin jobsmanager.")

    base_url = f'http://{complex_rest_address}/{JOBSMANAGER_TRANSIT}'
    makejob_url = base_url + '/makejob'
    checkjob_url = base_url + '/checkjob'

    data = {'sid': sid,
            'original_otl': f'{otl} |head 1000',
            'tws': tws,
            'twf': twf,
            'username': username,
            'preview': 'false',
            'field_extraction': 'false',
            'cache_ttl': ttl,
            'timeout': timeout}

    # make job
    makejob()

    # check job; wait finish
    checkjob()

    # get job

    # logger.info(f'{sid} Calculated OTL line with content: {content.text}')
    # logger.info(f'{sid} Calculated OTL line with content: {content.status_code}')
    logger.info(f'{sid} Finished task: {self.request.id}.')


# import subprocess
# @app.task()
# def script(filepath: str) -> None:
#     """
#     Execute bash-scripts
#
#     :param filepath: path to bash-script
#     """
#     logger.info(f'Get bash script to execute: {filepath}.')
#     if get_current_user() == 'root':
#         raise FileExistsError("Don't start complex_rest with 'root' user")
#     if not os.path.exists(filepath):
#         raise FileExistsError("Not exist path")
#     if not os.path.isfile(filepath):
#         raise FileExistsError("Not file")
#     if not os.access(filepath, os.X_OK):
#         raise FileExistsError("Can't execute, check permissions")
#     output = subprocess.check_output(["bash", filepath])
#     logger.info(f'Result: {output.decode()}.')
#     logger.info(f'Success execute bash-script.')
#
#
# @app.task()
# def commands(*args) -> None:
#     """
#     Execute bash commands.
#
#     :param args: linux commands, example: ["ls", "-la"]
#     """
#     logger.info(f'Get linux commands to execute: {args}.')
#     if get_current_user() == 'root':
#         raise FileExistsError("Don't start complex_rest with 'root' user")
#     process = subprocess.Popen(args, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
#     output, error = process.communicate()
#     logger.info(f'Result: {output.decode()}. \nError: {error.decode()}')
#     logger.info(f'Success execute linux commands.')
