#!/bin/bash

set -e


docker stop my_solr || true
docker rm my_solr || true

if test -f "output/monarch-kg-denormalized-edges.tsv.gz"; then
    gunzip --force output/monarch-kg-denormalized-edges.tsv.gz
fi

if test -f "output/monarch-kg-denormalized-nodes.tsv.gz"; then
    gunzip --force output/monarch-kg-denormalized-nodes.tsv.gz
fi

echo "Download the schema from monarch-py"
# This replaces poetry run monarch schema > model.yaml and just awkwardly pulls from a github raw link

# retrieve the schema from the main branch on monarch-app

curl -O https://raw.githubusercontent.com/monarch-initiative/monarch-app/main/backend/src/monarch_py/datamodels/model.yaml
curl -O https://raw.githubusercontent.com/monarch-initiative/monarch-app/main/backend/src/monarch_py/datamodels/similarity.yaml

echo "Starting the server"
poetry run lsolr start-server

echo "Waiting for Solr to be ready..."
for i in {1..30}; do
  if curl -s http://localhost:8983/solr/admin/info/system >/dev/null 2>&1; then
    echo "Solr is ready!"
    break
  fi
  echo "Waiting for Solr... ($((i*5))/150 seconds)"
  sleep 5
done

if ! curl -s http://localhost:8983/solr/admin/info/system >/dev/null 2>&1; then
  echo "Solr failed to start within 150 seconds"
  exit 1
fi

echo "Adding cores"
poetry run lsolr add-cores entity association sssom infores
sleep 30

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

echo "Adding infores schema"
poetry run lsolr create-schema -C infores -s data/infores/information_resource_registry.yaml -t InformationResource

# todo: this also should live in linkml-solr, and copy-fields should be based on the schema
echo "Add dynamic fields and copy fields declarations"
scripts/add_entity_copyfields.sh
scripts/add_association_copyfields.sh
sleep 5

echo "Adding update processor for phenotype frequency to association core"
scripts/add_update_processor.sh

echo "Load infores"

# load directly to avoid linkml-solr's unhappiness with jsonl loading
curl -X POST -H 'Content-Type: application/json' \
  'http://localhost:8983/solr/infores/update/json/docs?commit=true' \
  --data-binary @data/infores/infores_catalog.jsonl

# todo: this should probably happen after associations, but putting it first for testing
echo "Loading SSSOM mappings"
grep -v "^#" data/monarch/mondo.sssom.tsv > headless.mondo.sssom.tsv
grep -v "^#" data/monarch/gene_mappings.sssom.tsv > headless.gene_mappings.sssom.tsv
grep -v "^#" data/monarch/mesh_chebi_biomappings.sssom.tsv > headless.mesh_chebi_biomappings.sssom.tsv
# todo: copy the mappings to output/mappings as part of an earlier step
poetry run lsolr bulkload -C sssom -s model.yaml headless.mondo.sssom.tsv
poetry run lsolr bulkload -C sssom -s model.yaml headless.gene_mappings.sssom.tsv
poetry run lsolr bulkload -C sssom -s model.yaml headless.mesh_chebi_biomappings.sssom.tsv

echo "Loading entities"
poetry run lsolr bulkload -C entity -s model.yaml output/monarch-kg-denormalized-nodes.tsv

poetry run lsolr bulkload -C association -s model.yaml --processor frequency_update_processor output/monarch-kg-denormalized-edges.tsv
curl "http://localhost:8983/solr/association/select?q=*:*"

mkdir solr-data || true

docker cp -q my_solr:/var/solr/data solr-data/

# make sure it's readable by all in the tar file
chmod -R a+rX solr-data

# For now, just leaving solr running. It will go away on it's own in the jenkins builder
# and otherwise that makes this script a nice way to just run solr locally
# docker stop my_solr
# docker rm my_solr

tar czf solr.tar.gz -C solr-data data
mv solr.tar.gz output/

