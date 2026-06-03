# -*- coding: utf-8 -*-
from __future__ import unicode_literals

__copyright__ = 'Copyright 2011-2026 IC Manage. All rights reserved.'

"""Tests for data_replication.backends.splunk (SplunkRequest + helpers)."""

import datetime
import decimal

from django.test import TestCase

from data_replication.backends.splunk import (
    SplunkAuthenticationException,
    SplunkPostException,
    SplunkRequest,
    splunk_default,
)


class _Resp(object):
    def __init__(self, status_code, payload=None):
        self.status_code = status_code
        self._payload = payload or {}

    def json(self):
        return self._payload


class _Session(object):
    """A stand-in requests.Session: 200 for auth, configurable for the
    streaming receiver."""

    def __init__(self, stream_code=204):
        self.stream_code = stream_code
        self.posts = []

    def post(self, url, **kwargs):
        self.posts.append(url)
        if url.endswith('/services/auth/login?output_mode=json'):
            return _Resp(200, {'sessionKey': 'KEY'})
        if url.endswith('/services/receivers/stream'):
            return _Resp(self.stream_code)
        return _Resp(200, {'sid': '123'})


def _request(stream_code=204):
    req = SplunkRequest(username='u', password='p', host='localhost',
                        port='8089', scheme='https')
    req.session = _Session(stream_code=stream_code)  # pre-set => connect() no-ops
    req.headers = {}  # normally populated by connect() after auth
    return req


class SplunkDefaultTests(TestCase):
    def test_decimal_becomes_float(self):
        self.assertEqual(splunk_default(decimal.Decimal('1.5')), 1.5)

    def test_datetime_becomes_isoformat(self):
        dt = datetime.datetime(2026, 6, 3, 12, 0, 0)
        self.assertEqual(splunk_default(dt), dt.isoformat())

    def test_unhandled_type_raises(self):
        with self.assertRaises(TypeError):
            splunk_default(object())


class GetNormalizedDataTests(TestCase):
    def test_hoists_time_and_host_and_coerces_numbers(self):
        data = SplunkRequest.get_normalized_data({
            'host': 'h', 'time': '5', 'count': '10', 'ratio': '1.5', 'code': '007',
        })
        keys = list(data.keys())
        self.assertEqual(keys[0], 'time')     # time hoisted to the very front
        self.assertEqual(keys[1], 'host')     # host hoisted just behind it
        self.assertEqual(data['count'], 10)   # int string -> int
        self.assertEqual(data['ratio'], 1.5)  # float string -> float
        self.assertEqual(data['code'], '007')  # leading-zero string preserved


class PostDataTests(TestCase):
    def test_success_posts_to_stream(self):
        req = _request(stream_code=204)
        req.post_data([{'pk': 1, 'name': 'a'}], host='envision')
        self.assertTrue(any('receivers/stream' in u for u in req.session.posts))

    def test_non_204_raises_post_exception(self):
        req = _request(stream_code=500)
        with self.assertRaises(SplunkPostException):
            req.post_data([{'pk': 1, 'name': 'a'}])

    def test_dry_run_does_not_post(self):
        req = _request()
        req.post_data([{'pk': 1}], dry_run=True)
        self.assertNotIn('https://localhost:8089/services/receivers/stream', req.session.posts)


class ExceptionTests(TestCase):
    def test_auth_exception_str(self):
        self.assertIn('boom', str(SplunkAuthenticationException('boom')))

    def test_post_exception_str(self):
        self.assertIn('boom', str(SplunkPostException('boom')))
