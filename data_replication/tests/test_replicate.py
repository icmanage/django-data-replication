from data_replication.management.commands import replicate
from data_replication.management.commands.replicate import Command
from django.test import TestCase


class TestReplicate(TestCase):
    def test_sum(self):
        instance = Command()