import super_logger, logging
import os
import requests
import subprocess

from core.celeryapp import app
from .utils.del_schedule import del_unused_schedules

from .settings import COMPLEX_REST_ADDRESS, JOBSMANAGER_TRANSIT_MAKEJOB


logger = logging.getLogger('super_scheduler.tasks')


# os.getlogin() now work for WSL
def get_current_user() -> str:
    return os.getenv('username')


@app.task()
def logger(msg: str = None) -> None:
    logger.info(msg)


@app.task()
def trash_cleaner(clean_old_schedule: bool = True,) -> None:
    """
    Clean trash in database: delete unused schedules.

    :param clean_old_schedule: delete unused schedules
    """
    logger.info('Trash cleaning...')

    if clean_old_schedule:
        del_unused_schedules()

    logger.info('Trash cleaned.')


@app.task()
def otlmakejob(otl: str, complex_rest_address: str = COMPLEX_REST_ADDRESS,
               tws: int = 0, twf: int = 0, sid: int = 999999, ttl: int = 100, timeout: int = 100,
               username: str = 'admin') -> None:
    """
    Run the OTL line on a schedule.

    :param otl: OTL line
    :param complex_rest_address: complex_rest address 'host:port'
    :param sid: Search ID
    :param tws: Start search time (epoch)
    :param twf: End search time (epoch)
    :param ttl: timeout cache_ttl
    :param timeout: timeout
    :param username: username

    """
    logger.info(f'Calculating OTL line: {otl}')

    if JOBSMANAGER_TRANSIT_MAKEJOB:
        url = f'http://{complex_rest_address}/{JOBSMANAGER_TRANSIT_MAKEJOB}'
        data = {'sid': sid,
                'original_otl': f'{otl} |head 1000',
                'tws': tws,
                'twf': twf,
                'username': username,
                'preview': 'false',
                'field_extraction': 'false',
                'cache_ttl': ttl,
                'timeout': timeout}

        content = requests.post(url, data=data)

        logger.info(f'Calculated OTL line with content: {content.text}')
    else:
        logger.info("Add plugin 'JOBSMANAGER_TRANSIT'")


@app.task()
def script(filepath: str) -> None:
    """
    Execute bash-scripts

    :param filepath: path to bash-script
    """
    logger.info(f'Get bash script to execute: {filepath}.')
    if get_current_user() == 'root':
        raise FileExistsError("Don't start complex_rest with 'root' user")
    if not os.path.exists(filepath):
        raise FileExistsError("Not exist path")
    if not os.path.isfile(filepath):
        raise FileExistsError("Not file")
    if not os.access(filepath, os.X_OK):
        raise FileExistsError("Can't execute, check permissions")
    output = subprocess.check_output(["bash", filepath])
    logger.info(f'Result: {output.decode()}.')
    logger.info(f'Success execute bash-script.')


@app.task()
def commands(*args) -> None:
    """
    Execute bash commands.

    :param args: linux commands, example: ["ls", "-la"]
    """
    logger.info(f'Get linux commands to execute: {args}.')
    if get_current_user() == 'root':
        raise FileExistsError("Don't start complex_rest with 'root' user")
    process = subprocess.Popen(args, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
    output, error = process.communicate()
    logger.info(f'Result: {output.decode()}. \nError: {error.decode()}')
    logger.info(f'Success execute linux commands.')
