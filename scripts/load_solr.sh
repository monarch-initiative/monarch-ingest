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
# monarch-app's model.yaml is still used for the Mapping (sssom) core, but
# the Entity and Association core schemas now come from the koza-produced
# monarch-kg-schema.yaml that closurize emits alongside output/monarch-kg.duckdb.
python -c "from monarch_ingest.cli_utils import ensure_model_files; ensure_model_files()"

if ! test -f "output/monarch-kg-schema.yaml"; then
    echo "ERROR: output/monarch-kg-schema.yaml not found. Run \`ingest merge\` + \`ingest closure\` first."
    exit 1
fi

echo "Starting the server"
# Tunables — override via env to size Solr per host.
# Defaults are sized for a laptop with ~16 GB RAM; bump on bigger machines.
: "${SOLR_MEMORY:=12g}"
: "${SOLR_HEAP_SIZE:=10g}"
: "${SOLR_RAM_BUFFER_MB:=2048}"
uv run lsolr start-server \
  --memory "$SOLR_MEMORY" \
  --heap-size "$SOLR_HEAP_SIZE" \
  --ram-buffer-mb "$SOLR_RAM_BUFFER_MB"
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
uv run lsolr add-cores entity association sssom infores
sleep 30

# todo: ideally, this will live in linkml-solr
echo "Adding additional fieldtypes"
scripts/add_fieldtypes.sh
sleep 5

echo "Adding entity schema (from koza-produced monarch-kg-schema.yaml)"
uv run lsolr create-schema -C entity -s output/monarch-kg-schema.yaml -t Entity
sleep 5

echo "Adding association schema (from koza-produced monarch-kg-schema.yaml)"
uv run lsolr create-schema -C association -s output/monarch-kg-schema.yaml -t Association
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
uv run lsolr create-schema -C sssom -s model.yaml -t Mapping
sleep 5

echo "Adding infores schema"
uv run lsolr create-schema -C infores -s data/infores/information_resource_registry.yaml -t InformationResource

# todo: this also should live in linkml-solr, and copy-fields should be based on the schema
echo "Add dynamic fields and copy fields declarations"
scripts/add_entity_copyfields.sh
scripts/add_association_copyfields.sh
sleep 5

echo "Load infores"

# load directly to avoid linkml-solr's unhappiness with jsonl loading
curl -X POST -H 'Content-Type: application/json' \
  'http://localhost:8983/solr/infores/update/json/docs?commit=true' \
  --data-binary @data/infores/infores_catalog.jsonl


uv run lsolr bulkload-db -C sssom -s model.yaml output/monarch-kg.duckdb mappings

# Materialize the edges with `frequency_computed_sortable_float` — the
# derived field the Solr UI sorts on to rank phenotypes by prevalence.
# Previously this was set by a per-doc StatelessScriptUpdateProcessorFactory
# (Nashorn JS) on the association core, which dominated load time. Doing it
# once, vectorised in DuckDB, lets the edges load run substantially faster.
# Mapping mirrors HPO's frequency sub-ontology (HP:0040280..HP:0040285) and
# matches the legacy JS processor's outputs; rows with neither `has_quotient`
# nor a known `frequency_qualifier` get 0.0, same as before.
echo "Materializing edges with frequency_computed_sortable_float..."
uv run python -c "
import duckdb
db = duckdb.connect('output/monarch-kg.duckdb')
db.execute('''
    CREATE OR REPLACE TABLE _solr_edges AS
    SELECT *,
           CASE
             WHEN has_quotient IS NOT NULL THEN CAST(has_quotient AS DOUBLE)
             WHEN frequency_qualifier = 'HP:0040280' THEN 1.0
             WHEN frequency_qualifier = 'HP:0040281' THEN 0.8
             WHEN frequency_qualifier = 'HP:0040282' THEN 0.3
             WHEN frequency_qualifier = 'HP:0040283' THEN 0.05
             WHEN frequency_qualifier = 'HP:0040284' THEN 0.01
             WHEN frequency_qualifier = 'HP:0040285' THEN 0.0
             ELSE 0.0
           END AS frequency_computed_sortable_float
    FROM denormalized_edges
''')
print('Done.')
"

echo "Loading entities"

uv run lsolr bulkload-db -C entity -s output/monarch-kg-schema.yaml output/monarch-kg.duckdb denormalized_nodes

uv run lsolr bulkload-db -C association -s output/monarch-kg-schema.yaml output/monarch-kg.duckdb _solr_edges
# curl "http://localhost:8983/solr/association/select?q=*:*"



# Commit pending writes on every core, then stop Solr cleanly so the
# index isn't being mutated while we tar it. Without this, GNU tar
# bails with "file changed as we read it" when Solr merges a segment
# mid-archive (jenkins parallel-processing surfaced the race).
for core in entity association sssom infores; do
  curl -s "http://localhost:8983/solr/$core/update?commit=true&waitSearcher=true" \
    -H "Content-type: text/xml" --data-binary '' >/dev/null || true
done

# The tarball is the release artifact Jenkins publishes; for local runs we
# usually just want the live container to query against, and producing the
# ~30 GB tar adds minutes for no benefit. Set SOLR_SKIP_TARBALL=1 to skip
# the tar step (and leave the container running so it stays queryable).
if [ "${SOLR_SKIP_TARBALL:-0}" = "1" ]; then
  echo "SOLR_SKIP_TARBALL=1 — leaving my_solr running, skipping output/solr.tar.gz"
else
  docker stop my_solr

  # Tar from a sidecar that mounts the stopped container's volumes — the
  # index is now quiet on disk.
  docker run --rm --volumes-from my_solr busybox \
    tar czf - -C /var/solr data > output/solr.tar.gz

  docker rm my_solr
fi

