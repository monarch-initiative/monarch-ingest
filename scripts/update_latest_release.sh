#!/bin/bash

# This script will push a local copy of the Solr, Sqlite and denormalized edge artifacts up to all
# all copies of the bucket for a given release. It needs to be run from the root of the repo

echo "Updating Solr, SQLite and denormalized edge files for $RELEASE"

gsutil -q -m cp -r output/* gs://monarch-archive/monarch-kg-dev/$RELEASE/

# if RELEASE == LATEST_RELEASE, copy all of this release to latest
export LATEST_RELEASE=$(gsutil ls gs://data-public-monarchinitiative/monarch-kg-dev/latest/ | grep -o '[0-9]\{4\}-[0-9]\{2\}-[0-9]\{2\}')
if [ "$RELEASE" == "$LATEST_RELEASE" ]; then
    gsutil -q -m cp -r "gs://monarch-archive/monarch-kg-dev/$RELEASE/*" gs://data-public-monarchinitiative/monarch-kg-dev/latest/
fi