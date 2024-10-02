#!/bin/sh

neo4j-admin database import full --array-delimiter="|" --overwrite-destination=true --nodes=/import/monarch-kg_nodes.neo4j.csv --relationships=/import/monarch-kg_edges.neo4j.csv
neo4j-admin database dump  --to-path=/dump neo4j
 mv /dump/neo4j.dump /dump/monarch-kg.neo4j.dump
