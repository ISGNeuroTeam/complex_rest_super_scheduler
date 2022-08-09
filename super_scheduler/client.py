import argparse
import json
import requests
import sys
import logging
from typing import Union, Optional, Tuple
from rest_framework import serializers

import pydantic
from pydantic import Field
from pydantic import validator, root_validator, BaseModel

from settings import COMPLEX_REST_HOST, COMPLEX_REST_PORT, USERNAME, PASSWORD, AUTH_URL, SUPER_SCHEDULER_URL


logger = logging.getLogger("super_scheduler")


class SuperScheduler:
    AUTH_URL = AUTH_URL
    SUPER_SCHEDULER_URL = SUPER_SCHEDULER_URL
    COMPLEX_REST_HOST = COMPLEX_REST_HOST
    COMPLEX_REST_PORT = COMPLEX_REST_PORT
    USERNAME = USERNAME
    PASSWORD = PASSWORD

    logger = logger
    split_chr = ','

    # SCHEDULE_TASK = 'super_scheduler.tasks.otl_makejob'

    def __init__(self):
        self.token = None
        self.data = None

    @property
    def address(self) -> str:
        return self.COMPLEX_REST_HOST + ':' + self.COMPLEX_REST_PORT

    @property
    def header(self) -> Optional[dict]:
        return {"Authorization": f"Bearer {self.token}", 'Content-Type': 'application/json'}

    @classmethod
    def pretty_print(cls, data_str2dict: Optional[str] = None,
                     data_dict2dict: Optional[dict] = None):
        if data_str2dict:
            data_dict2dict = json.loads(data_str2dict)
        if data_dict2dict:
            print(json.dumps(data_dict2dict, indent=4))

    def send_request(self, data: dict, url: str, post: bool = False, delete: bool = False, get: bool = False) -> \
            Tuple[requests.models.Response, int]:
        """
        Send request to url with data.

        :param data:
        :param url:
        :param post:
        :param delete:
        :param get:
        :return:
        """
        data = json.dumps(data)
        if post:
            content = requests.post(url, data=data, headers=self.header)
        elif delete:
            content = requests.delete(url, data=data, headers=self.header)
        elif get:
            content = requests.get(url, data=data, headers=self.header)
        else:
            content = None

        return content, content.status_code

    def auth(self) -> str:

        self.data = {
            'login': self.USERNAME,
            'password': self.PASSWORD
        }
        url = f'http://{self.address}/{self.AUTH_URL}'
        content, status_code = self.send_request(url=url, data=self.data, post=True)

        if status_code == 200:
            token = content.json()['token']
            self.token = token
            return token

        self.logger.debug(f"Can't get token; {status_code}, {content.text}")
        raise ValueError("Can't get token")

    def new_data_construction(self,
                              task_args: dict, schedule_args: dict,
                              required_one_off_schedules: Optional[list[str]] = None,):
        if schedule_args.get('name') and schedule_args['name'] in required_one_off_schedules:
            task_args['one_off'] = True
        data = {
            'task': task_args,
            'schedule': schedule_args,
        }
        self.data = data
        return data

    def send_request_to_super_scheduler(self, post: bool = False, delete: bool = False, get: bool = False):
        url = f'http://{self.address}/{self.SUPER_SCHEDULER_URL}'
        content, status_code = self.send_request(url=url, data=self.data, post=post, delete=delete, get=get)

        if content is not None:
            self.logger.info(f"Finish request with code {content.status_code}.")
            print("\nResult:")
            if isinstance(content.text, str):
                self.pretty_print(data_str2dict=content.text)
            else:
                print(content.text)
            return content.status_code

        else:
            raise ValueError("Finish request without content")


class ConfigFormat(BaseModel):
    # config
    username: str = Field(
        default=USERNAME,
        description="username for login in django admin panel",
        example="--username test_user_1"
    )
    password: str = Field(
        default=PASSWORD,
        description="password for login in django admin panel",
        example="--password 12345678"
    )
    host: str = Field(
        default=COMPLEX_REST_HOST,
        description="host complex_rest",
        example="--host 192.168.0.1"
    )
    port: str = Field(
        default=COMPLEX_REST_PORT,
        description="port complex_rest",
        example="--port 8080"
    )

    @validator('username', 'password', 'host', 'port', pre=True)
    def field_str_validator(cls, value, field):
        field: pydantic.fields.ModelField
        field_name = field.name
        field_type = field.type_
        if isinstance(value, (list, tuple)):
            if len(value) != 1:
                raise ValueError(f"Set only one '{field_name}' argument: '--{field_name} \"smth...\"'")
            value = field_type(value[0])
        return value


