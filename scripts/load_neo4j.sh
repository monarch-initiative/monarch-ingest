#!/bin/bash

echo "Building Neo4j Artifact"

mkdir neo4j_data || True
rm -rf neo4j_data/* || True
rm -rf output/monarch-kg.neo4j.dump || True


docker run --rm \
  -v $(pwd)/output:/import \
  -v $(pwd)/neo4j_data:/data \
  neo4j:4.4 \
  neo4j-admin import \
  --force \
  --database=neo4j \
  --nodes=/import/monarch-kg_nodes.neo4j.csv \
  --relationships=/import/monarch-kg_edges.neo4j.csv

docker run -v $(pwd)/output:/backup -v neo4j_data:/data --entrypoint neo4j-admin neo4j:4.4 dump --to /backup/monarch-kg.neo4j.dump
