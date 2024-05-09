from django import test
from django.utils.timezone import now
import logging

import data_replication.forms as forms


class FormsTest(test.TestCase):

    def test_forms(self):
        self.assertEqual(forms.__author__, "Steven Klass", "author is incorrect")
        self.assertEqual(forms.__date__, "9/21/17 07:56", "date is incorrect")
        self.assertEqual(forms.__copyright__, "Copyright 2017 IC Manage. All rights reserved.", "copyright incorrect")
        self.assertEqual(forms.__credits__, ["Steven Klass"], "credits is incorrect")