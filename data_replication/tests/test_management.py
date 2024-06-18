import datetime

from django.core.management import CommandError
from django.test import TestCase

from django.core import management

from django.apps import apps
from mock import mock

from data_replication.models import ReplicationTracker, Replication
from data_replication.tests.factories import replication_tracker_factory
from data_replication.tests.test_tasks import mock_session

ip_verification_app = apps.get_app_config('ip_verification')

Example = apps.get_model('example', 'Example')

class DevNull:
    pass


class ManagementCommmandTestCase(TestCase):
    """This will flex out the Management Comands"""

    def setUp(self):
        """We want to set up our test data for running tests.
        When you do this you now this data available for each tests"""
        object_ids = []
        for i in range(3):
            example = Example.objects.create(name='User' + str(i))
            object_ids.append(example.id)

        rt = replication_tracker_factory(
            model=Example, replication_type=2,
            last_updated=datetime.datetime.now() - datetime.timedelta(days=1)
        )
        self.assertEqual(ReplicationTracker.objects.count(), 1)
        self.assertEqual(Replication.objects.count(), 0)

    def call_management_command(self, *args, **kwargs):
        """Wrap our management command with stdout dump to dev_null - we don't normally care about this"""
        # kwargs["stdout"] = DevNull()
        # kwargs["stderr"] = DevNull()
        return management.call_command(*args, **kwargs)

    @mock.patch('data_replication.backends.splunk.SplunkRequest.session', mock_session)
    def test_basic(self):
        """This is how we call the management commands for testing"""

        # We shouldn't have anything when we start
        self.assertEqual(ReplicationTracker.objects.count(), 1)
        self.assertEqual(Replication.objects.count(), 0)
        self.call_management_command(
            "replicate",
            "--app-name",
            "example",  # The name of the app
            "--replication-type",
            "splunk",
            "--replication_class_name",
            "TestSplunkReplicatorExample",  # The class name of the replicator
            "--max_count",
            "2",
            "--no_subtasks"
        )

        self.assertEqual(Replication.objects.count(), 2)
