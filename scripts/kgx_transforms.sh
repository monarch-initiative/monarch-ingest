#!/bin/bash

echo "kgx transform to jsonl"
# poetry run kgx transform -i tsv -c tar.gz -f jsonl -d tar.gz -o output/monarch-kg.jsonl.tar.gz output/monarch-kg.tar.gz
poetry run kgx transform -i tsv -c tar.gz -f jsonl -o output/monarch-kg output/monarch-kg.tar.gz
# create tar archive named output/monarch-kg.json.tar.gz that includes output/monarch-kg_nodes.jsonl and output/monarch-kg_edges.jsonl
tar -C output -czvf monarch-kg.jsonl.tar.gz monarch-kg_nodes.jsonl monarch-kg_edges.jsonl


rm output/monarch-kg_edges.jsonl
rm output/monarch-kg_nodes.jsonl
echo "kgx transform to rdf"
poetry run kgx transform -i tsv -c tar.gz -f nt -d gz -o output/monarch-kg.nt.gz output/monarch-kg.tar.gz


echo "Building Neo4j Artifact"
docker rm -f neo || True
mkdir neo4j-v4-data
docker run -d --name neo -p7474:7474 -p7687:7687 -v neo4j-v4-data:/data --env NEO4J_AUTH=neo4j/admin neo4j:4.4
poetry run kgx transform --stream --transform-config neo4j-transform.yaml > kgx-transform.log
docker stop neo
docker run -v $(pwd)/output:/backup -v neo4j-v4-data:/data --entrypoint neo4j-admin neo4j:4.4 dump --to /backup/monarch-kg.neo4j.dump
