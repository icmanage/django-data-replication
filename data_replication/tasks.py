# -*- coding: utf-8 -*-
"""tasks.py: Django data_replication"""

from __future__ import unicode_literals
from __future__ import print_function

import logging

from pymongo.errors import ConnectionFailure, OperationFailure

from conf import settings

from celery import shared_task

from data_replication.backends.base import ImproperlyConfiguredException
from data_replication.backends.mongo import MongoRequest
from data_replication.backends.splunk import SplunkRequest

__author__ = 'Steven Klass'
__date__ = '9/26/17 10:12'
__copyright__ = 'Copyright 2017 IC Manage. All rights reserved.'
__credits__ = ['Steven Klass', ]

log = logging.getLogger(__name__)


@shared_task(ignore_result=True, store_errors_even_if_ignored=True)
def push_splunk_objects(**kwargs):

    object_ids = kwargs.get('object_ids')
    tracker_id = kwargs.get('tracker_id')
    content_type_id = kwargs.get('content_type_id')
    model_name  = kwargs.get('model_name')

    source_type = kwargs.get('source_type', 'json')
    source = kwargs.get('source', None)
    host = kwargs.get('host', None)
    dry_run = kwargs.get('dry_run', False)

    assert object_ids is not None, "You failed to include object ids"
    assert tracker_id is not None, "You failed to include tracker_id"
    assert content_type_id is not None, "You failed to include content_type_id"
    assert model_name is not None, "You failed to include model_name"

    from data_replication.models import ReplicationTracker
    tracker = ReplicationTracker.objects.get(id=tracker_id)

    Replicator = tracker.get_replicator()
    data = Replicator.add_items(object_ids)

    for item in data:
        if 'model' not in item.keys():
            item['model'] = model_name
        else:
            log.warning("Model already exists?")
        assert 'pk' in item.keys(), "Missing pk in model"

    try:
        splunk = SplunkRequest()
    except ImproperlyConfiguredException as err:
        log.error("Splunk Improperly configured - %s" % err)
        return
    splunk.post_data(content=data, source=source, sourcetype=source_type, host=host, dry_run=dry_run)

    from data_replication.models import Replication
    Replication.objects.filter(
        content_type_id=content_type_id, tracker_id=tracker_id,
        object_id__in=object_ids).update(state=1)

    return "Added %d %s models objects to splunk" % (len(data), model_name)


@shared_task(ignore_result=True, store_errors_even_if_ignored=True)
def push_mongo_objects(**kwargs):

    object_ids = kwargs.get('object_ids')
    tracker_id = kwargs.get('tracker_id')
    content_type_id = kwargs.get('content_type_id')
    model_name = kwargs.get('model_name')

    collection_name = kwargs.get('collection_name', model_name)

    assert object_ids is not None, "You failed to include object ids"
    assert tracker_id is not None, "You failed to include tracker_id"
    assert content_type_id is not None, "You failed to include content_type_id"
    assert model_name is not None, "You failed to include model_name"

    from data_replication.models import ReplicationTracker
    tracker = ReplicationTracker.objects.get(id=tracker_id)

    Replicator = tracker.get_replicator()
    data = Replicator.add_items(object_ids)

    for item in data:
        assert 'pk' in item.keys(), "Missing pk in model"

    try:
        mongo = MongoRequest()
    except ImproperlyConfiguredException as err:
        log.error("Mongo Improperly configured - %s" % err)
        return
    try:
        mongo.post_data(content=data, collection_name=collection_name)
    except (ConnectionFailure, OperationFailure) as err:
        log.error("Unable to connect to Mongo!! - %s", err)

    else:
        from data_replication.models import Replication
        Replication.objects.filter(
            content_type_id=content_type_id, tracker_id=tracker_id,
            object_id__in=object_ids).update(state=1)

        return "Added %d %s models objects to mongo" % (len(data), collection_name)

