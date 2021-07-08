# -*- coding: utf-8 -*-
"""mongo: Django data_replication"""

import logging
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure

from .base import BaseReplicationCollector, ImproperlyConfiguredException
from ..apps import DataMigrationConf


__author__ = 'Steven Klass'
__date__ = '9/21/17 08:11'
__copyright__ = 'Copyright 2017 IC Manage. All rights reserved.'
__credits__ = ['Steven Klass', ]

log = logging.getLogger(__name__)


class MongoRequest(object):
    def __init__(self, *args, **kwargs):

        settings = DataMigrationConf()

        try:
            self.uri = kwargs.get('connection_uri', settings.MONGO_CONNECTION_URI)
        except AttributeError:
            raise ImproperlyConfiguredException("Missing Mongo settings.MONGO_CONNECTION_URI")

        # This is explicitly called out as I could not get this to work with using a replicaSet
        try:
            self.database_name = kwargs.get('database_name', settings.MONGO_DB_NAME)
        except AttributeError:
            self.database_name = None
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
        if self.database_name:
            return self.client[self.database_name]
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

    @property
    def collection_name(self):
        return self.model._meta.model_name

    def delete_items(self, object_pks):
        mongo = MongoRequest()
        mongo.delete_ids(collection_name=self.collection_name, object_ids=object_pks)

    @property
    def task_name(self):
        from data_replication.tasks import push_mongo_objects
        return push_mongo_objects

    def get_task_kwargs(self):
        return {'model_name': self.model._meta.model_name, 'collection_name': self.collection_name,
                'replication_class_name': self.__class__.__name__}
