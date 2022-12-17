#!/bin/bash

command -v curl >/dev/null 2>&1 || { echo >&2 "We require 'curl' but it's not installed.  Aborting."; exit 1; }

# 'Latest' Monarch Neo4j Dump file
NEO4J_DUMP_FILENAME=${1:-monarch-kg.neo4j.dump}
NEO4J_DUMP_DIRECTORY=${2:-https://data.monarchinitiative.org/monarch-kg-dev/latest}
NEO4J_DUMP=$NEO4J_DUMP_DIRECTORY/$NEO4J_DUMP_FILENAME

echo "Downloading '$NEO4J_DUMP'"; cd ../dumps; curl $NEO4J_DUMP --output $NEO4J_DUMP_FILENAME
