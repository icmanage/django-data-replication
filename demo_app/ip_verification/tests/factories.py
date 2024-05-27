# -*- coding: utf-8 -*-
"""factories.py - django-data-replication"""

__author__ = "Steven K"
__date__ = "5/27/24 12:31"
__copyright__ = "Copyright 2011-2024 IC Manage Inc. All rights reserved."
__credits__ = [
    "Steven K",
]

import datetime
import logging
import random

from django.apps import apps
from django.utils.timezone import now

log = logging.getLogger(__name__)


RegressionTagSummary = apps.get_model('ip_verification', 'RegressionTagSummary')
TestResultLink = apps.get_model('ip_verification', 'TestResultLink')


def regression_tag_summary_factory(**kwargs):
    total = random.randint(1, 1000)

    finalized = random.choice([True, False])

    passing = random.randint(1, total)
    failing = random.randint(1, total - passing)
    untested_count = 0
    if not finalized:
        untested_count = random.randint(1, total - passing-failing)

    kw = {
        'last_updated': now(),
        'first_requested': now()- datetime.timedelta(
            hours=random.randint(1, 3),
            minutes=random.randint(1, 5)),
        'untested_count': untested_count,
        'passing_count': passing,
        'failing_count': failing,
        'available': True,

    }
    kw.update(kwargs)
    return RegressionTagSummary.objects.create(**kw)


def test_result_link_factory(summary=None, **kwargs):
    if summary is None:
        summary = regression_tag_summary_factory()
    data = dict(summary=summary, test_result_id=random.randint(1, 1000000), last_used=now())
    data.update(**kwargs)
    return TestResultLink.objects.create(**data)


