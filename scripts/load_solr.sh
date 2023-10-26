#!/bin/bash

docker stop my_solr || true
docker rm my_solr || true

if test -f "output/monarch-kg.tar.gz"; then
    tar zxf output/monarch-kg.tar.gz -C output
fi

if test -f "output/monarch-kg-denormalized-edges.tsv.gz"; then
    gunzip --force output/monarch-kg-denormalized-edges.tsv.gz
fi

echo "Download the schema from monarch-py"
# This replaces poetry run monarch schema > model.yaml

# temporarily retrieve from a branch that has the sssom changes

curl -O https://raw.githubusercontent.com/monarch-initiative/monarch-app/schema-sssom-and-grouping/backend/src/monarch_py/datamodels/model.yaml
#curl -O https://raw.githubusercontent.com/monarch-initiative/monarch-app/v0.15.8/backend/src/monarch_py/datamodels/model.yaml
curl -O https://raw.githubusercontent.com/monarch-initiative/monarch-app/v0.15.8/backend/src/monarch_py/datamodels/similarity.yaml

echo "Starting the server"
poetry run lsolr start-server
sleep 30

echo "Adding cores"
poetry run lsolr add-cores entity association sssom
sleep 10

# todo: ideally, this will live in linkml-solr
echo "Adding additional fieldtypes"
scripts/add_fieldtypes.sh
sleep 5

echo "Adding entity schema"
poetry run lsolr create-schema -C entity -s model.yaml -t Entity
sleep 5

echo "Adding association schema"
poetry run lsolr create-schema -C association -s model.yaml -t Association
sleep 5

echo "Adding sssom schema"
poetry run lsolr create-schema -C sssom -s model.yaml -t Mapping
sleep 5

# todo: this also should live in linkml-solr, and copy-fields should be based on the schema
echo "Add dynamic fields and copy fields declarations"
scripts/add_entity_copyfields.sh
scripts/add_association_copyfields.sh
sleep 5

# todo: this should probably happen after associations, but putting it first for testing
echo "Loading SSSOM mappings"
grep -v "^#" data/monarch/mondo.sssom.tsv > headless.mondo.sssom.tsv
# todo: copy the mappings to output/mappings as part of an earlier step
poetry run lsolr bulkload -C sssom -s model.yaml headless.mondo.sssom.tsv
poetry run lsolr bulkload -C sssom -s model.yaml data/monarch/gene_mappings.tsv
poetry run lsolr bulkload -C sssom -s model.yaml data/monarch/chebi-mesh.biomappings.sssom.tsv

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
gzip --force output/monarch-kg-denormalized-edges.tsv
