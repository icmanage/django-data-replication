import decimal
from django.test import TestCase
import mock
from django.utils.datetime_safe import datetime
from mock import Mock, patch
import data_replication.backends.splunk as splunk
from data_replication.backends.splunk import SplunkAuthenticationException
from data_replication.backends.splunk import SplunkPostException
from data_replication.backends.splunk import SplunkRequest
from django.apps import apps
from data_replication.tests.test_tasks import MockSession, MockSession2

data_replication_app = apps.get_app_config("data_replication")
Example = apps.get_model("example", "Example")


class TestSplunk(TestCase):

    def setUp(self):
        class FooBar(SplunkRequest):
            model = Example
            change_keys = ["foo"]
            object_pks = ["all", "these", "things"]

        self.splunk_request = FooBar

        class FooBarf(SplunkRequest):
            model = Example
            change_keys = ["foo"]
            object_pks = []

        self.splunk_request2 = FooBarf

    def test_splunk_basics(self):
        self.assertEqual(splunk.__author__, "Steven Klass", "author is incorrect")
        self.assertEqual(splunk.__date__, "9/21/17 08:11", "date is incorrect")
        self.assertEqual(
            splunk.__copyright__,
            "Copyright 2017 IC Manage. All rights reserved.",
            "copyright incorrect",
        )
        self.assertEqual(splunk.__credits__, ["Steven Klass"], "credits is incorrect")
        self.assertEqual(splunk.SPLUNK_PREFERRED_DATETIME, "%Y-%m-%d %H:%M:%S:%f")
        # self.assertEqual(splunk.INTS, re.compile(r"^-?[0-9]+$"))
        # self.assertEqual(splunk.NUMS, re.compile(r"^[+-]?\d+(?:\.\d+)?(?:[eE][+-]?\d+)?$"))

    def test_splunk_auth_exception(self):
        with self.assertRaises(SplunkAuthenticationException):
            raise SplunkAuthenticationException("hello")
        try:
            raise SplunkAuthenticationException("hello")
        except SplunkAuthenticationException as error:
            self.assertIn("hello", str(error))

    def test_splunk_post_exception(self):
        with self.assertRaises(SplunkPostException):
            raise SplunkPostException("hello")
        try:
            raise SplunkPostException("hello")
        except SplunkPostException as error:
            self.assertIn("hello", str(error))

    @patch.object(SplunkRequest, "connect")
    def test_get_search_status(self, mock_sleep):
        mock_session = Mock()
        mock_request = Mock()
        mock_request.status_code = 400
        mock_request.json.return_value = {"results": ["mocked_data"]}
        mock_session.get.return_value = mock_request

        with patch.object(SplunkRequest, "session", new=mock_session):
            search_instance = SplunkRequest()
            result, status_code = search_instance.get_search_status("mock_search_id")

            self.assertEqual(status_code, 400)
            self.assertEqual(result, {"results": ["mocked_data"]})

    @patch.object(SplunkRequest, "connect")
    def test_get_search_status_break_error_count(self, mock_sleep):
        mock_session = Mock()
        mock_request = Mock()
        mock_request.error_count = 4
        mock_request.status_code = 400
        mock_request.json.return_value = {"results": ["mocked_data"]}
        mock_session.get.return_value = mock_request

        with patch.object(SplunkRequest, "session", new=mock_session):
            search_instance = SplunkRequest()
            result, status_code = search_instance.get_search_status("mock_search_id")

            self.assertEqual(status_code, 400)
            self.assertEqual(result, {"results": ["mocked_data"]})

    @patch.object(SplunkRequest, "connect")
    def test_get_search_status_break_wait_for_results(self, mock_sleep):
        mock_session = Mock()
        mock_request = Mock()
        mock_request.wait_for_results = False
        mock_request.status_code = 200
        mock_request.json.return_value = {"results": ["mocked_data"]}
        mock_session.get.return_value = mock_request

        with patch.object(SplunkRequest, "session", new=mock_session):
            search_instance = SplunkRequest()
            result, status_code = search_instance.get_search_status("mock_search_id")

            self.assertEqual(status_code, 200)
            self.assertEqual(result, {"results": ["mocked_data"]})

    @mock.patch("requests.Session", MockSession)
    def test_connect(self):
        splunk_request = SplunkRequest()
        splunk_request.connect()

    @mock.patch("requests.Session", MockSession2)
    def test_connect_error(self):
        splunk_request = SplunkRequest()
        with self.assertRaises(SplunkAuthenticationException):
            splunk_request.connect()

    @mock.patch("requests.Session", MockSession2)
    def test_connect_barf(self):
        with self.assertRaises(SplunkAuthenticationException):
            splunk_request = SplunkRequest()
            splunk_request.connect()

    def test_splunk_default_error(self):
        obj = 6.9
        with self.assertRaises(TypeError):
            instance = splunk.splunk_default(obj)

    def test_splunk_default_dec(self):
        obj = decimal.Decimal("6.9")
        instance = splunk.splunk_default(obj)
        self.assertEqual(instance, 6.9)

    def test_splunk_default_dat(self):
        obj = datetime(2024, 6, 23, 00, 00, 00)
        instance = splunk.splunk_default(obj)
        self.assertEqual(instance, "2024-06-23T00:00:00")
