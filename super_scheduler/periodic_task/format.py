from pydantic import validator

from ..utils.get_task import get_all_periodic_task_names, get_all_task_names
from ..utils.kwargs_parser import BaseFormat as BaseTaskParserFormat


class TaskCreateFormat(BaseTaskParserFormat):
    """
    Task create format.
    See PeriodicTask doc for additional args.
    """
    task: str
    args: list = []
    kwargs: dict = {}
    one_off: bool = False

    @validator('name')
    def name_validator(cls, value: str) -> str:
        """
        Check duplicate periodic task name in django database.
        """
        if value in get_all_periodic_task_names():
            raise ValueError(f"Duplicate periodic task name {value}")
        return value

    @validator('task')
    def task_exist(cls, value: str) -> str:
        """
        Check exist task.
        """
        if value not in get_all_task_names():
            raise ValueError(f"Task name {value} does not exist")
        return value


class TaskDeleteFormat(BaseTaskParserFormat):
    """
    Task delete format.
    """

    @validator('name', allow_reuse=True)
    def name_validator(cls, value: str) -> str:
        """
        Check exist task.
        """
        if value not in get_all_periodic_task_names():
            raise ValueError(f"Periodic task name {value} does not exist")
        return value
