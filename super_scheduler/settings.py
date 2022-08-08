from celery.schedules import crontab
import configparser
from pathlib import Path

# from core.settings.ini_config import merge_ini_config_with_defaults


default_ini_config = {
    'logging': {
        'level': 'DEBUG'
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

# API

if 'api' not in ini_config:
    raise ValueError("Add [api] in config")
JOBSMANAGER_TRANSIT = ini_config['api'].get('jobmanager', None) if 'api' in ini_config else None
AUTH_URL = ini_config['api'].get('auth', None) if 'api' in ini_config else None
SUPER_SCHEDULER_URL = ini_config['api'].get('super_scheduler_task', None) if 'api' in ini_config else None

# CELERY

if 'celery' not in ini_config:
    raise ValueError("Add [celery] in config")
MAX_RETRIES = int(ini_config['celery'].get('max_retries', '5'))
RETRY_JITTER = int(ini_config['celery'].get('retry_jitter', '3'))
MAX_RETRY_BACKOFF = int(ini_config['celery'].get('max_retry_backoff', '300'))
AUTO_DISABLE = bool(ini_config['celery'].get('auto-disable', 'False'))

# STATIC SCHEDULES

CELERY_BEAT_SCHEDULE = {
    "trash cleaner": {
        "task": "super_scheduler.tasks.trash_cleaner",
        "schedule": crontab(minute='*/1')
    }
}


