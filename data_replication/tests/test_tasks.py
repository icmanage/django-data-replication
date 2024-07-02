# -*- coding: utf-8 -*-
from unittest.mock import patch

from django.apps import apps
from django.contrib.auth import get_user_model
from django.test import TestCase

from data_replication.backends.splunk import SplunkPostException
from data_replication.models import ReplicationTracker, Replication

from data_replication.tasks import push_mongo_objects
from data_replication.tasks import push_splunk_objects

from data_replication.tests.factories import replication_tracker_factory

ip_verification_app = apps.get_app_config("ip_verification")

User = get_user_model()
Example = apps.get_model("example", "Example")


class MockResponse:
    status_code = 200
    dry_run = False

    def __init__(self, **kwargs):
        self.status_code = kwargs.get("status_code", self.status_code)

    def json(self):
        return {"sid": "12345"}


class MockSession:
    def post(self, url, data=None, json=None, dry_run=False, **kwargs):
        if url == "https://localhost:8089/services/receivers/stream":
            return MockResponse(status_code=204)
        elif url == "https://localhost:8089/services/search/jobs?output_mode=json":
            return MockResponse(status_code=200)
        elif url == "https://localhost:8089/services/auth/login?output_mode=json":
            return MockResponse(status_code=200)
        else:
            print("HANDLE ", url)

    def get(self, url, **kwargs):
        if url == "https://localhost:8089/services/search/jobs/12345/results?output_mode=json":
            return MockResponse(status_code=200)
        elif url == "https://localhost:8089/services/auth/login?output_mode=json":
            return MockResponse(status_code=205)
        else:
            print("HANDLE ", url)

    def request(
        self,
        method,
        url,
        params=None,
        data=None,
        headers=None,
        cookies=None,
        files=None,
        auth=None,
        timeout=None,
        allow_redirects=True,
        proxies=None,
        hooks=None,
        stream=None,
        verify=None,
        cert=None,
        json=None,
    ):
        if url == "{base_url}/services/search/jobs/{search_id}/results?output_mode=json":
            return MockResponse(status_code=400)


mock_session = MockSession()


class MockSession2:
    def post(self, url, data=None, json=None, **kwargs):
        if url == "https://localhost:8089/services/receivers/stream":
            return MockResponse(status_code=205)
        elif url == "https://localhost:8089/services/auth/login?output_mode=json":
            return MockResponse(status_code=69)

    def get(self, url, **kwargs):
        if url == "https://localhost:8089/services/search/jobs/12345/results?output_mode=json":
            return MockResponse(status_code=200)
        elif url == "https://localhost:8089/services/auth/login?output_mode=json":
            return MockResponse(status_code=205)
        else:
            print("HANDLE ", url)

    def request(
        self,
        method,
        url,
        params=None,
        data=None,
        headers=None,
        cookies=None,
        files=None,
        auth=None,
        timeout=None,
        allow_redirects=True,
        proxies=None,
        hooks=None,
        stream=None,
        verify=None,
        cert=None,
        json=None,
    ):
        if url == "{base_url}/services/search/jobs/{search_id}/results?output_mode=json":
            return MockResponse(status_code=420)


mock_session_fail = MockSession2()


class TestSplunkTasks(TestCase):
    @patch("data_replication.backends.splunk.SplunkRequest.session", mock_session)
    def test_push_splunk_objects(self, **kwargs):
        object_ids = []
        for i in range(3):
            example = Example.objects.create(name="User" + str(i))
            object_ids.append(example.id)

        rt = replication_tracker_factory(model=Example, replication_type=2)
        self.assertEqual(ReplicationTracker.objects.count(), 1)
        self.assertEqual(Replication.objects.count(), 0)

        push_splunk_objects(
            tracker_id=rt.id,
            object_ids=object_ids,
            content_type_id=rt.content_type_id,
            model_name="Example",
            replication_class_name="TestSplunkReplicatorExample",
        )
        self.assertEqual(Replication.objects.count(), 3)
        self.assertEqual(Replication.objects.filter(state=1).count(), 3)

    @patch("data_replication.backends.splunk.SplunkRequest.session", mock_session_fail)
    def test_push_splunk_objects_fail(self, **kwargs):
        with self.assertRaises(SplunkPostException):
            object_ids = []
            rt = replication_tracker_factory(model=Example, replication_type=2)
            self.assertEqual(Replication.objects.count(), 0)

            push_splunk_objects(
                tracker_id=rt.id,
                object_ids=object_ids,
                content_type_id=rt.content_type_id,
                model_name="Example",
                replication_class_name="TestSplunkReplicatorExample",
            )
        self.assertEqual(Replication.objects.count(), 0)


class MockMongoClient(dict):
    def __init__(self, *args, **kwargs):
        _client = None
        pass

    class admin:
        def command(self, *args, **kwargs):
            return True

    def get_database(self, *args, **kwargs):
        class collection:
            collection_name = "test collection"

            def insert_many(self, objects, *args, **kwargs):
                class ReturnObj:
                    inserted_ids = [x["pk"] for x in objects]

                return ReturnObj()

        class db:
            Example = collection()
            pass

        return db


client = MockMongoClient()


class TestMongoTasks(TestCase):
    @patch("data_replication.backends.mongo.MongoRequest._client", client)
    def test_push_mongo_objects(self):
        object_ids = []
        for i in range(3):
            example = Example.objects.create(name="User" + str(i))
            object_ids.append(example.id)
        rt = replication_tracker_factory(model=Example, replication_type=1)
        self.assertEqual(ReplicationTracker.objects.count(), 1)
        self.assertEqual(Replication.objects.count(), 0)

        push_mongo_objects(
            tracker_id=rt.id,
            object_ids=object_ids,
            content_type_id=rt.content_type_id,
            model_name="Example",
            replication_class_name="TestMongoReplicatorExample",
        )
        self.assertEqual(Replication.objects.count(), 3)
        self.assertEqual(Replication.objects.filter(state=1).count(), 3)
