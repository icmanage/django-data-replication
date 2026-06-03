# -*- coding: utf-8 -*-
from __future__ import unicode_literals

__copyright__ = 'Copyright 2011-2026 IC Manage. All rights reserved.'

"""Tests for data_replication.backends.base.BaseReplicationCollector."""

import datetime

import mock
from django.test import TestCase
from django.utils.timezone import now

from data_replication.backends.base import BaseReplicationCollector
from data_replication.models import Replication, ReplicationTracker
from example.models import Example


class _Replicator(BaseReplicationCollector):
    """A minimal concrete collector with no external Mongo/Splunk I/O."""

    replication_type = 2  # Splunk
    model = Example
    change_keys = ['last_updated']

    def delete_items(self, object_pks):
        pass

    @property
    def task_name(self):
        # _add_items dispatches the push here; a mock keeps it in-process.
        return mock.MagicMock()

    @classmethod
    def add_items(cls, chunk_ids):
        return []


class _NoQueryTimeReplicator(_Replicator):
    """Mirrors the production host bug: overrides changed_queryset_pks but
    (deliberately) never sets self.query_time."""

    @property
    def changed_queryset_pks(self):
        if len(self._queryset_pks):
            return self._queryset_pks
        self._queryset_pks = list(self.get_queryset().values_list('pk', flat=True))
        return self._queryset_pks


def _example(ts):
    return Example.objects.create(name='x', last_updated=ts)


class LockTests(TestCase):
    def test_lock_creates_tracker_in_process(self):
        r = _Replicator()
        r.lock()
        self.assertTrue(r.locked)
        self.assertEqual(r.last_look.replication_type, 2)
        self.assertEqual(r.last_look.state, 2)  # In-Process
        # seeded ~100 years in the past so the first pass sees everything
        self.assertLess(r.last_look.last_updated, now() - datetime.timedelta(days=36000))

    def test_lock_reuses_existing_tracker(self):
        _Replicator().lock()
        self.assertEqual(ReplicationTracker.objects.count(), 1)
        _Replicator().lock()
        self.assertEqual(ReplicationTracker.objects.count(), 1)

    # Note: lock() also guards against a tracker row whose last_updated is
    # already NULL, but that state can't be created through the ORM on sqlite
    # (NOT NULL is enforced), so it isn't reproducible here. The equivalent
    # invariant on the write path is covered by UnlockTests below.


class UnlockTests(TestCase):
    def test_unlock_sets_last_updated_to_query_time(self):
        _example(now())
        r = _Replicator()
        r.analyze()
        r.last_look.refresh_from_db()
        self.assertEqual(r.last_look.state, 0)  # Ready
        self.assertEqual(r.last_look.last_updated, r.query_time)

    def test_unlock_never_persists_null_when_query_time_unset(self):
        """Regression: a changed_queryset_pks override that omits query_time
        used to make unlock() write NULL into the NOT NULL last_updated column
        (IntegrityError 1048 in production)."""
        _example(now())
        r = _NoQueryTimeReplicator()
        r.analyze()  # used to raise IntegrityError
        r.last_look.refresh_from_db()
        self.assertIsNotNone(r.last_look.last_updated)


class GetActionsTests(TestCase):
    def test_first_pass_adds_all_rows(self):
        _example(now())
        _example(now())
        r = _Replicator()
        r.lock()
        add, update, delete = r.get_actions()
        self.assertEqual(len(add), 2)
        self.assertEqual(update, [])
        self.assertEqual(delete, [])

    def test_replicated_rows_are_accounted_not_re_added(self):
        _example(now())
        _Replicator().analyze()  # first pass replicates the row
        self.assertEqual(Replication.objects.count(), 1)
        r = _Replicator()
        r.lock()
        add, update, delete = r.get_actions()
        self.assertEqual(add, [])
        self.assertEqual(delete, [])

    def test_new_row_after_last_run_is_an_add(self):
        old = _example(now() - datetime.timedelta(days=1))
        _Replicator().analyze()
        fresh = _example(now())
        r = _Replicator()
        r.lock()
        add, update, delete = r.get_actions()
        self.assertIn(fresh.pk, add)
        self.assertNotIn(old.pk, add)

    def test_deleted_source_row_becomes_a_delete(self):
        keep = _example(now())
        gone = _example(now())
        _Replicator().analyze()
        Example.objects.filter(pk=gone.pk).delete()
        r = _Replicator()
        r.lock()
        add, update, delete = r.get_actions()
        self.assertIn(gone.pk, delete)
        self.assertNotIn(keep.pk, delete)
