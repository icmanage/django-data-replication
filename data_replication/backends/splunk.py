# -*- coding: utf-8 -*-
"""splunk: Django data_replication"""

import decimal
import json
import logging
import re
import time
from collections import OrderedDict

import datetime
import requests

from .base import BaseReplicationCollector, ImproperlyConfiguredException
from ..apps import settings

__author__ = 'Steven Klass'
__date__ = '9/21/17 08:11'
__copyright__ = 'Copyright 2017 IC Manage. All rights reserved.'
__credits__ = ['Steven Klass', ]

log = logging.getLogger(__name__)

SPLUNK_PREFERRED_DATETIME = "%Y-%m-%d %H:%M:%S:%f"
INTS = re.compile(r"^-?[0-9]+$")
NUMS = re.compile(r"^[+-]?\d+(?:\.\d+)?(?:[eE][+-]?\d+)?$")


def splunk_default(obj):
    if isinstance(obj, decimal.Decimal):
        return float(obj)
    if isinstance(obj, datetime.datetime):
        return obj.isoformat()
    raise TypeError


class SplunkAuthenticationException(Exception):
    def __init__(self, value, *args, **kwargs):
        self.value = value

    def __str__(self):
        return repr(self.value)


class SplunkPostException(Exception):
    def __init__(self, value, *args, **kwargs):
        self.value = value

    def __str__(self):
        return repr(self.value)


