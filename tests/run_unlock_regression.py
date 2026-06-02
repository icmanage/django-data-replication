# -*- coding: utf-8 -*-
"""Regression: unlock() must never persist a NULL last_updated.

Reproduces the production failure raised by apps.splunk.tasks
.periodic_push_change_data on icm_ipcentral (py2.7):

    IntegrityError(1048, "Column 'last_updated' cannot be null")
    ... base.py unlock() -> self.last_look.save()

Root cause: a replicator subclass overrides ``changed_queryset_pks``
WITHOUT setting ``self.query_time`` (the base implementation sets it as its
first statement). ``unlock()`` Path A then assigns ``self.query_time`` --
which is still the ``__init__`` default of None -- to the NOT NULL
``last_updated`` column.

Self-contained so it runs on the production runtime (py2.7 + Django 1.11)
without the optional Mongo/Splunk/Celery dependencies:

    PYTHONPATH=. /tmp/ddr27/bin/python tests/test_unlock_null_regression.py
"""
from __future__ import unicode_literals
from __future__ import print_function

import sys
import types


def _stub(name, **attrs):
    module = types.ModuleType(str(name))
    for key, value in attrs.items():
        setattr(module, str(key), value)
    sys.modules[str(name)] = module
    return module


# Stub the optional heavy dependencies imported at package load time so the
# replication code can be imported with only Django + pytz installed.
class _OperationalError(Exception):
    pass


class _ConnectionFailure(Exception):
    pass


class _OperationFailure(Exception):
    pass


_stub("kombu")
_stub("kombu.exceptions", OperationalError=_OperationalError)
_stub("pymongo", MongoClient=object)
_stub("pymongo.errors", ConnectionFailure=_ConnectionFailure,
      OperationFailure=_OperationFailure)
_stub("requests")
_stub("appconf", AppConf=type(str("AppConf"), (object,), {}))


import django
from django.conf import settings

settings.configure(
    DEBUG=True,
    DATABASES={"default": {"ENGINE": "django.db.backends.sqlite3",
                           "NAME": ":memory:"}},
    INSTALLED_APPS=[
        "django.contrib.contenttypes",
        "django.contrib.auth",
        "data_replication",
        "tests.testapp",
    ],
    USE_TZ=True,
)
django.setup()

from django.core.management import call_command
from data_replication.backends.base import BaseReplicationCollector
from tests.testapp.models import Thing


class _OverrideWithoutQueryTime(BaseReplicationCollector):
    """Mirrors PerforceChangeDataReplicator: overrides changed_queryset_pks
    and (like the production code) never sets self.query_time."""

    replication_type = 2  # Splunk
    model = Thing
    change_keys = ["timestamp"]

    @property
    def changed_queryset_pks(self):
        if len(self._queryset_pks):
            return self._queryset_pks
        # Deliberately omits ``self.query_time = now()`` -- this is the bug.
        self._queryset_pks = list(
            self.get_queryset().values_list("pk", flat=True))
        return self._queryset_pks

    def delete_items(self, object_pks):  # pragma: no cover - never called here
        pass


def main():
    call_command("migrate", run_syncdb=True, verbosity=0)

    replicator = _OverrideWithoutQueryTime()
    replicator.analyze()  # raised IntegrityError before the fix

    replicator.last_look.refresh_from_db()
    assert replicator.last_look.last_updated is not None, \
        "unlock() persisted a NULL last_updated"

    print("PASS: unlock() persisted last_updated=%r"
          % replicator.last_look.last_updated)


if __name__ == "__main__":
    main()
