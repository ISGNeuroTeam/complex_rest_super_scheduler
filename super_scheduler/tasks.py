import logging
import time

from core.celeryapp import app
from plugins.super_scheduler.utils.schedule.del_schedule import del_unused_schedules


log = logging.getLogger('super_scheduler.tasks')


@app.task()
def test_logger():
    log.info('Success task log.')
    time.sleep(1)


@app.task()
def trash_cleaner(clean_old_schedule: bool = True,):
    """
    Clean trash in database: delete unused schedules.

    :param clean_old_schedule: delete unused schedules
    """
    log.info('Trash cleaning...')

    if clean_old_schedule:
        del_unused_schedules()

    log.info('Trash cleaned.')
