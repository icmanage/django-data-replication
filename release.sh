#!/usr/bin/env bash
#
# Release django-data-replication via the shared ../releaser tool -- the same
# mechanism ip_verification uses. The releaser bumps setup.py, creates the git
# release, and builds a tarball of the package. On prod it is installed with
#     pip install --upgrade <extracted-dir>/
#
# Requirements:
#   * Run from the repo root with the ../releaser checkout alongside it.
#   * ICM VPN connectivity (the releaser checks internal FTP first).
#
# NOTE: the releaser only auto-creates a release on the `master` branch. This
# is the stable/1.0.x maintenance branch, so the version MUST be passed
# explicitly:
#
#     ./release.sh 1.0.4
#

LABEL=data_replication

# Load build-time environment (e.g. P4USER / P4PORT / P4CLIENT).
if [ -f .env ]; then
    export $(grep -v '^#' .env | xargs)
fi

# Activate the venv that carries the releaser's dependencies.
source ../icm_ipcatalog/.venv/bin/activate

RELEASE_ARG=""
if [ -n "$1" ]; then
    RELEASE_ARG="--release=$1"
else
    echo "WARNING: no version given. On stable/1.0.x the releaser will NOT"
    echo "         create a release unless you pass one, e.g. ./release.sh 1.0.4"
fi

python ../releaser/release.py \
    --label=${LABEL} \
    --env=.env \
    --verbose 3 \
    ${RELEASE_ARG}

if [ $? -eq 0 ]; then
    echo ""
    echo "Build ${LABEL} completed"
    echo ""
else
    echo ""
    echo "Build ${LABEL} failed"
    exit 1
fi
