# -*- coding: utf-8 -*-
from __future__ import unicode_literals
__copyright__ = 'Copyright 2011-2026 IC Manage. All rights reserved.'

from .context import sample

import unittest


class AdvancedTestSuite(unittest.TestCase):
    """Advanced test cases."""

    def test_thoughts(self):
        self.assertIsNone(sample.hmm())


if __name__ == '__main__':
    unittest.main()
