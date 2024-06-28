# -*- coding: utf-8 -*-
from django.db import models


class Example(models.Model):
    name = models.CharField(max_length=16)
    last_updated = models.DateTimeField(auto_now=True)


class ManyExample(models.Model):
    name = models.CharField(max_length=16)
    last_updated = models.DateTimeField(auto_now=True)
