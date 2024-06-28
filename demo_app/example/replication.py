# -*- coding: utf-8 -*-
from django.forms import model_to_dict

from data_replication.backends.mongo import MongoReplicator
from data_replication.backends.splunk import SplunkReplicator
from .models import Example, ManyExample


class ExampleMixin:
    def add_items(self, object_ids):
        data = []
        for object_id in object_ids:
            item = Example(id=object_id)
            pt = model_to_dict(item)
            pt["pk"] = pt.pop("id")
            data.append(pt)
        return data


class TestMongoReplicatorExample(ExampleMixin, MongoReplicator):
    model = Example
    change_keys = ["last_used"]


class TestSplunkReplicatorExample(ExampleMixin, SplunkReplicator):
    model = Example
    change_keys = ["last_updated"]


class TestMongoReplicatorManyExample(ExampleMixin, MongoReplicator):
    model = ManyExample
    change_keys = ["last_used"]


class TestMongoReplicatorManyExample2(ExampleMixin, MongoReplicator):
    model = ManyExample
    change_keys = ["last_used"]
