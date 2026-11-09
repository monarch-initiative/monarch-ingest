#!/bin/bash
# Fail on the first error: a failed import otherwise falls through to a dump of
# a half-built store and the script still exits 0, so the release ships without
# dumps and nothing turns red.
set -euo pipefail

# Some text fields (MeDIC supporting_text) contain newlines. The CSV quotes them,
# but neo4j-admin rejects multi-line fields unless --multiline-fields=true.

# The neo4j containers chown their /data mount to the neo4j user, so a previous
# run's store can't be removed from the host; clear it from inside a container.
clear_data_dir() {
  mkdir -p "$1"
  docker run --rm --user root -v "$(pwd)/$1":/data --entrypoint sh "$2" -c 'rm -rf /data/*'
}

echo "Building Neo4j Artifacts"

# Neo4j v4 dump
echo "Building Neo4j v4 dump..."
clear_data_dir neo4j_data_v4 neo4j:4.4
rm -f output/monarch-kg.neo4j.dump

docker run --rm \
  -v $(pwd)/output:/import \
  -v $(pwd)/neo4j_data_v4:/data \
  neo4j:4.4 \
  neo4j-admin import \
  --force \
  --multiline-fields=true \
  --database=neo4j \
  --nodes=/import/monarch-kg_nodes.neo4j.csv \
  --relationships=/import/monarch-kg_edges.neo4j.csv

docker run --rm \
  -v $(pwd)/output:/backup \
  -v $(pwd)/neo4j_data_v4:/data \
  --entrypoint neo4j-admin \
  neo4j:4.4 dump --to /backup/monarch-kg.neo4j.dump

# Neo4j v5 dump
echo "Building Neo4j v5 dump..."
clear_data_dir neo4j_data_v5 neo4j:5
rm -f output/monarch-kg.neo4j.v5.dump

docker run --rm \
  -v $(pwd)/output:/import \
  -v $(pwd)/neo4j_data_v5:/data \
  neo4j:5 \
  neo4j-admin database import full \
  --overwrite-destination=true \
  --multiline-fields=true \
  --nodes=/import/monarch-kg_nodes.neo4j.csv \
  --relationships=/import/monarch-kg_edges.neo4j.csv

docker run --rm \
  -v $(pwd)/output:/dump \
  -v $(pwd)/neo4j_data_v5:/data \
  --entrypoint neo4j-admin \
  neo4j:5 database dump --to-path=/dump neo4j

mv output/neo4j.dump output/monarch-kg.neo4j.v5.dump

echo "Done building Neo4j artifacts"
