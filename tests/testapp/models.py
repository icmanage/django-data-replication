# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models


class Thing(models.Model):
    """Minimal model to drive a replicator in tests."""

    timestamp = models.DateTimeField()
