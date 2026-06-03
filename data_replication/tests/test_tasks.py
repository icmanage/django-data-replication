# -*- coding: utf-8 -*-
from __future__ import unicode_literals

__copyright__ = 'Copyright 2011-2026 IC Manage. All rights reserved.'

"""Tests for data_replication.tasks (the Celery push tasks).

On this branch the tasks only push the data and flip already-tracked
Replication rows to state=1 (state=In Storage); they do not create the rows
(base._add_items does that before dispatch)."""

import datetime

import mock
from django.contrib.contenttypes.models import ContentType
from django.test import TestCase
from django.utils.timezone import now

from data_replication.models import Replication, ReplicationTracker
from data_replication.tasks import push_mongo_objects, push_splunk_objects
from example.models import Example


def _setup(replication_type):
    ex = Example.objects.create(name='a', last_updated=now())
    ct = ContentType.objects.get_for_model(Example)
    tracker = ReplicationTracker.objects.create(
        content_type=ct, replication_type=replication_type,
        last_updated=now() - datetime.timedelta(days=3650), state=1)
    Replication.objects.create(
        tracker=tracker, content_type=ct, object_id=ex.pk, state=0, last_updated=now())
    return ex, ct, tracker


class PushSplunkObjectsTests(TestCase):
    @mock.patch('data_replication.tasks.SplunkRequest')
    def test_pushes_payload_and_marks_in_storage(self, MockSplunk):
        ex, ct, tracker = _setup(2)
        push_splunk_objects(
            object_ids=[ex.pk], tracker_id=tracker.id, content_type_id=ct.id,
            model_name='example', replication_class_name='ExampleSplunkReplicator')

        self.assertTrue(MockSplunk.return_value.post_data.called)
        content = MockSplunk.return_value.post_data.call_args[1]['content']
        self.assertEqual(content[0]['pk'], ex.pk)
        self.assertEqual(content[0]['model'], 'example')  # task stamps the model
        self.assertEqual(Replication.objects.get(object_id=ex.pk).state, 1)


class PushMongoObjectsTests(TestCase):
    @mock.patch('data_replication.tasks.MongoRequest')
    def test_pushes_payload_and_marks_in_storage(self, MockMongo):
        ex, ct, tracker = _setup(1)
        push_mongo_objects(
            object_ids=[ex.pk], tracker_id=tracker.id, content_type_id=ct.id,
            model_name='example', collection_name='example',
            replication_class_name='ExampleMongoReplicator')

        self.assertTrue(MockMongo.return_value.post_data.called)
        kwargs = MockMongo.return_value.post_data.call_args[1]
        self.assertEqual(kwargs['collection_name'], 'example')
        self.assertEqual(kwargs['content'][0]['pk'], ex.pk)
        self.assertEqual(Replication.objects.get(object_id=ex.pk).state, 1)

    @mock.patch('data_replication.tasks.MongoRequest')
    def test_mongo_failure_leaves_state_unchanged(self, MockMongo):
        from pymongo.errors import ConnectionFailure
        MockMongo.return_value.post_data.side_effect = ConnectionFailure('down')
        ex, ct, tracker = _setup(1)
        push_mongo_objects(
            object_ids=[ex.pk], tracker_id=tracker.id, content_type_id=ct.id,
            model_name='example', collection_name='example',
            replication_class_name='ExampleMongoReplicator')
        # connection error is swallowed; the row is NOT marked in-storage
        self.assertEqual(Replication.objects.get(object_id=ex.pk).state, 0)
