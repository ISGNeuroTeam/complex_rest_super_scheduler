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
def otl_makejob(otl: str, complex_rest_address: str = COMPLEX_REST_ADDRESS):
    """
    Run the OTL line on a schedule.

    :param otl: OTL line
    :param complex_rest_address: complex_rest address 'ip:port'
    """
    logger.info(f'Calculating OTL line: {otl}')

    if JOBSMANAGER_TRANSIT:
        url = f'http://{complex_rest_address}/{JOBSMANAGER_TRANSIT_MAKEJOB}'

        content = requests.post(url, data={'sid': 999999,
                                           'original_otl': f'{otl} |head 1000',
                                           'tws': 0,
                                           'twf': 0,
                                           'username': 'admin',
                                           'preview': 'false',
                                           'field_extraction': 'false',
                                           'cache_ttl': 100,
                                           'timeout': 100})

        logger.info(f'Calculated OTL line with content: {content.text}')
    else:
        logger.info("Add plugin 'JOBSMANAGER_TRANSIT'")
