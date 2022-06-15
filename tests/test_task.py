import json
from rest.response import Response
from rest.test import TestCase, APIClient
from rest_auth.models import User


def get_user_token(client: APIClient):
    data = {
        "login": 'admin',
        "password": 'admin',
    }
    response = client.post('/auth/login/', data=data)
    return response.data['token']


class TestExample(TestCase):
    def setUp(self):
        """
        define instructions that will be executed before each test method
        """
        self.admin_user = User(username='admin', is_staff=True, is_active=True)
        self.admin_user.set_password('admin')
        self.admin_user.save()

        self.client = APIClient()
        self.user_token = get_user_token(self.client)
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + str(self.user_token))

    def _detele_task(self):
        response = self.client.delete(
            '/super_scheduler/v1/task/'.lower(),
            json.dumps(
                {"task": {"name": "test_logger123"}}
            ),
            content_type='application/json'
        )
        return response

    def test_create_task_clocked(self):
        response = self.client.post(
            '/super_scheduler/v1/task/'.lower(),
            json.dumps({"task": {"name": "test_logger123", "task": "super_scheduler.tasks.test_logger", "one_off": True},
                        "schedule": {"name": "clocked", "clocked_time": "2023-11-28 01:01:01"}}),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 201)

        response = self._detele_task()
        self.assertEqual(response.status_code, 200)

    def test_create_task_solar(self):
        response = self.client.post(
            '/super_scheduler/v1/task/'.lower(),
            json.dumps(
                {"task": {"name": "test_logger123", "task": "super_scheduler.tasks.test_logger"},
                 "schedule": {"name": "solar", "event": "sunset", "latitude": -37.81753, "longitude": 144.96715}}
            ),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 201)

        response = self._detele_task()
        self.assertEqual(response.status_code, 200)

    def test_create_task_crontab(self):
        response = self.client.post(
            '/super_scheduler/v1/task/'.lower(),
            json.dumps(
                {"task": {"name": "test_logger123", "task": "super_scheduler.tasks.test_logger"},
                 "schedule": {"name": "crontab", "minute": "*/1"}}
            ),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 201)

        response = self._detele_task()
        self.assertEqual(response.status_code, 200)

    def test_create_task_interval(self):
        response = self.client.post(
            '/super_scheduler/v1/task/'.lower(),
            json.dumps(
                {"task": {"name": "test_logger123", "task": "super_scheduler.tasks.test_logger"},
                 "schedule": {"name": "interval", "every": 20, "period": "seconds"}}
            ),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 201)

        response = self._detele_task()
        self.assertEqual(response.status_code, 200)

    def test_invalid_create_task_interval1(self):
        response = self.client.post(
            '/super_scheduler/v1/task/'.lower(),
            json.dumps(
                {"task": {"name": "test_logger123", "task": "super_scheduler.tasks.test_logger"},}
            ),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 400)

    def test_invalid_create_task_interval2(self):
        response = self.client.post(
            '/super_scheduler/v1/task/'.lower(),
            json.dumps(
                {"task": {"name": "test_logger123"},
                 "schedule": {"name": "interval", "every": 20, "period": "seconds"}}
            ),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 400)

    def test_invalid_create_task_interval3(self):
        response = self.client.post(
            '/super_scheduler/v1/task/'.lower(),
            json.dumps(
                {"task": {"task": "super_scheduler.tasks.test_logger"},
                 "schedule": {"name": "interval", "every": 20, "period": "seconds"}}
            ),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 400)

    def test_invalid_create_task_interval4(self):
        response = self.client.post(
            '/super_scheduler/v1/task/'.lower(),
            json.dumps(
                {"task": {"name": "test_logger123", "task": "super_scheduler.tasks.test_logger"},
                 "schedule": {"name": "interval", "every": -1, "period": "seconds"}}
            ),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 400)

    def test_invalid_create_task1(self):
        response = self.client.post(
            '/super_scheduler/v1/task/'.lower(),
            json.dumps(
                {"schedule": {"name": "interval", "every": 20, "period": "seconds"}}
            ),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 400)