class SplunkRequest(object):
    def __init__(self, *args, **kwargs):

        try:
            self.username = kwargs.get('username', settings.SPLUNK_USERNAME)
        except AttributeError:
            raise ImproperlyConfiguredException("Missing settings.SPLUNK_USERNAME")
        try:
            self.password = kwargs.get('password', settings.SPLUNK_PASSWORD)
        except AttributeError:
            raise ImproperlyConfiguredException("Missing settings.SPLUNK_PASSWORD")
        self.scheme = kwargs.get('scheme', settings.SPLUNK_SCHEME)
        self.host = kwargs.get('host', settings.SPLUNK_HOST)
        self.port = kwargs.get('port', settings.SPLUNK_PORT)
        self.session_key = kwargs.get('splunk_session_key')
        self.session = None
        self.base_url = '{scheme}://{host}:{port}'.format(scheme=self.scheme, host=self.host, port=self.port)

    def connect(self, **kwargs):
        if self.session_key:
            return

        if self.session:
            return self.session

        self.session = requests.Session()
        try:
            url = '{base_url}/services/auth/login?output_mode=json'.format(base_url=self.base_url)
            request = self.session.post(
                url, data={'username': self.username, 'password': self.password},
                auth=(self.username, self.password), verify=False)
            if request.status_code != 200:
                raise SplunkAuthenticationException(
                    "Authorization error ({status_code}) connecting to {url}".format(
                        status_code=request.status_code, url=url))
            self.session_key = request.json().get('sessionKey')
            self.headers = {'Authorization': 'Splunk {session_key}'.format(**self.__dict__),
                            'content-type': 'application/json'}
        except:
            log.error("Issue connecting to %(base_url)s with %(username)s:%(password)s", self.__dict__)
            raise
        log.debug("Successfully logged in and have session key %(session_key)s", self.__dict__)


    def create_search(self, search_query):
        """Create a basic search"""
        self.connect()
        if not search_query.startswith('search'):
            search_query = 'search {search_query}'.format(search_query=search_query)
        request = self.session.post(
            '{base_url}/services/search/jobs?output_mode=json'.format(base_url=self.base_url),
            headers=self.headers, data={'search': search_query}, verify=False)

        data = request.json()
        if data.get('messages') and data.get('messages')[0].get('type') == 'FATAL':
            log.error('FATAL response received: {text}'.format(
                text=data.get('messages')[0].get('text')))
        log.debug("Created search on {search} with search id = {sid}".format(search=search_query, **data))
        return data.get('sid')

    def get_search_status(self, search_id, wait_for_results=True):

        self.connect()
        url = '{base_url}/services/search/jobs/{search_id}/results?output_mode=json'
        start = None
        error_count = 0
        while True:
            request = self.session.get(url.format(base_url=self.base_url, search_id=search_id),
                                       headers=self.headers, verify=False)
            if not wait_for_results:
                break

            if error_count > 3:
                break

            if not start or (datetime.datetime.now() - start).seconds > 5:
                log.debug("Waiting on results")
                start = datetime.datetime.now()
            if request.status_code == 200:
                break
            if request.status_code == 400:
                log.error("Unable to push to {} - {}".format(url.format(base_url=self.base_url, search_id=search_id),
                                                             request.json()))
                error_count += 1

            time.sleep(.5)
        return request.json(), request.status_code

    def delete_items(self, object_pks):
        if not len(object_pks):
            return
        ids = " OR ".join(["id={}".format(x) for x in object_pks])
        delete_query = "{} ({}) | delete".format(self.search_quantifier, ids)
        search_id = self.splunk.create_search(delete_query)
        return self.splunk.get_search_status(search_id, wait_for_results=True)

    @classmethod
    def get_normalized_data(cls, content):

        data = OrderedDict()
        keys = content.keys()


        for date_key in ['host', 'hostname']:
            if date_key in keys:
                keys.pop(keys.index(date_key))
                keys = [date_key] + keys
                break

        for date_key in ['time', 'date', 'timestamp']:
            if date_key in keys:
                keys.pop(keys.index(date_key))
                keys = [date_key] + keys
                break

        for key in keys:
            value = content.get(key)
            if isinstance(value, str):
                if value.startswith("00"):
                    pass
                elif INTS.search(value):
                    value = int(value)
                elif NUMS.search(value):
                    value = float(value)
            data[key] = value
        return data

    def post_data(self, content, source="tcp://envision", sourcetype="json", host='envision', dry_run=False):
        """Push to splunk - data"""
        self.connect()
        params = {'host': host, 'source': source, 'sourcetype': sourcetype}
        url = '{base_url}/services/receivers/stream'.format(base_url=self.base_url)
        headers = self.headers.copy()
        headers.update({'content-type': 'application/json', 'x-splunk-input-mode': 'streaming'})

        if not isinstance(content, (list, tuple)):
            content = [content]

        content = [self.get_normalized_data(item) for item in content]

        _content = []
        for item in content:
            _data = json.dumps(item, default=splunk_default, sort_keys=False)
            _content.append(_data)
        data = "\n".join(_content)

        if not dry_run:
            response = self.session.post(
                url, data=data, headers=headers,
                params=params, verify=False)

            if response.status_code != 204:
                log.error("Unable to push to {} - {}".format(url, content))
                raise SplunkPostException("Unable to push to {} - {}".format(url, content))
        else:
            log.info(data)

        return None


class SplunkReplicator(BaseReplicationCollector):
    replication_type = 2
    source = "tcp://envision"
    source_type = "json"
    host = "hostname"

    @property
    def search_quantifier(self):
        data = ""
        if self.search_quantifiers:
            data = self.search_quantifier
        return data + " model={}".format(self.model._meta.model_name)

    def delete_items(self, object_pks):
        if not len(object_pks):
            return
        splunk = SplunkRequest()
        ids = " OR ".join(["pk={}".format(x) for x in object_pks])
        delete_query = "{} ({}) | delete".format(self.search_quantifier, ids)
        search_id = splunk.create_search(delete_query)
        return splunk.get_search_status(search_id, wait_for_results=True)

    @property
    def task_name(self):
        from data_replication.tasks import push_splunk_objects
        return push_splunk_objects

    def get_task_kwargs(self):
        return {'source': self.source, 'source_type': self.source_type, 'host': self.host,
                'model_name': self.model._meta.model_name, 'replication_class_name': self.__class__.__name__}