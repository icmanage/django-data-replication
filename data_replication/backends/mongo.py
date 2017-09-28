# -*- coding: utf-8 -*-
"""mongo: Django data_replication"""

from __future__ import unicode_literals
from __future__ import print_function

import logging
from urllib import quote_plus
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure

from base import BaseReplicationCollector
from ..conf import settings


__author__ = 'Steven Klass'
__date__ = '9/21/17 08:11'
__copyright__ = 'Copyright 2017 IC Manage. All rights reserved.'
__credits__ = ['Steven Klass', ]

log = logging.getLogger(__name__)


class MongoRequest(object):
    def __init__(self, *args, **kwargs):
        uri = []
        self.username = kwargs.get('username', settings.MONGO_USERNAME)
        if self.username:
            uri.append(quote_plus(self.username))
        self.password = kwargs.get('password', settings.MONGO_PASSWORD)
        if self.password:
            uri += [":", quote_plus(self.password)]
        self.host = kwargs.get('host', settings.MONGO_HOST)
        if len(uri):
            uri.append("@")
        uri.append(self.host)
        self.port = kwargs.get('port', settings.MONGO_PORT)
        uri += [":", self.port]
        self.database = kwargs.get('db', settings.MONGO_DB)
        uri += ["/", self.database]
        self.uri = 'mongodb://{uri}'.format(uri="".join(uri))

        self._client = None

    @property
    def client(self):
        if self._client is not None:
            return self._client

        self._client = MongoClient(self.uri)

        try:
            self._client.admin.command('ismaster')
        except ConnectionFailure:
            print("Server not available")
            raise ConnectionFailure("Server at %s is not available" % self.uri)

        return self._client

    @property
    def db(self):
        return self.client.get_database()

    def post_data(self, content, collection_name='default'):
        collection = getattr(self.db, collection_name)
        result = collection.insert_many(content)
        log.debug("Inserted %d and Mongo collection %s", len(result.inserted_ids), collection_name)

    def delete_ids(self, collection_name, object_ids):
        collection = getattr(self.db, collection_name)
        result = collection.delete_many({"pk": {"$in": object_ids}})
        log.debug("Found and removed %d items in Mongo", result.deleted_count)


class MongoReplicator(BaseReplicationCollector):
    replication_type = 1

    def delete_items(self, object_pks):
        mongo = MongoRequest()
        mongo.delete_ids(collection_name=self.model._meta.model_name, object_ids=object_pks)

    @property
    def task_name(self):
        from data_replication.tasks import push_mongo_objects
        return push_mongo_objects

    def get_task_kwargs(self):
        return {'model_name': self.model._meta.model_name}
