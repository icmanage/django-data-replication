# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib.contenttypes.fields import GenericRelation
from django.db import models
from django.db.models import SET_NULL
from django_extensions.db.fields.json import JSONField

from .managers import TestResultLinkManager, RegressionTagSummaryManager


class TestStatusName(models.Model):
    """This is a mapping of status to keep everything consistant"""

    name = models.CharField(max_length=128, null=True)
    status_id = models.PositiveIntegerField(null=True, db_index=True)
    last_used = models.DateTimeField(null=True)


# Create your models here.
class TestResultLink(models.Model):
    updated_status = models.ForeignKey(
        "TestStatusName", null=True, blank=True, on_delete=models.SET_NULL
    )
    test_result_id = models.PositiveIntegerField(null=True, db_index=True)
    summary = models.ForeignKey(
        "RegressionTagSummary", related_name="test_results", null=True, on_delete=SET_NULL
    )
    last_used = models.DateTimeField(db_index=True)
    replications = GenericRelation("data_replication.Replication")
    options = JSONField(default=dict)
    objects = TestResultLinkManager()


class RegressionTagSummary(models.Model):
    first_requested = models.DateTimeField()
    last_updated = models.DateTimeField(db_index=True)

    untested_count = models.PositiveIntegerField(default=0)
    passing_count = models.PositiveIntegerField(default=0)
    failing_count = models.PositiveIntegerField(default=0)

    finalized = models.BooleanField(default=False)
    available = models.BooleanField(
        default=False
    )  # This is used to identify those which are ready for showing.

    objects = RegressionTagSummaryManager()


class RegressionAnalytic(models.Model):
    summary = models.OneToOneField(
        "RegressionTagSummary", related_name="analytics", null=True, on_delete=SET_NULL
    )
    last_updated = models.DateTimeField(auto_now=True, db_index=True)
    replications = GenericRelation("data_replication.Replication")


class PlannedTestCase(models.Model):
    plan_qty = models.PositiveIntegerField()
    plan_date = models.DateField()

    last_updated = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["plan_date"]
