from rest_framework.request import Request
from typing import Union, Optional
import super_logger, logging
import uuid

from rest.permissions import IsAuthenticated
from rest.response import Response, status
from rest.views import APIView

from ..utils.get_task import get_all_task_names, get_all_periodic_task_names, get_all_periodic_task_full
from ..periodic_task.periodic_task import PeriodicTask
from ..schedule.schedule import Schedule


class TaskView(APIView):

    permission_classes = (IsAuthenticated,)
    http_method_names = ['post', 'delete', 'get']
    handler_id = str(uuid.uuid4())
    logger = logging.getLogger('super_scheduler')

    @staticmethod
    def _validate_request_format(request_dict: dict, necessary_params: Union[tuple, list, set]) -> Optional[str]:
        """
        Validate request format, check first-level keys.

        :param request_dict: request params
        :param necessary_params: necessary params in first-level keys
        :return: optional error msg
        """
        for param in necessary_params:
            if param not in request_dict:
                msg_error = "Not valid format; " \
                            "expected: {}".format({param_: {} for param_ in necessary_params}) + \
                            "got: {}".format(request_dict)
                return msg_error
        return None

    def post(self, request: Request) -> Response:

        req_params = dict(request.data)
        self.logger.info(f"Got post request data: {request.data}")

        # validate format
        msg_error = self._validate_request_format(req_params, ('task', 'schedule'))
        if msg_error:
            return Response(data=msg_error, status=status.HTTP_400_BAD_REQUEST)

        # create schedule
        schedule, msg_error = Schedule.get_or_create(req_params['schedule'])
        if schedule is None:
            return Response(data=msg_error, status=status.HTTP_400_BAD_REQUEST)

        # create task
        msg_error = PeriodicTask.get_or_create(schedule=schedule, task_kwargs=req_params['task'])
        if msg_error:
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
        msg_error = self._validate_request_format(req_params, ('task',))
        if msg_error:
            return Response(data=msg_error, status=status.HTTP_400_BAD_REQUEST)

        # delete task
        msg_error = PeriodicTask.delete(req_params['task'])
        if msg_error:
            return Response(data=msg_error, status=status.HTTP_400_BAD_REQUEST)

        self.logger.info("Success delete periodic task.")
        data = {'status': 'success'}
        return Response(data=data, status=status.HTTP_200_OK)

    def get(self, request: Request) -> Response:

        data = {
            'tasks': get_all_task_names(),
            'periodic_tasks': get_all_periodic_task_full(),
        }
        self.logger.info(f"Data: {data}")
        self.logger.info("Success get periodic tasks.")
        return Response(data=data, status=status.HTTP_200_OK)
