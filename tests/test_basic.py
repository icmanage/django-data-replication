# -*- coding: utf-8 -*-
from __future__ import unicode_literals
__copyright__ = 'Copyright 2011-2026 IC Manage. All rights reserved.'

from .context import sample

import unittest


class BasicTestSuite(unittest.TestCase):
    """Basic test cases."""

    def test_absolute_truth_and_meaning(self):
        assert True


if __name__ == '__main__':
    unittest.main()