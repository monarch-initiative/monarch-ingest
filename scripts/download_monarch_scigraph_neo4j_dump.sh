#!/bin/bash

command -v curl >/dev/null 2>&1 || { echo >&2 "We require 'curl' but it's not installed.  Aborting."; exit 1; }

# scigraph.tgz
#    Neo4J data dump for the Monarch SciGraph database.
#    See https://github.com/SciGraph/SciGraph/wiki
NEO4J_DUMP=${1:-https://data.monarchinitiative.org/latest/scigraph.tgz}

echo "Downloading '$NEO4J_DUMP'"
cd ../dumps; curl $NEO4J_DUMP --output neo4j_dump.tgz
