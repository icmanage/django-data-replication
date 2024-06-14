from django import test
from mock import patch

from data_replication.tests.test_tasks import MockMongoClient


class MongoTestCase(test.TestCase):

    @patch('data_replication.backends.mongo.MongoRequest._client', MockMongoClient)
    def test_client(self):
        pass

    def test_get_task_kwargs(self):
        pass
