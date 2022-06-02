from .get_schedule import get_all_schedules, get_all_schedules_subclasses, filter_unused_schedules_in_tasks


def del_unused_schedules():
    """
    Delete unused schedules.
    """
    all_schedule_classes = list(get_all_schedules())
    all_schedule_subclasses = list(get_all_schedules_subclasses(all_schedule_classes))
    schedule_dict = {str(subclass_): class_
                     for class_, subclass_ in zip(all_schedule_classes, all_schedule_subclasses)}

    # delete used schedules from dict
    schedule_dict = filter_unused_schedules_in_tasks(schedule_dict)

    # delete unused schedules
    for key, val in schedule_dict.items():
        val.delete()
