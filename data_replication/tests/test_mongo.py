# -*- coding: utf-8 -*-
from __future__ import unicode_literals

__copyright__ = 'Copyright 2011-2026 IC Manage. All rights reserved.'

"""Tests for data_replication.backends.mongo (MongoRequest)."""

import mock
from django.test import TestCase

from data_replication.backends.mongo import MongoRequest


class _FakeCollection(object):
    def __init__(self):
        self.inserted = None
        self.deleted_query = None

    def insert_many(self, content):
        self.inserted = list(content)
        return mock.Mock(inserted_ids=[c['pk'] for c in self.inserted])

    def delete_many(self, query):
        self.deleted_query = query
        return mock.Mock(deleted_count=len(query['pk']['$in']))


class _FakeDB(object):
    def __init__(self, collection):
        self._collection = collection

    def __getattr__(self, name):
        return self._collection


class _FakeClient(object):
    def __init__(self, db):
        self._db = db
        self.admin = mock.Mock()

    def get_database(self):
        return self._db


def _request_with(collection):
    req = MongoRequest(connection_uri='mongodb://example')
    req._client = _FakeClient(_FakeDB(collection))  # bypass real MongoClient
    return req


class PostDataTests(TestCase):
    def test_inserts_into_named_collection(self):
        coll = _FakeCollection()
        _request_with(coll).post_data([{'pk': 1, 'name': 'a'}], collection_name='example')
        self.assertEqual(coll.inserted[0]['pk'], 1)


class DeleteIdsTests(TestCase):
    def test_builds_pk_in_query(self):
        coll = _FakeCollection()
        _request_with(coll).delete_ids('example', [1, 2, 3])
        self.assertEqual(coll.deleted_query, {'pk': {'$in': [1, 2, 3]}})
