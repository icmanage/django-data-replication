from django import test
from mock import patch

from data_replication import tasks
from data_replication.backends.mongo import MongoRequest
from data_replication.tests.test_tasks import MockMongoClient


class MongoTestCase(test.TestCase):
    client = MockMongoClient()

    @patch('data_replication.backends.mongo.MongoRequest._client', MockMongoClient)
    def test_client(self):
        mongo_request = MongoRequest()
        mongo_request.client()

    @patch('data_replication.backends.mongo.MongoRequest._client', client)
    def test_db(self):
        mongo_request = MongoRequest()
        mongo_request.db()

    # TODO fix or remove
    @patch('data_replication.backends.mongo.MongoRequest._client', client)
    def test_delete(self, **kwargs):
        mongo = MongoRequest()
        model_name = kwargs.get('model_name')
        # collection_name = kwargs.get('collection_name', model_name)
        collection_name = 'test collection'
        object_pks = ['1', '2', '3']
        mongo.delete_ids(collection_name=collection_name, object_ids=object_pks)
        collection = MongoRequest.db[collection_name]
        object_ids = ['ObjectId(), ObjectId()']
        remaining_count = collection.count_documents({"pk": {"$in": object_ids}})
        self.assertEqual(remaining_count, 0)

    def test_get_task_kwargs(self):
        pass
