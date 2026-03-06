#!/bin/sh

echo "Running \"scripts/after_download.sh\"."

# set zcat to gzcat if gzcat is available
if command -v gzcat
then
    ZCAT=gzcat
else
    ZCAT=zcat
fi

# set sed command to gsed if gsed is available (a crutch for OSX)
if command -v gsed
then
    SED=gsed
else
    SED=sed
fi

if command -v python
then
    PYTHON=python
else
    PYTHON=python3
fi


if [ -f data/monarch/phenio-relation-graph.tsv.gz ]; then
  # Unpack the phenio relation graph file
  gunzip --force data/monarch/phenio-relation-graph.tsv.gz 
  awk '{ if ($2 == "rdfs:subClassOf" || $2 == "BFO:0000050" || $2 == "UPHENO:0000001") { print } }' data/monarch/phenio-relation-graph.tsv > data/monarch/phenio-relation-filtered.tsv
else
  echo "\"data/monarch/phenio-relation-graph.tsv.gz\" does not exist. Skipping creation of \"data/monarch/phenio-relation-filtered.tsv\"."
fi

if [ -f data/monarch/mondo.sssom.tsv ]; then
  # Repair Orphanet prefixes in MONDO sssom rows as necessary
  $SED -i 's/\torphanet.ordo\:/\tOrphanet\:/g' data/monarch/mondo.sssom.tsv
  # Repair mesh: prefixes in MONDO sssom rows as necessary
  $SED -i 's@mesh:@MESH:@g' data/monarch/mondo.sssom.tsv
else
  echo "\"data/monarch/mondo.sssom.tsv\" does not exist. Skipping it's repair."
fi

# python one-liner to covnert yaml to json for infores catalog, then extract ids 
$PYTHON -c "import yaml, json, sys; print(json.dumps(yaml.safe_load(sys.stdin)))" < data/infores/infores_catalog.yaml > data/infores/infores_catalog.json 
jq -r '.information_resources[].id' data/infores/infores_catalog.json > data/infores/infores_ids.txt



