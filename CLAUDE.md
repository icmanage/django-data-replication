# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## This branch: `stable/1.0.x` (Python 2.7 maintenance line)

This is the **production maintenance branch**, cut from tag `1.0.3`. The only
deployment runs **`django-data-replication` 1.0.x on Python 2.7 / Django 1.11**
(virtualenv `icm_ipcentral`, MariaDB), behind a corporate firewall.

**Do NOT port `master` here.** `master` (tagged `2.0.0`, never published) is a
Python-3.12 / Django-4.2+ rewrite and is runtime-incompatible with prod (it
removed `conf.py` in favour of `apps.py` settings, reworked migrations, dropped
`from __future__`/implicit relative imports, switched `setup.py` → `pyproject`).
Fixes for prod are made here and stay Python-2.7-safe (**no f-strings**, etc.).

## Commands

Tests run under a Python 2.7 + Django 1.11 venv via the standard
`manage.py test` against the never-shipped `demo_app/` project:

```bash
# one-time (pyenv has 2.7.18); pins matter -- see requirements-test.txt
python2.7 -m virtualenv .venv
.venv/bin/pip install -r requirements-test.txt

# run the suite (or: make test)
.venv/bin/python demo_app/manage.py test data_replication --settings=demo_app.settings_test
# a subset:
.venv/bin/python demo_app/manage.py test data_replication.tests.test_base.UnlockTests --settings=demo_app.settings_test
```

Tests live in `data_replication/tests/`. `demo_app/` is a Django project that
is **not built or shipped** (excluded from the sdist) — it provides the test
settings (`demo_app/demo_app/settings_test.py`) and the `example` app whose
`Example` model + `replication.py` drive the tests. The DB is in-memory
sqlite; external Mongo/Splunk I/O is mocked.

### Releasing & deploying
Releases are cut with the shared `../releaser` via `./release.sh`. See `README.md`
for the full prerequisites (ICM VPN; `../releaser` and `../icm_ipcatalog/.venv`
as siblings of this repo — so run from this canonical checkout, not a worktree;
branch pushed to origin; `.env` with `ICMUSER`).

```bash
./release.sh --dry-run   # preview the version + actions, change nothing
./release.sh             # auto micro-bump (1.0.4 -> 1.0.5 ...), confirm prompt, push tarball to ICM
```
`release.sh` passes `--force-micro` to keep this line in the **`1.0.x` corridor**
(1.1.x and 2.0.0 are already taken by the old master line — a release must never
auto-bump the minor and collide). Deploy on prod: `pip install --upgrade
data_replication-X.tar.gz` in the `icm_ipcentral` venv, then **restart the celery
workers** so they reload the code.

## Architecture

### The replication cycle (`data_replication/backends/base.py`)
`BaseReplicationCollector.analyze()` drives one pass:
1. `lock()` — find/create the `ReplicationTracker` for this (content_type,
   replication_type); set state In-Process. `reset=True` wipes prior `Replication` rows.
2. `get_actions()` — diff three PK sets: **changed** (queryset rows whose
   `change_keys` timestamp `> tracker.last_updated`), **accounted** (PKs already in
   `Replication`), and the current queryset → classify adds / updates / deletes.
3. Apply deletes then adds (optionally capped by `max_count`).
4. `unlock()` — advance `tracker.last_updated`, set state Ready.

Concrete replicators subclass `MongoReplicator` or `SplunkReplicator`, set `model`
and `change_keys`, and implement `add_items(pks) -> list[dict]` (each dict needs a
`pk`). Async pushes go through Celery tasks in `tasks.py` (`push_splunk_objects` /
`push_mongo_objects`).

### Discovery convention
`ReplicationTracker.get_replicator()` imports `<app_label>.replication` and finds the
subclass whose `model` matches the tracker's content type. Each replicated app must
define a `replication.py`.

### Settings (`data_replication/conf.py`)
Connection config is a **django-appconf** `DataMigrationConf(AppConf)` (`SPLUNK_*`,
`MONGO_*`). Backends import it as `from ..conf import settings`. (Note: this is
`conf.py` on this branch — `master` replaced it with `apps.py:DataMigrationSettings`.)

### Models / migrations
`ReplicationTracker` (`last_updated` is **NOT NULL**) and `Replication` (generic FK to
the source object). Migrations: `0001_initial` + `0002_auto_20210722_2316`.

## Gotchas

- **`unlock()` must never persist a NULL `last_updated`.** A subclass that overrides
  `changed_queryset_pks` and forgets `self.query_time = now()` will make `unlock()`
  Path A write `None` → `IntegrityError(1048)`. The base now falls back to `now()`
  (`self.query_time or now()`); keep that invariant, and set `query_time` in any new
  `changed_queryset_pks` override. Covered by `tests/run_unlock_regression.py`.
- **House style is enforced at release time.** The releaser's `pre_file_check`
  rejects the build unless every `.py` has `# -*- coding: utf-8 -*-`,
  `from __future__ import unicode_literals`, and a `Copyright 2011-<year>` line.
