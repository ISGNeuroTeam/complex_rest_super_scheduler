from rest_framework.request import Request
from typing import Union, Tuple, Optional
import super_logger
import uuid

from rest.permissions import IsAuthenticated
from rest.response import Response, status
from rest.views import APIView

from plugins.super_scheduler.utils.task.get_task import get_all_task_names, get_all_periodic_task_names
from plugins.super_scheduler.utils.task.add_task import AddPeriodicTask
from plugins.super_scheduler.utils.task.del_task import DelPeriodicTask
from plugins.super_scheduler.utils.schedule.add_schedule import AddSchedule


class TaskView(APIView):

    permission_classes = (IsAuthenticated,)
    http_method_names = ['post', 'delete', 'get']
    handler_id = str(uuid.uuid4())
    logger = super_logger.getLogger('super_scheduler')

    @staticmethod
    def _validate_request_format(request_dict: dict, necessary_params: Union[tuple, list, set]) -> \
            Tuple[bool, Optional[str]]:
        """
        Validate request format, check first-level keys.

        :param request_dict: request params
        :param necessary_params: necessary params in first-level keys
        :return: bool & optional error msg
        """
        for param in necessary_params:
            if param not in request_dict:
                msg_error = "Not valid format; " \
                            "waited: {}".format({param_: {} for param_ in necessary_params}) + \
                            "got: {}".format(request_dict)
                return False, msg_error
        return True, None

    def post(self, request: Request) -> Response:

        req_params = dict(request.data)

        # validate format
        status_format, msg_error = self._validate_request_format(req_params, ('task', 'schedule'))
        if status_format is False:
            return Response(data=msg_error, status=status.HTTP_400_BAD_REQUEST)

        # create schedule
        schedule, msg_error = AddSchedule.create(req_params['schedule'])
        if schedule is None:
            return Response(data=msg_error, status=status.HTTP_400_BAD_REQUEST)

        # create task
        status_task, msg_error = AddPeriodicTask.create(schedule=schedule, task_kwargs=req_params['task'])
        if status_task is False:
            return Response(data=msg_error, status=status.HTTP_400_BAD_REQUEST)

        self.logger.info("Success add periodic task.")
        data = {'status': 'success'}
        return Response(data=data, status=status.HTTP_201_CREATED)

    def delete(self, request: Request) -> Response:
        """
        request example: {'task': {'name': 'taskname', ...}, ...}
        """

        req_params = dict(request.data)

        # validate format
        status_format, msg_error = self._validate_request_format(req_params, ('task',))
        if status_format is False:
            return Response(data=msg_error, status=status.HTTP_400_BAD_REQUEST)

        # delete task
        status_task, msg_error = DelPeriodicTask.delete(req_params['task'])
        if status_task is False:
            return Response(data=msg_error, status=status.HTTP_400_BAD_REQUEST)

        self.logger.info("Success delete periodic task.")
        data = {'status': 'success'}
        return Response(data=data, status=status.HTTP_200_OK)

    def get(self, request: Request) -> Response:

        self.logger.info("Success get periodic tasks.")
        data = {
            'tasks': get_all_task_names(),
            'periodic_tasks': get_all_periodic_task_names(),
        }
        return Response(data=data, status=status.HTTP_200_OK)
