# -*- coding: utf-8 -*-
from data_replication.management.commands.replicate import Command
from django.test import TestCase


class TestReplicate(TestCase):
    def test_basic(self):
        instance = Command()
        self.assertEqual(instance.help, "Replicate data to the different engines")
