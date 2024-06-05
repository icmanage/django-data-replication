import logging
#import parser

from django.core.management import base, CommandParser

from data_replication.management.commands import replicate
from data_replication.management.commands.replicate import Command
from django.test import TestCase

from data_replication.models import ReplicationTracker


# I had a question here for why the instance attributes are seemingly created outside __init__
# this makes the attributes "exist outside of Command"
class TestReplicate(TestCase):
    def test_basic(self):
        instance = Command()
        self.assertEqual(instance.help, 'Replicate data to the different engines')

    def XXXtest_add_arguments(self):
        instance = Command()
        parser = CommandParser(cmd='test_command')
        instance.add_arguments(parser)

        # Argument '-f' or '--no-confirm'
        self.assertTrue(any(arg.option_strings == ['-f', '--no-confirm'] for arg in parser._actions))
        no_confirm_action = [arg for arg in parser._actions if arg.option_strings == ['-f', '--no-confirm']][0]
        self.assertEqual(no_confirm_action.dest, 'no_confirm')
        self.assertEqual(no_confirm_action.help, 'Do not prompt for confirmation')

        # -a or --app-name
        self.assertTrue(any(arg.option_strings == ['-a', '--app-name'] for arg in parser._actions))
        no_confirm_action = [arg for arg in parser._actions if arg.option_strings == ['-a', '--app-name']][0]
        self.assertEqual(no_confirm_action.dest, 'app')
        self.assertEqual(no_confirm_action.help, 'Provide the app to work on to replication')

        # -t or --replication-type
        self.assertTrue(any(arg.option_strings == ['-t', '--replication-type'] for arg in parser._actions))
        no_confirm_action = [arg for arg in parser._actions if arg.option_strings == ['-t', '--replication-type']][0]
        self.assertEqual(no_confirm_action.dest, 'replication_type')
        self.assertEqual(no_confirm_action.help, 'Provide the type of replication')

        # -R or --replication_class_name
        self.assertTrue(any(arg.option_strings == ['-R', '--replication_class_name'] for arg in parser._actions))
        no_confirm_action = \
            [arg for arg in parser._actions if arg.option_strings == ['-R', '--replication_class_name']][0]
        self.assertEqual(no_confirm_action.dest, 'replication_class_name')
        self.assertEqual(no_confirm_action.help, 'Replication Class Name')

        # -T or --no_subtasks
        self.assertTrue(any(arg.option_strings == ['-T', '--no_subtasks'] for arg in parser._actions))
        no_confirm_action = [arg for arg in parser._actions if arg.option_strings == ['-T', '--no_subtasks']][0]
        self.assertEqual(no_confirm_action.dest, 'no_subtasks')
        self.assertEqual(no_confirm_action.help, 'Sub Tasks')

        # -m or --max_count
        self.assertTrue(any(arg.option_strings == ['-m', '--max_count'] for arg in parser._actions))
        no_confirm_action = [arg for arg in parser._actions if arg.option_strings == ['-m', '--max_count']][0]
        self.assertEqual(no_confirm_action.dest, 'max_count')
        self.assertEqual(no_confirm_action.help, 'Max count -- DEV ONLY FOR TESTING')

        # --reset
        self.assertTrue(any(arg.option_strings == ['--reset'] for arg in parser._actions))
        no_confirm_action = [arg for arg in parser._actions if arg.option_strings == ['--no-confirm']][0]
        self.assertEqual(no_confirm_action.dest, 'reset')
        self.assertEqual(no_confirm_action.help, 'Reset -- DEV ONLY FOR TESTING')
        self.assertTrue(instance.requires_system_checks)

    def XXXtest_set_options(self, **options):
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

    # I don't want to use GPT to finish this at least for now. I'll come back to it
    def XXXtest_handle(self, **options):
        instance = Command()
        # total = instance.replications.count()

        options = {'replication_class_name': 'replication_class',
                   'use_subtasks': False,
                   'max_count': 100,
                   'reset': False,
                   'log_level': 0}
        instance.handle()

        self.assertIn("Done!!", instance.stdout.getvalue())
