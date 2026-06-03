# Django Data Replication

This will allow you to replicate data to another place - Like mongo for analytics.

Learn more https://github.com/icmanage/django-data-replication.

## Production / branch model

The only production deployment runs **`django-data-replication` 1.0.x on Python 2.7**
(virtualenv `icm_ipcentral`). This `stable/1.0.x` branch is the maintenance line,
cut from tag `1.0.3` (which is byte-identical to the published PyPI 1.0.3).

**Do not release production from `master`.** `master` (tagged `2.0.0`, never published)
is a Python-3.12 / Django-4.2+ rewrite and is runtime-incompatible with prod
(removed `conf.py`, reworked migrations, dropped `from __future__`/implicit relative
imports). Fixes for prod are made here, on `stable/1.0.x`.

## Releasing

Releases are cut with the shared `../releaser` tool (the same one `ip_verification`
uses), driven by `release.sh`. It bumps the version, tags the release, and builds the
package tarball.

### Prerequisites
- On the **ICM VPN** (the releaser checks internal connectivity first).
- `../releaser` and `../icm_ipcatalog/.venv` exist as **siblings** of this repo
  (so run from a checkout at e.g. `/Volumes/Development/django-data-replication`,
  not from a git worktree, or the `../` paths won't resolve).
- The branch is **pushed to origin** (`git push -u origin stable/1.0.x`) — the
  releaser tags against the remote and refuses if local/remote differ.
- A local **`.env`** (gitignored) defining **`ICMUSER`** — the ssh user used to
  scp the tarball to the ICM FTP (`--push-tarball`).

### Commands
```bash
./release.sh --dry-run     # preview the computed version + actions, change nothing
./release.sh               # auto micro-bump from the latest tag (1.0.3 -> 1.0.4 ...),
                           #   prompts to confirm releasing from a non-master branch
./release.sh --noinput     # same, but skip the branch-confirmation prompt (automation)
./release.sh --release 1.0.7   # force a specific version
```

`release.sh` passes `--force-micro`, which **keeps this line in the `1.0.x` corridor**
(1.0.4, 1.0.5, ...). This is deliberate: `1.1.0`–`1.1.5` and `2.0.0` are already taken
by the old master line, so a large changeset must never be allowed to auto-bump the
minor and collide with an existing tag.

### What a release does
1. Bumps `version=` in `setup.py` **and** `__version_info__`/`__version__` in
   `data_replication/__init__.py`, commits ("Bump to X") and pushes.
2. Creates the annotated git tag `X` and pushes it.
3. Builds the package tarball and (via `--push-tarball`) scp's it to the ICM
   outgoing FTP — verified to install under an old Python 2.7 pip.

### Deploy to production
```bash
# pull django_data_replication-X.tar.gz from ICM onto the server, then in the
# icm_ipcentral venv:
pip install --upgrade django_data_replication-X.tar.gz
# restart the celery workers so they load the new code:
#   (e.g. supervisorctl restart <celery worker group>)
```

## Testing

Python 2.7 + Django 1.11, via `manage.py test` against the never-shipped
`demo_app/` project:
```bash
python2.7 -m virtualenv .venv
.venv/bin/pip install -r requirements-test.txt   # pinned py2.7-safe versions
.venv/bin/python demo_app/manage.py test data_replication --settings=demo_app.settings_test
# or: make test
```
Tests live in `data_replication/tests/` (in-memory sqlite; Mongo/Splunk mocked).

## Conventions

- **Python 2.7 only** on this branch.
- The releaser's `pre_file_check` requires every `.py` file to carry a
  `# -*- coding: utf-8 -*-` pragma, `from __future__ import unicode_literals`, and a
  `Copyright 2011-<year>` copyright. Keep new files compliant or the release will fail.