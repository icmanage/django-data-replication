#!/usr/bin/env bash
#
# Release django-data-replication via the shared ../releaser tool -- the same
# mechanism ip_verification uses. The releaser bumps setup.py + the package
# __init__, creates the git release, and builds a tarball of the package. On
# prod it is installed with `pip install --upgrade <extracted-dir>/`.
#
# Requirements:
#   * Run from the repo root with the ../releaser checkout alongside it.
#   * ICM VPN connectivity.
#   * stable/1.0.x pushed to origin (the releaser tags against the remote).
#
# --force-micro keeps this maintenance branch inside the 1.0.x corridor
# (1.0.4, 1.0.5, ...) so a large changeset can never auto-roll into the
# already-published 1.1.x range. Being a non-master branch, the releaser will
# warn and ask you to confirm the release.
#
# Usage:
#   ./release.sh              # auto micro-bump from the latest tag, prompts to confirm
#   ./release.sh --dry-run    # preview the version + actions, change nothing
#   ./release.sh --release 1.0.7   # force a specific version
#   ./release.sh --noinput    # skip the branch confirmation prompt (automation)

LABEL=data_replication

# Load build-time environment (e.g. P4USER / P4PORT / P4CLIENT).
if [ -f .env ]; then
    export $(grep -v '^#' .env | xargs)
fi

# Activate the venv that carries the releaser's dependencies.
source ../icm_ipcatalog/.venv/bin/activate

python ../releaser/release.py \
    --label=${LABEL} \
    --env=.env \
    --verbose 3 \
    --force-micro \
    "$@"

if [ $? -eq 0 ]; then
    echo ""
    echo "Build ${LABEL} completed"
    echo ""
else
    echo ""
    echo "Build ${LABEL} failed"
    exit 1
fi