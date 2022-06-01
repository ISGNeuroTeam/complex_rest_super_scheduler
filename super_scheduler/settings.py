from celery.schedules import crontab
import configparser
from pathlib import Path

from core.settings.ini_config import merge_ini_config_with_defaults


default_ini_config = {
    'logging': {
        'level': 'INFO'
    },
    'db_conf': {
        'host': 'localhost',
        'port': '5432',
        'database':  'complex_rest_eva_plugin',
        'user': 'complex_rest_eva_plugin',
        'password': 'complex_rest_eva_plugin'
    }
}

# # # # # #  Configuration section  # # # # # # #

config_parser = configparser.ConfigParser()

config_parser.read(Path(__file__).parent / 'super_scheduler.conf')

ini_config = merge_ini_config_with_defaults(config_parser, default_ini_config)


CELERY_BEAT_SCHEDULE = {
    "trash cleaner": {
        "task": "super_scheduler.tasks.trash_cleaner",
        "schedule": crontab(minute='*/1')
    }
}


