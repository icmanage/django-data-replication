import django_extensions
from django.test import TestCase

from django.core import management
from django.core.management import CommandError

from django.apps import apps

from data_replication.models import ReplicationTracker, Replication
from data_replication.tests.factories import replication_tracker_factory
ip_verification_app = apps.get_app_config('ip_verification')

TestResultLink = apps.get_model('ip_verification', 'TestResultLink')


class DevNull:
    pass


class ManagementCommmandTestCase(TestCase):
    """This will flex out the Management Comands"""

    def setUp(self):
        """We want to set up our test data for running tests.
        When you do this you now this data available for each tests"""

        # Create us 10 tests all under the same summary ID
        ip_verification = ip_verification_app.test_result_link_factory()
        for i in range(10):
            ip_verification = ip_verification_app.test_result_link_factory(summary=ip_verification.summary)

        self.replication_tracker = replication_tracker_factory(replication_type="splunk", model=TestResultLink)

    def call_management_command(self, *args, **kwargs):
        """Wrap our management command with stdout dump to dev_null - we don't normally care about this"""
        # kwargs["stdout"] = DevNull()
        # kwargs["stderr"] = DevNull()
        return management.call_command(*args, **kwargs)

    def test_basic(self):
        """This is how we call the management commands for testing"""

        # We shouldn't have anything when we start
        self.assertEqual(ReplicationTracker.objects.count(), 1)
        self.assertEqual(Replication.objects.count(), 0)

        self.call_management_command(
            "replicate",
            "--app-name",
            "ip_verification",  # The name of the app
            "--replication-type",
            "splunk",
            "--replication_class_name",
            "TestResultSplunkReplicator",  # The class name of the replicator
            "--max_count",
            "2",
            "--no_subtasks"
        )

        self.assertEqual(Replication.objects.count(), 2)

