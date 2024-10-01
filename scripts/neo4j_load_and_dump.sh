#!/bin/sh

neo4j-admin database import full --array-delimiter="|" --overwrite-destination=true --nodes=/import/monarch-kg_nodes.neo4j.csv --relationships=/import/monarch-kg_edges.neo4j.csv
neo4j-admin database dump  --to-path=/import neo4j
mv /import/neo4j.dump /import/monarch-kg.neo4j.dump