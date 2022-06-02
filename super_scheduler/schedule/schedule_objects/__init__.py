from .interval import IntervalDjangoSchedule, IntervalFormat
from .crontab import CrontabDjangoSchedule, CrontabFormat
from .solar import SolarDjangoSchedule, SolarFormat
from .сlocked import ClockedDjangoSchedule, ClockedFormat


SCHEDULES = {
    'interval': (IntervalDjangoSchedule, IntervalFormat),
    'crontab': (CrontabDjangoSchedule, CrontabFormat),
    'solar': (SolarDjangoSchedule, SolarFormat),
    'clocked': (ClockedDjangoSchedule, ClockedFormat),
}


def schedule_name2class(name: str):
    """
    Schedule type to schedule class.
    """
    return SCHEDULES[name][0]


def schedule_name2format(name: str):
    """
    Schedule type to schedule format.
    """
    return SCHEDULES[name][1]
