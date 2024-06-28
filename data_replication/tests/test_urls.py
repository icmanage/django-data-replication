from django import test
import data_replication.urls as urls


class UrlsTest(test.TestCase):

    def test_urls(self):
        self.assertEqual(urls.__author__, "Steven Klass", "author is incorrect")
        self.assertEqual(urls.__date__, "9/21/17 07:57", "date is incorrect")
        self.assertEqual(
            urls.__copyright__,
            "Copyright 2017 IC Manage. All rights reserved.",
            "copyright incorrect",
        )
        self.assertEqual(urls.__credits__, ["Steven Klass"], "credits is incorrect")
