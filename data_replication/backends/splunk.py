# -*- coding: utf-8 -*-
"""splunk: Django data_replication"""

from __future__ import unicode_literals
from __future__ import print_function

import logging

from data_replication.backends.base import BaseReplicationCollector

__author__ = 'Steven Klass'
__date__ = '9/21/17 08:11'
__copyright__ = 'Copyright 2017 IC Manage. All rights reserved.'
__credits__ = ['Steven Klass', ]

log = logging.getLogger(__name__)


class SplunkReplicator(BaseReplicationCollector):
    replication_type = 1
    splunk_ready = False

    @property
    def splunk(self):
        if not self.splunk_ready:
            print("Setting SPLUNK READY")  # TODO
            # self.splunk_req = SplunkRequest()
            self.splunk_ready = True
        return self.splunk_req

    def delete_items(self, object_pks):
        if not len(object_pks):
            return
        ids = " OR ".join(["id={}".format(x) for x in object_pks])
        delete_query = "{} ({}) | delete".format(self.search_quantifier, ids)
        search_id = self.splunk.create_search(delete_query)
        return self.splunk.get_search_status(search_id, wait_for_results=True)

    def add_items(self, object_pks):
        print("Adding ")