class ActionFormat(BaseModel):
    # action
    create: bool = Field(
        description="flag for creating task",
        example="--create"
    )
    delete: bool = Field(
        description="flag for deleting task",
        example="--delete"
    )
    get: bool = Field(
        description="flag for getting task",
        example="--get"
    )

    @root_validator(pre=True)
    def action_validator(cls, values):
        keys = ['create', 'delete', 'get']
        for key in keys:
            values[key] = True if key in values else False
        if sum([values.get(key) for key in keys]) != 1:
            raise ValueError("Set only one flag '--create', '--delete' or '--get'")

        return values


class TaskGetFormat(BaseModel):
    pass


class TaskDeleteFormat(BaseModel):

    # task
    name: str = Field(
        description="periodic task name",
        example="--name my_first_task"
    )

    @validator('name', pre=True)
    def name_validator(cls, value):
        if isinstance(value, (list, tuple)):
            if len(value) != 1:
                raise ValueError(f"Set only one 'name' argument: '--name \"testname\"'")
            value = str(value[0])
        return value


class TaskCreateFormat(TaskDeleteFormat):

    # task
    task: str = Field(
        description="function name",
        example="--task super_scheduler.tasks.otlmakejob"
    )
    args: list = Field(
        default=[],
        description="args for periodic task",
        example="--args \"| otstats index=test\" \"| makeresults\""
    )
    kwargs: dict = Field(
        default={},
        description="kwargs for periodic task, use rarely",
        example="--kwargs \"key1=value1\" \"key2=value2\""
    )
    priority: Optional[int] = Field(
        default=None,
        description="periodic task priority, min priority - 0, max priority - 255",
        example="--priority 10"
    )
    one_off: bool = Field(
        default=False,
        description="flag, run task only ones; always use with 'clocked' schedule",
        example="--one_off"
    )
    disable: bool = Field(
        default=False,
        description="flag, disable task and do not run on schedule",
        example="--disable"
    )
    start_time: Optional[str] = Field(
        default=None,
        description="datetime when the schedule should begin triggering the task to run",
        example="--start_time \"2023-11-28 01:01:01\""
    )
    expires: Optional[str] = Field(
        default=None,
        description="datetime after which the schedule will no longer trigger the task to run",
        example="--expires \"2025-11-28 12:10:50.001\""
    )

    @validator('task', 'priority', 'start_time', 'expires', pre=True)
    def fields_validator(cls, value, field):
        field: pydantic.fields.ModelField
        field_name = field.name
        field_type = field.type_
        if isinstance(value, (list, tuple)):
            if len(value) != 1:
                raise ValueError(f"Set only one '{field_name}' argument: '--{field_name} \"smth...\"'")
            value = field_type(value[0])
        return value

    @validator('kwargs', pre=True)
    def kwargs_validator(cls, value):
        kwargs = {}
        for arg in value:
            tmp_arg_list = arg.split('=')
            key, value = tmp_arg_list[0], tmp_arg_list[-1]
            kwargs[key] = value
        return kwargs

    @validator('one_off', 'disable', pre=True)
    def flag_validator(cls, value, field):
        field: pydantic.fields.ModelField
        field_name = field.name
        if isinstance(value, (list, tuple)):
            if len(value) != 0:
                raise ValueError(f"Set only '{field_name}' flag: '--{field_name}'")
            value = True
        return value


class ScheduleFormat(BaseModel):
    # action
    crontab: bool = Field(
        description="flag for crontab schedule",
        example="--crontab"
    )
    clocked: bool = Field(
        description="flag for clocked schedule",
        example="--clocked"
    )
    interval: bool = Field(
        description="flag for interval schedule",
        example="--interval"
    )
    solar: bool = Field(
        description="flag for solar schedule",
        example="--solar"
    )

    @root_validator(pre=True)
    def schedule_validator(cls, values):
        keys = ['crontab', 'clocked', 'interval', 'solar']
        for key in keys:
            values[key] = True if key in values else False
        if sum([values.get(key) for key in keys]) != 1:
            raise ValueError("Set only one flag '--crontab', '--clocked', '--interval' or '--solar'")

        return values


