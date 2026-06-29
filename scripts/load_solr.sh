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

# No schema is downloaded from monarch-app anymore. All core schemas come from
# the ingest side:
#   - entity / association : the koza-produced output/monarch-kg-schema.yaml
#     (closurize emits it alongside output/monarch-kg.duckdb)
#   - sssom (Mapping)      : the canonical SSSOM schema shipped by the installed
#     sssom-schema package (the mappings ARE SSSOM, unrelated to the KG schema)
#   - infores             : data/infores/information_resource_registry.yaml
echo "Resolving the SSSOM schema from the installed sssom-schema package"
SSSOM_SCHEMA=$(uv run python -c "import sssom_schema, pathlib; print(pathlib.Path(sssom_schema.__file__).parent / 'schema' / 'sssom_schema.yaml')")
echo "SSSOM schema: $SSSOM_SCHEMA"

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
uv run lsolr create-schema -C sssom -s "$SSSOM_SCHEMA" -t mapping
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


uv run lsolr bulkload-db -C sssom -s "$SSSOM_SCHEMA" output/monarch-kg.duckdb mappings

# `_solr_edges` (denormalized_edges + frequency_computed_sortable_float) is
# materialized by `ingest prepare-solr`, run sequentially before this stage,
# so we open the duckdb strictly read-only here — necessary because the
# Jenkinsfile fans this stage out in parallel with kgx-graph-summary /
# connectivity-report / kgx-transforms / neo4j-dump / sqlite, which would all
# race on the file lock otherwise. Fail loud if the precondition isn't met.
echo "Verifying _solr_edges was materialized by prepare-solr..."
uv run python -c "
import duckdb, sys
con = duckdb.connect('output/monarch-kg.duckdb', read_only=True)
rows = con.execute(\"SELECT 1 FROM information_schema.tables WHERE table_name='_solr_edges'\").fetchall()
if not rows:
    sys.exit('ERROR: _solr_edges not found - run \\\"ingest prepare-solr\\\" first.')
print('_solr_edges present.')
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

# Post-load verification (defense in depth). The bulk loader now fails loud on
# dropped chunks, but a silently short index is the single worst release defect
# we can ship — build #328 published a half-empty entity core that still passed
# as SUCCESS. So independently assert each big core's committed numDocs equals
# the count of distinct ids in its source table, and abort the release if not.
echo "Verifying Solr core doc counts against source tables..."
uv run python - <<'PYEOF'
import sys
import duckdb
import requests

DB = "output/monarch-kg.duckdb"
# core -> source table feeding it (Solr dedupes by id, so the expected number of
# indexed docs is the count of DISTINCT ids in the source).
CHECKS = {
    "entity": "denormalized_nodes",
    "association": "_solr_edges",
}

con = duckdb.connect(DB, read_only=True)
failures = []
for core, table in CHECKS.items():
    expected = con.execute(f"SELECT count(DISTINCT id) FROM {table}").fetchone()[0]
    resp = requests.get(
        f"http://localhost:8983/solr/{core}/select",
        params={"q": "*:*", "rows": 0},
        timeout=60,
    )
    resp.raise_for_status()
    got = resp.json()["response"]["numFound"]
    status = "OK" if got == expected else "MISMATCH"
    print(f"  {core}: numDocs={got:,} expected={expected:,} ({status})")
    if got != expected:
        failures.append(f"{core}: {got} indexed != {expected} expected ({table})")

if failures:
    sys.exit("ERROR: Solr load incomplete:\n  - " + "\n  - ".join(failures))
print("All core doc counts match source tables.")
PYEOF

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

