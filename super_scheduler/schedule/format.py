from pydantic import validator

from ..utils.kwargs_parser import BaseFormat as BaseScheduleParserFormat

from .schedule_objects import SCHEDULES


class ScheduleCreateFormat(BaseScheduleParserFormat):
    """
    Parse main required params to identify schedule format.
    """

    @validator('name', allow_reuse=True)
    def name_validator(cls, value: str) -> str:
        """
        Check duplicated names in django database.
        """
        if value not in SCHEDULES:
            raise ValueError(f"Schedule name {value} does not exist")
        return value


class ScheduleDeleteFormat(BaseScheduleParserFormat):
    """
    Schedule delete format.
    """

    @validator('name', allow_reuse=True)
    def name_validator(cls, value: str) -> str:
        """
        Check exist schedule type.
        """
        if value not in SCHEDULES:
            raise ValueError(f"Schedule name {value} does not exist")
        return value
