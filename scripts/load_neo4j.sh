#!/bin/bash

echo "Building Neo4j Artifacts"

# Decompress the gzipped CSV files for import
echo "Decompressing Neo4j CSV files..."
gunzip -k output/monarch-kg_nodes.neo4j.csv.gz
gunzip -k output/monarch-kg_edges.neo4j.csv.gz

# Neo4j v4 dump
echo "Building Neo4j v4 dump..."
mkdir -p neo4j_data_v4
rm -rf neo4j_data_v4/*
rm -f output/monarch-kg.neo4j.dump

docker run --rm \
  -v $(pwd)/output:/import \
  -v $(pwd)/neo4j_data_v4:/data \
  neo4j:4.4 \
  neo4j-admin import \
  --force \
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
mkdir -p neo4j_data_v5
rm -rf neo4j_data_v5/*
rm -f output/monarch-kg.neo4j.v5.dump

docker run --rm \
  -v $(pwd)/output:/import \
  -v $(pwd)/neo4j_data_v5:/data \
  neo4j:5 \
  neo4j-admin database import full \
  --overwrite-destination=true \
  --nodes=/import/monarch-kg_nodes.neo4j.csv \
  --relationships=/import/monarch-kg_edges.neo4j.csv

docker run --rm \
  -v $(pwd)/output:/dump \
  -v $(pwd)/neo4j_data_v5:/data \
  --entrypoint neo4j-admin \
  neo4j:5 database dump --to-path=/dump neo4j

mv output/neo4j.dump output/monarch-kg.neo4j.v5.dump

# Clean up uncompressed CSV files (gzipped versions remain for upload)
echo "Cleaning up uncompressed CSV files..."
rm -f output/monarch-kg_nodes.neo4j.csv
rm -f output/monarch-kg_edges.neo4j.csv

echo "Done building Neo4j artifacts"
