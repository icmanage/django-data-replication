import mock
from django.apps import apps
from django.contrib.auth import get_user_model
from django.contrib.contenttypes.models import ContentType
from django.test import TestCase

from data_replication.models import ReplicationTracker

from data_replication.tasks import push_mongo_objects
from data_replication.tasks import push_splunk_objects

from data_replication.tests.factories import replication_tracker_factory

ip_verification_app = apps.get_app_config('ip_verification')

User = get_user_model()
Example = apps.get_model('example', 'Example')


class MockResponse():
    status_code = 200

    def __init__(self, **kwargs):
        self.status_code = kwargs.get('status_code', self.status_code)

    def json(self):
        # TODO test here but for push mongo now
        pass


class MockSession1():
    def post(self, url, data=None, json=None, **kwargs):
        print(url)
        if url == 'https://localhost:8089/services/receivers/stream':
            return MockResponse(status_code=205)

    def post_fail(self, url, data=None, json=None):
        print(url)
        if url == 'https://localhost:8089/services/receivers/stream':
            return MockResponse(status_code=205)

    def get(self, url, **kwargs):
        pass
        print(url)


mock_session = MockSession1()


class MockSession2():

    def post_fail(self, url, data=None, json=None):
        print(url)
        if url == 'https://localhost:8089/services/receivers/stream':
            return MockResponse(status_code=205)


mock_session_fail = MockSession2()


class TestTasks(TestCase):

    @mock.patch('data_replication.backends.splunk.SplunkRequest.session', mock_session)
    def test_push_splunk_objects(self, **kwargs):
        object_ids = []
        for i in range(3):
            example = Example.objects.create(name='User' + str(i))
            object_ids.append(example.id)
        rt = replication_tracker_factory(model=Example, replication_type=2)
        self.assertEqual(ReplicationTracker.objects.count(), 1)

        push_splunk_objects(
            tracker_id=rt.id,
            object_ids=object_ids,
            content_type_id=rt.content_type_id,
            model_name='Example',
            replication_class_name='TestSplunkReplicatorExample'
        )

    @mock.patch('data_replication.backends.splunk.SplunkRequest.session', mock_session_fail)
    def test_push_splunk_objects_fail(self, **kwargs):
        self.assertEqual(MockSession2.status_code, 205)


    @mock.patch('data_replication.backends.mongo.MongoRequest.session', mock_session)
    def test_push_mongo_objects(self, **kwargs):
        object_ids = []
        for i in range(3):
            example = Example.objects.create(name='User' + str(i))
            object_ids.append(example.id)
        rt = replication_tracker_factory(model=Example, replication_type=1)
        self.assertEqual(ReplicationTracker.objects.count(), 1)

        push_mongo_objects(
            tracker_id=rt.id,
            object_ids=object_ids,
            content_type_id=rt.content_type_id,
            model_name='Example',
            replication_class_name='TestMongoReplicatorExample'
        )
