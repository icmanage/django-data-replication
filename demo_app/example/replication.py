from django.forms import model_to_dict

from data_replication.backends.mongo import MongoReplicator
from data_replication.backends.splunk import SplunkReplicator
from .models import Example


class ExampleMixin():
    def add_items(self, object_ids):
        data = []
        for object_id in object_ids:
            item = Example(id=object_id)
            pt = model_to_dict(item)
            pt['pk'] = pt.pop('id')
            data.append(pt)
        return data

    def _get_replication_object(self, replication_type):
        ctype = ContentType.objects.get_for_model(self.__class__)
        try:
            obj = Replication.objects.get(content_type__pk=ctype.id, object_id=self.id, replicaion_type=replication_type)
        except Replication.DoesNotExist:
            return None
        return obj

class TestMongoReplicatorExample(ExampleMixin, MongoReplicator):
    model = Example
    change_keys = ['last_used']


class TestSplunkReplicatorExample(ExampleMixin, SplunkReplicator):
    model = Example
    change_keys = ['last_used']

