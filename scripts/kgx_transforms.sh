#!/bin/bash

#echo "kgx transform to rdf"
#poetry run kgx transform -i tsv -c tar.gz -f nt -d gz -o output/monarch-kg.nt.gz output/monarch-kg.tar.gz
#
#echo "Building Neo4j 4 Artifact"
#docker rm -f neo4 || True
#mkdir neo4j-v4-data || True
#docker run -d --name neo4 -p7474:7474 -p7687:7687 -v neo4j-v4-data:/data --env NEO4J_AUTH=neo4j/admin neo4j:4.4
#poetry run kgx transform --transform-config neo4j-transform.yaml > neo4j-v4-load.log
#docker stop neo4
#docker run -v $(pwd)/output:/backup -v neo4j-v4-data:/data --entrypoint neo4j-admin neo4j:4.4 dump --to /backup/monarch-kg.neo4j.dump

echo "Building Neo4j 5 Artifact"
docker rm -f neo5 || True
docker volume rm neo4j-v5-data || True
mkdir neo4j-v5-data || True
rm -rf neo4j-v5-data || True
docker run --rm --name neo5  -v $(pwd)/scripts:/scripts -v $(pwd)/neo4j-v5-data:/data -v $(pwd)/output:/import -v $(pwd)/output:/backup neo4j:5.2 /scripts/neo4j_load_and_dump.sh
