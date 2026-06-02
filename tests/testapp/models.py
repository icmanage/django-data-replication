# -*- coding: utf-8 -*-
from __future__ import unicode_literals
__copyright__ = 'Copyright 2011-2026 IC Manage. All rights reserved.'

from django.db import models


class Thing(models.Model):
    """Minimal model to drive a replicator in tests."""

    timestamp = models.DateTimeField()
