from celery.schedules import crontab
import configparser
from pathlib import Path

# from core.settings.ini_config import merge_ini_config_with_defaults


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

# ini_config = merge_ini_config_with_defaults(config_parser, default_ini_config)
ini_config = config_parser

COMPLEX_REST_HOST = ini_config['address_rest']['host']
COMPLEX_REST_PORT = ini_config['address_rest']['port']
COMPLEX_REST_ADDRESS = COMPLEX_REST_HOST + ':' + COMPLEX_REST_PORT

# CLIENT

USERNAME = ini_config['client'].get('username', None) if 'client' in ini_config else None
PASSWORD = ini_config['client'].get('password', None) if 'client' in ini_config else None

# PLUGINS

JOBSMANAGER_TRANSIT = 'jobsmanager_transit' in ini_config
JOBSMANAGER_TRANSIT_MAKEJOB = ini_config['jobsmanager_transit'].get('makejob', None)

# STATIC SCHEDULES

CELERY_BEAT_SCHEDULE = {
    "trash cleaner": {
        "task": "super_scheduler.tasks.trash_cleaner",
        "schedule": crontab(minute='*/1')
    }
}


