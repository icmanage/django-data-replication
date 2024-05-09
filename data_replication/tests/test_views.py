from django import test
from django.utils.timezone import now
import logging

import data_replication.views as views


class ViewsTest(test.TestCase):

    def test_views(self):
        self.assertEqual(views.__author__, "Steven Klass", "author is incorrect")
        self.assertEqual(views.__date__, "9/21/17 07:56", "date is incorrect")
        self.assertEqual(views.__copyright__, "Copyright 2017 IC Manage. All rights reserved.", "copyright incorrect")
        self.assertEqual(views.__credits__, ["Steven Klass"], "credits is incorrect")
