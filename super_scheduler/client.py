import argparse
import os
import json
import requests
from typing import Union

from settings import COMPLEX_REST_HOST, COMPLEX_REST_PORT, USERNAME, PASSWORD


def auth(address, username, password):
    def _save_token(content):
        os.makedirs('tmp/', exist_ok=True)
        token = content.json()['token']
        with open('tmp/auth_token', 'w') as f:
            f.write(token)
        return token

    url = f'http://{address}/auth/login'

    data = {
        'login': username,
        'password': password
    }

    content = requests.post(url, data=data)
    if content.status_code == 200:
        token = _save_token(content)
        return token
    print(content.status_code, content.text)
    raise ValueError("Can't get token")


def send_request(address, data, token, post: bool = False, delete: bool = False, get: bool = False):
    url = f'http://{address}/super_scheduler/v1/task/'
    headers = {"Authorization": f"Bearer {token}", 'Content-Type': 'application/json'}
    data = json.dumps(data)
    content = None
    if post:
        content = requests.post(url, data=data, headers=headers)
    elif delete:
        content = requests.delete(url, data=data, headers=headers)
    elif get:
        content = requests.get(url, data=data, headers=headers)
    if content is not None:
        print(content.status_code, content.text)


def parse_schedule(schedule_parsers, args):
    schedule_name = args.schedule_name

    schedule_dict = schedule_parsers[schedule_name].parse_known_args()[0].__dict__
    schedule_dict['name'] = schedule_dict['schedule_name']
    return schedule_dict


def data_construction(args, schedule_parsers) -> dict:
    # task args
    task = args.task
    task_args = [] if not args.task_args else args.task_args
    task_name = args.name
    one_off = args.one_off

    # schedule
    schedule_dict = parse_schedule(schedule_parsers, args)

    # construct data
    data = {
        'task':
            {
                'name': task_name,
                'task': task,
            },
        'schedule': schedule_dict,
    }

    if one_off:
        data['task']['one_off'] = one_off
    if task_args:
        data['task']['args'] = task_args
    return data


def client():
    """

    Example:

        -C -T super_scheduler.tasks.test_logger --one_off --name test_logger123
        clocked --clocked_time '2023-11-28 01:01:01'

    """

    parser = argparse.ArgumentParser(description='SuperScheduler client')

    parser.add_argument('-U', '--username', type=str, help=f'Username for authorization; default \'{USERNAME}\'', default=USERNAME)
    parser.add_argument('-P', '--password', type=str, help=f'User password for authorization; default \'{PASSWORD}\'', default=PASSWORD)

    parser.add_argument('--host', type=str, help=f'Ip complex_rest; default \'{COMPLEX_REST_HOST}\'', default=COMPLEX_REST_HOST)
    parser.add_argument('--port', type=str, help=f'Port complex_rest; default \'{COMPLEX_REST_PORT}\'', default=COMPLEX_REST_PORT)

    parser.add_argument('-C', '--create', action='store_true', help='Create periodic task')
    parser.add_argument('-D', '--delete', action='store_true', help='Delete periodic task')
    parser.add_argument('-G', '--get', action='store_true', help='Get all tasks')

    parser.add_argument('-T', '--task', type=str, help='Task for schedule; '
                                                       'example: super_scheduler.tasks.test_logger, '
                                                       'tasks.test_logger or test_logger')
    parser.add_argument('-Ta', '--task_args', type=str, nargs="*", help='Task args if necessary')
    parser.add_argument('-N', '--name', type=str, required=True, help='Periodic task name')
    parser.add_argument('--one_off', action='store_true', help="Run periodic task only ones; "
                                                               "always use with 'clocked' schedule")

    subparsers = parser.add_subparsers()

    # schedule subparsers
    schedule_parsers = {}

    crontab_parser = subparsers.add_parser('crontab')
    schedule_parsers['crontab'] = crontab_parser
    crontab_parser.add_argument('--minute', type=str, required=True, help=f'Default \'*\'')
    crontab_parser.add_argument('--hour', type=str, required=True, help=f'Default \'*\'')
    crontab_parser.add_argument('--day_of_week', type=str, required=True, help=f'Default \'*\'')
    crontab_parser.add_argument('--day_of_month', type=str, required=True, help=f'Default \'*\'')
    crontab_parser.add_argument('--month_of_year', type=str, required=True, help=f'Default \'*\'')
    crontab_parser.add_argument('--schedule_name', type=str, help="Schedule name; default 'crontab'", default="crontab")

    interval_parser = subparsers.add_parser('interval')
    schedule_parsers['interval'] = interval_parser
    interval_parser.add_argument('--every', type=int, required=True, help='Run every N * time range')
    interval_parser.add_argument('--period', type=str, required=True, help='Time range; example: minutes')
    interval_parser.add_argument('--schedule_name', type=str, help="Schedule name; default 'interval'", default="interval")

    solar_parser = subparsers.add_parser('solar')
    schedule_parsers['solar'] = solar_parser
    solar_parser.add_argument('--event', type=str, required=True, help='Solar events; example: dawn_astronomical; '
                                                      'see https://docs.celeryq.dev/en/stable/userguide/periodic-tasks.html#solar-schedules')
    solar_parser.add_argument('--latitude', type=Union[int, float], required=True, help='Current latitude')
    solar_parser.add_argument('--longitude', type=Union[int, float], required=True, help='Current longitude')
    solar_parser.add_argument('--schedule_name', type=str, help="Schedule name; default 'solar'", default="solar")

    clocked_parser = subparsers.add_parser('clocked')
    schedule_parsers['clocked'] = clocked_parser
    clocked_parser.add_argument('--clocked_time', type=str, required=True, help='Datetime format; example: 2023-11-28 01:01:01')
    clocked_parser.add_argument('--schedule_name', type=str, help="Schedule name; default 'clocked'", default="clocked")

    args = parser.parse_args()
    print(args)

    # auth
    username = args.username
    password = args.password
    if (username, password).count(None) > 0:
        raise ValueError("Set both username and password")

    # address
    host = args.host
    port = args.port
    address = host + ':' + port

    token = auth(address, username, password)

    # event args
    create = args.create
    delete = args.delete
    get = args.get
    if sum([create, delete, get]) != 1:
        raise ValueError("Set only one param: -C, -D or -G")

    data = data_construction(args, schedule_parsers)

    send_request(address, data, token, post=create, delete=delete, get=get)


if __name__ == "__main__":
    client()
