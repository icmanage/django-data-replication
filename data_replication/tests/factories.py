# -*- coding: utf-8 -*-
import random

from django.apps import apps
from django.contrib.contenttypes.models import ContentType
from django.utils.timezone import now

from data_replication.models import REPLICATION_TYPES, ReplicationTracker, Replication

TestResultLink = apps.get_model("ip_verification", "TestResultLink")
ip_verification_app = apps.get_app_config("ip_verification")


def replication_tracker_factory(model=None, replication_type=None, **kwargs):
    ct = None
    if model:
        ct = ContentType.objects.get_for_model(model)

    if replication_type:
        assert replication_type in [1, 2, "splunk", "mongo"]
        replication_type = 2 if replication_type == "splunk" else replication_type
        replication_type = 1 if replication_type == "mongo" else replication_type
    else:
        replication_type = random.choice([x[0] for x in REPLICATION_TYPES])

    data = dict(replication_type=replication_type, content_type=ct, state=1, last_updated=now())

    data.update(**kwargs)
    return ReplicationTracker.objects.create(**data)


def replication_factory(tracker=None, content_object=None, **kwargs):
    if content_object is None:
        content_object = ip_verification_app.test_result_link_factory(**kwargs)

    ct = ContentType.objects.get_for_model(content_object)

    if tracker is None:
        tracker = replication_tracker_factory(content_type=ct)

    data = dict(content_type=ct, object_id=content_object.id, state=0, last_updated=now())
    data.update(**kwargs)
    return Replication.objects.create(**data)
