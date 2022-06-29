import super_logger, logging
import time
import requests

from core.celeryapp import app
from .utils.del_schedule import del_unused_schedules

from .settings import COMPLEX_REST_ADDRESS, JOBSMANAGER_TRANSIT, JOBSMANAGER_TRANSIT_MAKEJOB


logger = logging.getLogger('super_scheduler.tasks')


@app.task()
def test_logger():
    logger.info('Success task log.')
    time.sleep(1)


@app.task()
def trash_cleaner(clean_old_schedule: bool = True,):
    """
    Clean trash in database: delete unused schedules.

    :param clean_old_schedule: delete unused schedules
    """
    logger.info('Trash cleaning...')

    if clean_old_schedule:
        del_unused_schedules()

    logger.info('Trash cleaned.')


@app.task()
def otl_makejob(otl: str, complex_rest_address: str = COMPLEX_REST_ADDRESS,
                tws: int = 0, twf: int = 0, sid: int = 999999, ttl: int = 100, timeout: int = 100,
                username: str = 'admin'):
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

    if JOBSMANAGER_TRANSIT:
        url = f'http://{complex_rest_address}/{JOBSMANAGER_TRANSIT_MAKEJOB}'

        content = requests.post(url, data={'sid': sid,
                                           'original_otl': f'{otl} |head 1000',
                                           'tws': tws,
                                           'twf': twf,
                                           'username': username,
                                           'preview': 'false',
                                           'field_extraction': 'false',
                                           'cache_ttl': ttl,
                                           'timeout': timeout})

        logger.info(f'Calculated OTL line with content: {content.text}')
    else:
        logger.info("Add plugin 'JOBSMANAGER_TRANSIT'")
