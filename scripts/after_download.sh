#!/bin/sh

# Make a simple text file of all the gene IDs in Alliance
zcat data/alliance/BGI_*.gz | jq '.data[].basicGeneticEntity.primaryId' | gzip > data/alliance/alliance_gene_ids.txt.gz

# Make an id, name map of DDPHENO terms
sqlite3 -cmd ".mode tabs" -cmd ".headers on" data/dictybase/ddpheno.db "select subject as id, value as name from rdfs_label_statement where predicate = 'rdfs:label' and subject like 'DDPHENO:%'" > data/dictybase/ddpheno.tsv

# Unpack the phenio relation graph file
tar -xzf data/monarch/phenio-relation-graph.tar.gz -C data/monarch/

awk '{ if ($2 == "rdfs:subClassOf" || $2 == "BFO:0000050" || $2 == "UPHENO:0000001") { print } }' data/monarch/phenio-relation-graph.tsv > data/monarch/phenio-relation-filtered.tsv
