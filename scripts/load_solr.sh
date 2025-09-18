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

echo "Download the schema files using pystow"
python -c "from monarch_ingest.cli_utils import ensure_model_files; ensure_model_files()"

echo "Starting the server"
poetry run lsolr start-server --memory 8g --heap-size 6g --ram-buffer-mb 2048
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

# turn off transaction logging for the big indexes
core_names=(entity association)
for core_name in "${core_names[@]}"; do
  curl -X POST "http://localhost:8983/solr/$core_name/config" \
    -H "Content-type: application/json" \
    -d '{
      "set-property": {
        "updateLog.numRecordsToKeep": 0
      }
    }'
  curl "http://localhost:8983/solr/admin/cores?action=RELOAD&core=$core_name"
done

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


poetry run lsolr bulkload-db -C sssom -s model.yaml output/monarch-kg.duckdb mappings

echo "Loading entities"

poetry run lsolr bulkload-db -C entity -s model.yaml output/monarch-kg.duckdb denormalized_nodes

poetry run lsolr bulkload-db -C association -s model.yaml --processor frequency_update_processor output/monarch-kg.duckdb denormalized_edges
# curl "http://localhost:8983/solr/association/select?q=*:*"



# For now, just leaving solr running. It will go away on it's own in the jenkins builder
# and otherwise that makes this script a nice way to just run solr locally
# docker stop my_solr
# docker rm my_solr

docker exec my_solr tar czf - -C /var/solr data > output/solr.tar.gz

