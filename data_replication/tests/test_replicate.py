import logging
#import parser

from django.core.management import base

from data_replication.management.commands import replicate
from data_replication.management.commands.replicate import Command
from django.test import TestCase

from data_replication.models import ReplicationTracker


class TestReplicate(TestCase):
    def test_basic(self):
        instance = Command()
        self.assertEqual(instance.help, 'Replicate data to the different engines')

    def test_add_arguments(self):
        instance = Command()
        parser = instance.add_arguments()
        parser.add_argument()
        self.assertTrue(instance.requires_system_checks)

    def test_set_options(self, **options):
        instance = Command()
        self.assertEqual(instance.verbosity, int(options.get('verbosity', 0)))
        kwargs = {}
        self.assertEqual(instance.app_name, options.get('app'))
        self.assertEqual(instance.replication_class_name, options.get('replication_class_name'))
        self.assertEqual(instance.replication_type, options.get('replication_type'))

        level_map = {0: logging.ERROR, 1: logging.WARNING, 2: logging.INFO, 3: logging.DEBUG}
        self.assertEqual(instance.log_level, level_map.get(instance.verbosity, 0))

        self.assertEqual(instance.replications, ReplicationTracker.objects.filter(**kwargs))

        self.assertEqual(instance.replications.count(), not 0)
        with self.assertRaises(base.CommandError):
            instance.replications.count()

        if self.assertEqual(instance.replications.count(), 0):
            self.assertEqual(instance.no_subtasks, options.get('no_subtasks', False))
            self.assertEqual(instance.max_count, int(options.get('max_count')) if options.get('max_count') else None)
            self.assertEqual(instance.reset, options.get('reset', False))

    def test_handle(self, **options):
        instance = Command()
        so = instance.set_options(**options)
        total = instance.replications.count()

