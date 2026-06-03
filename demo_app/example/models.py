# -*- coding: utf-8 -*-
from __future__ import unicode_literals

__copyright__ = 'Copyright 2011-2026 IC Manage. All rights reserved.'

from django.db import models


class Example(models.Model):
    """A trivial model to drive replication in tests. last_updated is a plain
    field (not auto_now) so tests can control change-detection timestamps."""

    name = models.CharField(max_length=16, blank=True)
    last_updated = models.DateTimeField()
