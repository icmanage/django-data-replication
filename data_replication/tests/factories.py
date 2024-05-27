import random
from collections import OrderedDict

from django.apps import apps
from django.contrib.contenttypes.models import ContentType
from django.utils.timezone import now

from data_replication import tasks
from data_replication.backends.base import BaseReplicationCollector
from data_replication.models import REPLICATION_TYPES, ReplicationTracker, Replication

TestResultLink = apps.get_model('ip_verification', 'TestResultLink')
ip_verification_app = apps.get_app_config('ip_verification')


def replication_tracker_factory(model=None, replication_type=None, **kwargs):

    ct = None
    if model:
        ct=ContentType.objects.get_for_model(TestResultLink)

    if replication_type:
        assert replication_type in [1, 2, "splunk", "mongo"]
        replication_type = 2 if replication_type == "splunk" else replication_type
        replication_type = 1 if replication_type == "1" else replication_type
    else:
        replication_type = random.choice([x[0] for x in REPLICATION_TYPES])

    data = dict(
        replication_type=replication_type,
        content_type=ct,
        state=1,
        last_updated=now()
    )

    data.update(**kwargs)
    return ReplicationTracker.objects.create(**data)


def replication_factory(tracker=None, content_object=None, **kwargs):
    if content_object is None:
        content_object = ip_verification_app.test_result_link_factory(**kwargs)

    ct = ContentType.objects.get_for_model(content_object)

    if tracker is None:
        tracker = replication_tracker_factory(
            content_type=ct
        )

    data = dict(content_type=ct, object_id=content_object.id,
                state=0, last_updated=now())
    data.update(**kwargs)
    return Replication.objects.create(**data)


def tasks_splunk_factory(object_ids=None, content_type_id=None, model_name=None, tracker_id=None, ignore_result=True,
                         store_errors_even_if_ignored=True, **kwargs):
    if ignore_result is True:
        pass
    if store_errors_even_if_ignored is True:
        pass
    if object_ids is None:
        pass
        #object_ids = test_result_link_factory(**kwargs).object_ids
    if content_type_id is None:
        pass
    if model_name is None:
        pass
    if object_ids is None:
        pass
    if tracker_id is None:
        #tracker_id = replication_tracker_factory(content_type=kwargs.get('tracker_id'))
        pass

    data = dict(state=1,
                model_name=kwargs.get('model_name'),
                content_type_id=kwargs.get('content_type_id'),
                object_ids=kwargs.get('object_ids'),
                tracker_id=kwargs.get('tracker_id'),
                replication_class_name=kwargs.get('replication_class_name'),
                source_type=kwargs.get('source_type', 'json'),
                )
    data.update(**kwargs)
    return tasks.push_splunk_objects(**data)


#these two should be nearly the same


def tasks_mongo_factory(object_ids=None, content_type_id=None, model_name=None, tracker_id=None, ignore_result=True,
                        store_errors_even_if_ignored=True, **kwargs):
    if ignore_result is True:
        pass
    if store_errors_even_if_ignored is True:
        pass
    if object_ids is None:
        pass
        #object_ids = test_result_link_factory(**kwargs).object_ids
    if content_type_id is None:
        pass
    if model_name is None:
        pass
    if object_ids is None:
        pass
    if tracker_id is None:
        #tracker_id = replication_tracker_factory(content_type=kwargs.get('tracker_id'))
        pass

    data = dict(state=1,
                model_name=kwargs.get('model_name'),
                content_type_id=kwargs.get('content_type_id'),
                object_ids=kwargs.get('object_ids'),
                tracker_id=kwargs.get('tracker_id'),
                replication_class_name=kwargs.get('replication_class_name'),
                source_type=kwargs.get('source_type', 'json'),
                )
    data.update(**kwargs)
    return tasks.push_mongo_objects(**data)


#def base_factory(reset=False, max_count=None, **kwargs)
#if reset is False:
#    pass
#if max_count is None:
#    pass

#data = dict(last_look=None, self.locked=False, query_time=None, add_pks=[], update_pks=[], delete_pks=[],
#_accounted_pks=[], _queryset_pks=[], skip_locks=True, reset=reset, output_file=None,
#max_count = max_count, use_subtasks=kwargs.get('use_subtasks', True)

#data.update(**kwargs)
#return tasks.push_mongo_objects(**data)


def base_factory(model=None, change_keys=[], field_map=OrderedDict(), search_quantifiers=None, days=365 * 100,
                      last_updated=now(), **kwargs):
    if model is None:
        pass

    data = dict(state=0, days=365 * 100,
                #tracker=self.last_look, object_id__in=object_pks, content_type=self.content_type,
                #content_type=self.content_type, tracker=self.last_look,
                #object_id=pop(0),
                last_updated=last_updated)

    data.update(**kwargs)
    return BaseReplicationCollector.objects.create(**data)