class CrontabScheduleFormat(BaseModel):

    # schedule
    minute: str = Field(
        default="*",
        description="minute",
        example="--minute 50"
    )
    hour: str = Field(
        default="*",
        description="hour",
        example="--hour 10"
    )
    day_of_week: str = Field(
        default="*",
        description="day of week",
        example="--day_of_week mon,wed"
    )
    day_of_month: str = Field(
        default="*",
        description="day of month",
        example="--day_of_month 17,20"
    )
    month_of_year: str = Field(
        default="*",
        description="month of year",
        example="--month_of_year 1,3"
    )
    crontab_line: Optional[str] = Field(
        default=None,
        description="crontab line",
        example="--crontab_line \"32 18 mon,wed 17,21,29 *\""
    )

    @validator('minute', 'hour', 'day_of_week', 'day_of_month', 'month_of_year', 'crontab_line', pre=True)
    def time_range_validator(cls, value, field):
        field: pydantic.fields.ModelField
        field_name = field.name
        field_type = field.type_
        if isinstance(value, (list, tuple)):
            if len(value) != 1:
                raise ValueError(f"Set only one '{field_name}' argument: '--{field_name} \"smth...\"'")
            value = field_type(value[0])
        return value

    @root_validator()
    def transform_crontab_line(cls, values):
        if not values.get('crontab_line'):
            return values
        crontab_line = values['crontab_line']
        crontab_line = crontab_line.split(' ')
        if len(crontab_line) != 5:
            raise ValueError(f"Enter 5 params in crontab line. Got {crontab_line} "
                             "Example: '32 18 mon,wed 17,21,29 * *', '10 * * * *'")
        schedule_time_params = ('minute', 'hour', 'day_of_week', 'day_of_month', 'month_of_year')
        for param, value in zip(schedule_time_params, crontab_line):
            values[param] = value
        return values


class ClockedScheduleFormat(BaseModel):

    # schedule
    clocked_time: str = Field(
        description="datetime string",
        example="--clocked_time \"2023-11-28 01:01:01\""
    )

    @validator('clocked_time', pre=True)
    def time_range_validator(cls, value, field):
        field: pydantic.fields.ModelField
        field_name = field.name
        field_type = field.type_
        if isinstance(value, (list, tuple)):
            if len(value) != 1:
                raise ValueError(f"Set only one '{field_name}' argument: '--{field_name} \"smth...\"'")
            value = field_type(value[0])
        return value


class IntervalScheduleFormat(BaseModel):

    # schedule
    every: int = Field(
        description="run every N * time range",
        example="--every 10"
    )
    period: str = Field(
        description="time range",
        example="--period minutes"
    )

    @validator('every', 'period', pre=True)
    def time_range_validator(cls, value, field):
        field: pydantic.fields.ModelField
        field_name = field.name
        field_type = field.type_
        if isinstance(value, (list, tuple)):
            if len(value) != 1:
                raise ValueError(f"Set only one '{field_name}' argument: '--{field_name} \"smth...\"'")
            value = field_type(value[0])
        return value


class SolarScheduleFormat(BaseModel):

    # schedule
    event: str = Field(
        description="solar events; available: 'dawn_astronomical', 'dawn_nautical', 'dawn_civil', 'sunrise', "
                    "'solar_noon', 'sunset', 'dusk_civil', 'dusk_nautical', 'dusk_astronomical'; "
                    "for more info: https://docs.celeryq.dev/en/stable/userguide/periodic-tasks.html#solar-schedules",
        example="--event dawn_astronomical"
    )
    latitude: float = Field(
        description="current latitude; value must be between -180 and 180",
        example="--latitude 55.6"
    )
    longitude: float = Field(
        description="current longitude; value must be between -180 and 180",
        example="--longitude 150.01"
    )

    @validator('event', 'latitude', 'longitude', pre=True)
    def time_range_validator(cls, value, field):
        field: pydantic.fields.ModelField
        field_name = field.name
        field_type = field.type_
        if isinstance(value, (list, tuple)):
            if len(value) != 1:
                raise ValueError(f"Set only one '{field_name}' argument: '--{field_name} \"smth...\"'")
            value = field_type(value[0])
        return value


