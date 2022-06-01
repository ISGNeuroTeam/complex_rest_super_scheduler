import json
from rest.test import TestCase, APIClient


class TestExample(TestCase):
    def setUp(self):
        """
        define instructions that will be executed before each test method
        """
        pass

    def _detele_task(self):
        client = APIClient()
        response = client.delete(
            '/super_scheduler/v1/task/'.lower(),
            json.dumps(
                {"task": {"name": "test_logger123"}}
            ),
            content_type='application/json'
        )
        return response

    def test_create_task_clocked(self):
        client = APIClient()
        response = client.post(
            '/super_scheduler/v1/task/'.lower(),
            json.dumps({"task": {"name": "test_logger123", "task": "super_scheduler.tasks.test_logger", "one_off": True},
                        "schedule": {"name": "clocked", "clocked_time": "2023-11-28 01:01:01"}}),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 201)

        response = self._detele_task()
        self.assertEqual(response.status_code, 200)

    def test_create_task_solar(self):
        client = APIClient()
        response = client.post(
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
        client = APIClient()
        response = client.post(
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
        client = APIClient()
        response = client.post(
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
