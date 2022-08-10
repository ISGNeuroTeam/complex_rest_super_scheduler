from django_celery_beat.models import PeriodicTask
from requests.exceptions import RequestException
from pottery import RedisCounter
from typing import Optional
from redis import Redis
import requests
import logging
import celery
import json
import time
import os

from rest.response import status

from core.celeryapp import app
from core.settings.base import REDIS_CONNECTION_STRING
from .settings import \
    COMPLEX_REST_ADDRESS, JOBSMANAGER_TRANSIT, \
    MAX_RETRIES, RETRY_JITTER, MAX_RETRY_BACKOFF, AUTO_DISABLE
from .utils.del_schedule import del_unused_schedules
from .utils.celery_task import get_periodic_task_names_by_task_kwargs, \
    get_periodic_task_names_by_task_name, \
    get_task_name_by_class
from .utils.get_task import get_all_active_tasks


logger = logging.getLogger("super_scheduler.tasks")


# os.getlogin() now work for WSL
def get_current_user() -> str:
    try:
        return os.getlogin()
    except:
        logger.warning("Not work os.getlogin, try os.getenv")
        return os.getenv('username')


class BaseTask(celery.Task):

    MAX_ERROR_COUNTER = MAX_RETRIES

    # my init
    def init(self, task_id, args, kwargs):
        self.p_task_name = self._get_p_task_name(args, kwargs)
        # self.logger = logging.getLogger(f"super_scheduler.tasks {self.request.hostname} {self.p_task_name} {task_id}")
        self.logger = logging.getLogger(f"super_scheduler.task {self.p_task_name} {task_id}")

    def _get_p_task_names(self, args, kwargs) -> list:
        """
        OLD VERSION! NOT USE!
        Get periodic task name from task, args and kwargs.
        """
        p_task_names: list = get_periodic_task_names_by_task_name(task_name=get_task_name_by_class(self),
                                                                  args=args)
        self.logger.info(f'Found periodic task name with task {get_task_name_by_class(self)}, '
                         f'args {args} and kwargs {kwargs}')
        return p_task_names

    def _get_p_task_name(self, args, kwargs) -> str:
        """
        Get periodic task name from kwargs.
        """
        p_task_name = get_periodic_task_names_by_task_kwargs(kwargs)

        if not p_task_name:
            self.logger.error(f"Can't find periodic task name with task {get_task_name_by_class(self)}, args {args} "
                              f"and kwargs {kwargs}")
            raise ValueError(f"Can't find periodic task name with task {get_task_name_by_class(self)}, args {args} "
                             f"and kwargs {kwargs}")

        return p_task_name

    def _check_another_running_task(self, task_id, args, kwargs):
        p_task_name = self._get_p_task_name(args, kwargs)
        p_task_id = task_id

        running_tasks: list = get_all_active_tasks()[self.request.hostname]

        running_task: dict
        for running_task in running_tasks:
            running_p_task_id = running_task['id']
            args, kwargs = running_task['args'], running_task['kwargs']
            running_p_task_name = self._get_p_task_name(args, kwargs)

            if running_p_task_name == p_task_name and running_p_task_id != p_task_id:
                logger.error(f"Previous started periodic task with name {running_p_task_name} "
                             f"haven't been finished yet")
                raise ProcessLookupError(f"Previous started periodic task with name {running_p_task_name} "
                                         f"haven't been finished yet")

    def _disable_task_after_fails(self, args, kwargs, exc):

        p_task_name = self._get_p_task_name(args, kwargs)

        self.logger.error(f'Exception message: {exc}')
        self.logger.error(f"Total errors with task {p_task_name}: {self.request.retries}")

        if AUTO_DISABLE and self.request.retries > self.MAX_ERROR_COUNTER:
            self.logger.error(f"Too many errors. Disable periodic task '{p_task_name}'.")

            p_task = PeriodicTask.objects.get(name=p_task_name)
            p_task.enabled = False
            p_task.save()

    def before_start(self, task_id, args, kwargs):

        self.init(task_id, args, kwargs)
        self._check_another_running_task(task_id, args, kwargs)

    def on_retry(self, exc: str, task_id: str, args: list, kwargs: dict, einfo: str):

        self._disable_task_after_fails(args, kwargs, exc)

    def on_success(self, retval, task_id: str, args: list, kwargs: dict):
        pass


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
    },
)
def logger_msg(self, msg: str = None, **kwargs) -> None:
    self.logger.info(msg)


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
    },
)
def test_logger_msg_with_sleep(self, time_sleep: str, **kwargs) -> None:
    # sid = str(self.request.id)  # uuid.uuid4()

    self.logger.info(f'Test logger with sleep started.')
    time.sleep(int(time_sleep))
    self.logger.info(f'Test logger with sleep finished.')


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
    },
)
def trash_cleaner(self, clean_old_schedule: bool = True, **kwargs) -> None:
    """
    Clean trash in database: delete unused schedules.

    :param clean_old_schedule: delete unused schedules
    """
    # sid = str(self.request.id)  # uuid.uuid4()
    self.logger.info(f'Trash cleaning...')

    if clean_old_schedule:
        del_unused_schedules()

    self.logger.info(f'Trash cleaned.')


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
    },
)
def otlmakejob(self, otl: str, complex_rest_address: str = COMPLEX_REST_ADDRESS,
               tws: int = 0, twf: int = 0, sid: Optional[str] = None, ttl: int = 100, timeout: int = 100,
               username: str = 'admin', **kwargs) -> int:
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
    :return: status code

    """

    def request_error(content):
        self.logger.error(f'Content text: {content.text}.')
        self.logger.error(f'Status code: {content.status_code}.')
        raise RequestException

    def send_post_request_content_status(_url, _data, post=False, get=False) -> \
            (requests.Response, Optional[str]):
        if post:
            content = requests.post(_url, data=_data)
        elif get:
            content = requests.get(_url, data=_data)
        else:
            return None, None
        job_status = json.loads(content.content)['status'] if content.status_code == 200 else None
        return content, job_status

    def makejob() -> requests.Response:
        self.logger.info(f'Sending request on url: {makejob_url}; data: {data}.')

        content, job_status = send_post_request_content_status(makejob_url, data, post=True)

        if content.status_code != 200:
            request_error(content)

        self.logger.info(f'Created job.')
        return content

    def checkjob() -> requests.Response:

        self.logger.info(f'Sending request on url: {checkjob_url}.')

        content, job_status = send_post_request_content_status(checkjob_url, data, get=True)

        time_start = time.time()
        while job_status == 'running':
            time.sleep(1)
            content, job_status = send_post_request_content_status(checkjob_url, data, get=True)
            if time.time() - time_start > 60:
                raise TimeoutError

        if content.status_code != 200:
            request_error(content)

        self.logger.info(f'Checked job.')
        return content

    def getresult() -> requests.Response:

        self.logger.info(f'Sending request on url: {getresult_url}.')

        content, job_status = send_post_request_content_status(getresult_url, data, get=True)

        if content.status_code != 200:
            request_error(content)

        self.logger.info(f'Get result job.')
        return content

    sid = sid if sid else str(self.request.id)

    if not JOBSMANAGER_TRANSIT:
        self.logger.error("Add plugin jobsmanager.")
        raise ImportError("Add plugin jobsmanager.")

    base_url = f'http://{complex_rest_address}/{JOBSMANAGER_TRANSIT}'
    makejob_url = base_url + '/makejob'
    checkjob_url = base_url + '/checkjob'
    getresult_url = base_url + '/getresult'

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
    content = makejob()

    # check job; wait finish
    content = checkjob()

    # get job
    # content = getresult()

    self.logger.info(f'Finished task: {self.request.id}.')
    return status.HTTP_200_OK


def group_otlmakejob(otl: str, complex_rest_address: str = COMPLEX_REST_ADDRESS,
                     tws: int = 0, twf: int = 0, sid: Optional[str] = None, ttl: int = 100, timeout: int = 100,
                     username: str = 'admin', **kwargs):
    pass


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
