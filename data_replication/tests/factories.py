import random

from celery import Task
from celery.worker.consumer import Tasks
import data
from django.apps import apps
from django.contrib.contenttypes.models import ContentType
from django.utils.timezone import now

from data_replication import tasks
from data_replication.models import REPLICATION_TYPES, ReplicationTracker, Replication

TestResultLink = apps.get_model('ip_verification', 'TestResultLink')
RegressionTagSummary = apps.get_model('ip_verification', 'RegressionTagSummary')


def replication_tracker_factory(**kwargs):
    data = dict(replication_type=random.choice([x[0] for x in REPLICATION_TYPES]),
                content_type=ContentType.objects.get_for_model(TestResultLink),
                state=1,
                last_updated=now())

    data.update(**kwargs)
    return ReplicationTracker.objects.create(**data)


def test_result_link_factory(summary=None, **kwargs):
    if summary is None:
        summary = RegressionTagSummary.objects.create()
    data = dict(summary=summary, test_result_id=random.randint(1, 1000000), last_used=now())
    data.update(**kwargs)
    return TestResultLink.objects.create(**data)


def replication_factory(tracker=None, content_object=None, **kwargs):
    if content_object is None:
        content_object = test_result_link_factory(**kwargs)

    ct = ContentType.objects.get_for_model(content_object)

    if tracker is None:
        tracker = replication_tracker_factory(
            content_type=ct
        )

    data = dict(content_type=ct, object_id=content_object.id,
                state=0, last_updated=now())
    data.update(**kwargs)
    return Replication.objects.create(**data)


def tasks_factory(object_ids=None, content_type_id=None, model_name=None, tracker_id=None, **kwargs):

    if object_ids is None:
        object_ids = test_result_link_factory(**kwargs).object_ids
    if content_type_id is None:
        pass
    if model_name is None:
        pass
    if object_ids is None:
        pass
    if tracker_id is None:
        tracker_id = replication_tracker_factory(
            content_type=kwargs.get('tracker_id')
        )

    data = dict(state=1,
                model_name=kwargs.get('model_name'),
                content_type_id=kwargs.get('content_type_id'))
    data.update(**kwargs)
    return tasks.objects.create(**data)
