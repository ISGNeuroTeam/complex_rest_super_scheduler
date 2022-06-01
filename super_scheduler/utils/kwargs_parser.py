from typing import Tuple, Optional

from pydantic import BaseModel, validator

from plugins.super_scheduler.utils.validate_format import validate_format


class BaseFormat(BaseModel):
    """
    See PeriodicTask doc for additional args
    """
    name: str

    @validator('name')
    def name_validator(cls, value: str) -> str:
        raise NotImplementedError


class KwargsParser:

    @classmethod
    def parse_kwargs(cls, kwargs: dict, kwargs_format) -> Tuple[Optional[dict], Optional[str]]:
        """
        Parse kwargs.

        :param kwargs: task kwargs
        :param kwargs_format: pydantic kwargs format
        :return: parsed kwargs & None | None & msg error
        """
        try:
            kwargs = validate_format(kwargs, kwargs_format)
            return kwargs.dict(), None
        except Exception as err:
            return None, str(err)
