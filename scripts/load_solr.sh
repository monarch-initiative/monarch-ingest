#!/bin/bash

docker stop my_solr || true
docker rm my_solr || true

if test -f "output/monarch-kg.tar.gz"; then
    tar zxf output/monarch-kg.tar.gz -C output
fi

if test -f "output/monarch-kg-denormalized-edges.tsv.gz"; then
    gunzip output/monarch-kg-denormalized-edges.tsv.gz
fi

echo "Extracting the schema from monarch-py"
poetry run monarch schema > model.yaml

echo "Starting the server"
poetry run lsolr start-server
sleep 30

echo "Adding cores"
poetry run lsolr add-cores entity association
sleep 10

# todo: ideally, this will live in linkml-solr
echo "Adding additional fieldtypes"
scripts/add_entity_fieldtypes.sh
sleep 5

echo "Adding entity schema"
poetry run lsolr create-schema -C entity -s model.yaml -t Entity
sleep 5

echo "Adding association schema"
poetry run lsolr create-schema -C association -s model.yaml -t Association
sleep 5

# todo: this also should live in linkml-solr, and copy-fields should be based on the schema
echo "Add dynamic fields and copy fields declarations"
scripts/add_entity_copyfields.sh
sleep 5

echo "Loading entities"
poetry run lsolr bulkload -C entity -s model.yaml output/monarch-kg_nodes.tsv

echo "Loading associations"
poetry run lsolr bulkload -C association -s model.yaml output/monarch-kg-denormalized-edges.tsv
curl "http://localhost:8983/solr/association/select?q=*:*"

mkdir solr-data || true

docker cp my_solr:/var/solr/data solr-data/

# make sure it's readable by all in the tar file
chmod -R a+rX solr-data

# For now, just leaving solr running. It will go away on it's own in the jenkins builder
# and otherwise that makes this script a nice way to just run solr locally
# docker stop my_solr
# docker rm my_solr

tar czf solr.tar.gz -C solr-data data
mv solr.tar.gz output/
gzip output/monarch-kg-denormalized-edges.tsv 
