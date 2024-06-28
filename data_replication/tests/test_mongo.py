# -*- coding: utf-8 -*-
from django import test
import mock
from mock import patch
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure

from data_replication.backends.mongo import MongoRequest
from data_replication.tests.test_tasks import MockMongoClient


class MongoTestCase(test.TestCase):
    client = MockMongoClient()

    @patch("data_replication.backends.mongo.MongoRequest._client", MockMongoClient)
    def test_client(self):
        mongo_request = MongoRequest()
        mongo_request.client()

    @patch("data_replication.backends.mongo.MongoRequest._client", client)
    def test_client_not_none(self):
        mongo_request = MongoRequest()
        mongo_request._client = None
        with self.assertRaises(ConnectionFailure):
            mongo_request.client()

    @patch("data_replication.backends.mongo.MongoRequest._client", client)
    def test_db(self):
        mongo_request = MongoRequest()
        mongo_request.db()

    @mock.patch("data_replication.backends.mongo.MongoRequest._client")
    def test_delete_ids(self, mock_client):
        mock_db = mock_client.return_value
        mock_collection = mock_db["test_collection"]

        mock_collection.delete_many.return_value.deleted_count = 3
        mongo = MongoRequest()

        collection_name = "test_collection"
        object_ids = ["1", "2", "3"]

        mongo.delete_ids(collection_name=collection_name, object_ids=object_ids)

        # mock_collection.delete_many.assert_called_once_with({"pk": {"$in": object_ids}})

        remaining_count = mock_collection.count_documents({})
        # self.assertEqual(remaining_count, 0)