class ArgParser:

    HELP_FLAGS: set = {'-h', '--help'}
    ARG_PARSER_FORMATS = {
        'config': ConfigFormat,
        'action': ActionFormat,
        'task (create)': TaskCreateFormat,
        'task (delete)': TaskDeleteFormat,
        'task (get)': TaskGetFormat,
        'schedule': ScheduleFormat,
        'schedule (crontab)': CrontabScheduleFormat,
        'schedule (clocked)': ClockedScheduleFormat,
        'schedule (interval)': IntervalScheduleFormat,
        'schedule (solar)': SolarScheduleFormat,
    }

    def __init__(self):
        self.args = sys.argv[1:]
        self.args_set = set(self.args)

    def check_help_flag(self) -> bool:
        return any(self.HELP_FLAGS.intersection(self.args_set))

    def group_args(self) -> dict:

        result = {}
        key_arg = None

        for arg in self.args:
            if arg[:2] == '--':
                key_arg = arg[2:]
                result[key_arg] = []
            elif key_arg is not None:
                result[key_arg] += [arg]

        return result

    def _filter_none_task_args(self, task_args: dict):
        keys = list(task_args.keys())
        for key in keys:
            if task_args[key] is None:
                del task_args[key]
        return task_args

    def parse(self) -> Tuple[dict, dict, dict, dict]:
        if self.check_help_flag():
            DocGenerator.generate()
            exit(0)

        group_args = self.group_args()

        config_args = self.ARG_PARSER_FORMATS['config'](**group_args).dict()
        # print(dict(config_args))

        action_args = self.ARG_PARSER_FORMATS['action'](**group_args).dict()
        # print(action_args)

        task_args = {}
        for key, key_format in zip(('create', 'delete', 'get'), ('task (create)', 'task (delete)', 'task (get)')):
            if action_args[key]:
                task_args = self.ARG_PARSER_FORMATS[key_format](**group_args).dict()
                break
        self._filter_none_task_args(task_args)
        # print(task_args)

        schedule_args = {}
        if action_args['create']:
            schedule_types = self.ARG_PARSER_FORMATS['schedule'](**group_args).dict()
            # print(schedule_types)

            schedule_type = [key for key, value in schedule_types.items() if value is True][0]
            # print(schedule_type)

            schedule_args = self.ARG_PARSER_FORMATS[f'schedule ({schedule_type})'](**group_args).dict()
            schedule_args['name'] = schedule_type  # for recognition schedule in super_scheduler format validator
            # print(schedule_args)

        return config_args, action_args, task_args, schedule_args


class DocGenerator:

    # ArgParser.ARG_PARSER_FORMATS
    SHIFT_HEADER = "  "
    SHIFT_DOC = "      "

    @classmethod
    def _generate_header(cls, field):
        return cls.SHIFT_HEADER + f"--{field}:\n"

    @classmethod
    def _generate_description(cls, text):
        return cls.SHIFT_DOC + f"Description: {text}\n"

    @classmethod
    def _generate_required(cls, required: bool):
        return cls.SHIFT_DOC + f"Required: {required}\n"

    @classmethod
    def _generate_default(cls, text):
        if text is None:
            return cls.SHIFT_DOC + f"No default value\n"
        return cls.SHIFT_DOC + f"Default: {text}\n"

    @classmethod
    def _generate_example(cls, text):
        if text is None:
            return ""
        return cls.SHIFT_DOC + f"Example: {text}\n"

    @classmethod
    def generate(cls):
        for key, parser in ArgParser.ARG_PARSER_FORMATS.items():
            parser: pydantic.main.ModelMetaclass
            print(f"Available args and flags for {key} parser:\n")
            parser_fields = parser.__fields__
            for field, value in parser_fields.items():
                value: pydantic.fields.ModelField

                doc_string = cls._generate_header(field) + \
                             cls._generate_description(value.field_info.description) + \
                             cls._generate_required(value.required) + \
                             cls._generate_default(value.default) + \
                             cls._generate_example(value.field_info.extra.get('example', None))

                print(doc_string)


def client():
    config_args, action_args, task_args, schedule_args = ArgParser().parse()
    logger.debug("Parsed args")

    print("\nConfig args:")
    SuperScheduler.pretty_print(data_dict2dict=config_args)

    print("\nAction args:")
    SuperScheduler.pretty_print(data_dict2dict=action_args)


    SuperScheduler.USERNAME, SuperScheduler.PASSWORD, \
    SuperScheduler.COMPLEX_REST_HOST, SuperScheduler.COMPLEX_REST_PORT = \
        config_args['username'], config_args['password'], \
        config_args['host'], config_args['port']

    SuperSchedulerClass = SuperScheduler()
    SuperSchedulerClass.auth()

    data = SuperSchedulerClass.new_data_construction(task_args, schedule_args, ['clocked'])

    print("\nRequest data:")
    SuperScheduler.pretty_print(data_dict2dict=data)

    SuperSchedulerClass.send_request_to_super_scheduler(post=action_args['create'], delete=action_args['delete'], get=action_args['get'])


if __name__ == "__main__":
    client()

