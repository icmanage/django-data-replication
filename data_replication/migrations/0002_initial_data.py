# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import os

from django.core.management import call_command
from django.db import migrations, models

fixture_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '../fixtures'))
fixture_filenames = [
    os.path.join(fixture_dir, 'data_replication', 'initial_data.json'),
]


def load_fixture(apps, schema_editor):
    for fixture_file in fixture_filenames:
        call_command('loaddata', fixture_file)


def unload_fixture(apps, schema_editor):
    for Model in [apps.get_model('data_replication', 'ReplicationTracker'),
                  apps.get_model('Replication')]:
        Model.objects.all().delete()


class Migration(migrations.Migration):

    dependencies = [
        ('data_replication', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(load_fixture, reverse_code=unload_fixture),
    ]
