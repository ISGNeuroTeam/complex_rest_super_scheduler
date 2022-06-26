import argparse
import os
import json
import requests

from settings import COMPLEX_REST_ADDRESS, LOGIN, PASSWORD


def auth(args):
    def _save_token(content):
        os.makedirs('tmp/', exist_ok=True)
        token = content.json()['token']
        with open('tmp/auth_token', 'w') as f:
            f.write(token)
        return token

    url = f'http://{COMPLEX_REST_ADDRESS}/auth/login'
    login, password = LOGIN, PASSWORD
    if args.login and args.password:
        login, password = args.login, args.password
    elif args.login or args.password:
        raise ValueError("Enter login and password both")

    data = {
        'login': login,
        'password': password
    }

    content = requests.post(url, data=data)
    if content.status_code == 200:
        token = _save_token(content)
        return token
    raise ValueError("Can't get token")


def send_request(data, token, post: bool = False, delete: bool = False, get: bool = False):
    url = f'http://{COMPLEX_REST_ADDRESS}/super_scheduler/v1/task/'
    headers = {"Authorization": f"Bearer {token}", 'Content-Type': 'application/json'}
    content = None
    if post:
        content = requests.post(url, data=json.dumps(data), headers=headers)
    elif delete:
        content = requests.delete(url, data=json.dumps(data), headers=headers)
    elif get:
        content = requests.get(url, data=json.dumps(data), headers=headers)
    if content is not None:
        print(content.text)
        print(content.status_code)


# class Checker:
#
#     def check_event_args(self):
#         pass


def client():
    """

    Example:

        python client.py -C -T super_scheduler.tasks.test_logger --one_off --name test_logger123
        -S 'name=clocked' 'clocked_time=2023-11-28 01:01:01'

    """

    parser = argparse.ArgumentParser(description='SuperScheduler client')

    parser.add_argument('-L', '--login', type=str, help='User EVA login for authorization')
    parser.add_argument('-P', '--password', type=str, help='User EVA password for authorization')

    parser.add_argument('-C', '--create', action='store_true', help='Create periodic task')
    parser.add_argument('-D', '--delete', action='store_true', help='Delete periodic task')
    parser.add_argument('-G', '--get', action='store_true', help='Get all tasks')

    parser.add_argument('-T', '--task', type=str, required=True, help='Task for schedule; '
                                                                      'example: super_scheduler.tasks.test_logger')  # , choices=list("...")
    parser.add_argument('-Ta', '--task_args', type=str, nargs="*", help='Task args if necessary')
    parser.add_argument('-N', '--name', type=str, required=True, help='Periodic task name')
    parser.add_argument('--one_off', action='store_true', help="Run periodic task only ones; "
                                                               "always use with 'clocked' schedule")
    parser.add_argument('-S', '--schedule', type=str, nargs="*", required=True,
                        help='Schedule in dict format; '
                             "example: --schedule 'name=clocked' 'clocked_time=2023-11-28 01:01:01'")

    # TODO: add subparser for schedules

    args = parser.parse_args()
    token = auth(args)

    # event args
    create = args.create
    delete = args.delete
    get = args.get

    if sum([create, delete, get]) != 1:
        raise ValueError("Set only one param: -C, -D or -G")

    # task args
    task = args.task
    task_args = [] if not args.task_args else args.task_args
    task_name = args.name
    one_off = args.one_off
    schedule = args.schedule

    schedule_dict = {}
    for schedule_arg in schedule:
        splited = schedule_arg.split('=')
        schedule_dict[splited[0]] = splited[-1]

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

    send_request(data, token, post=create, delete=delete, get=get)


if __name__ == "__main__":
    client()
