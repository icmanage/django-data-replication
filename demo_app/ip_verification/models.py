# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib.contenttypes.fields import GenericRelation
from django.db import models
from django.db.models import SET_NULL


# Create your models here.
class TestResultLink(models.Model):
    test_result_id = models.PositiveIntegerField(null=True, db_index=True)
    summary = models.ForeignKey('RegressionTagSummary', related_name="test_results", null=True, on_delete=SET_NULL)
    last_used = models.DateTimeField(db_index=True)
    replications = GenericRelation('data_replication.Replication')


class RegressionTagSummary(models.Model):
    pass


class RegressionAnalytic(models.Model):
    summary = models.OneToOneField('RegressionTagSummary', related_name="analytics", null=True, on_delete=SET_NULL)
    last_updated = models.DateTimeField(auto_now=True, db_index=True)
    replications = GenericRelation('data_replication.Replication')
