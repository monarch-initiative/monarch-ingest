#!/bin/bash

# This script will push a local copy of the Solr, Sqlite and denormalized edge artifacts up to all
# all copies of the bucket for a given release. It needs to be run from the root of the repo

export RELEASE=$(gsutil ls gs://data-public-monarchinitiative/monarch-kg-dev/latest/ | grep -o '[0-9]\{4\}-[0-9]\{2\}-[0-9]\{2\}')
echo "Updating Solr, SQLite and denormalized edge files for $RELEASE"

gsutil cp output/monarch-kg.db.gz gs://monarch-archive/monarch-kg-dev/$RELEASE/
gsutil cp output/monarch-kg-denormalized-edges.tsv.gz gs://monarch-archive/monarch-kg-dev/$RELEASE/
gsutil cp output/solr.tar.gz gs://monarch-archive/monarch-kg-dev/$RELEASE/

gsutil cp "gs://monarch-archive/monarch-kg-dev/$RELEASE/*.gz" gs://data-public-monarchinitiative/monarch-kg-dev/$RELEASE/
gsutil cp "gs://monarch-archive/monarch-kg-dev/$RELEASE/*.gz" gs://data-public-monarchinitiative/monarch-kg-dev/latest/
