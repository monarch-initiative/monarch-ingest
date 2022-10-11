#!/bin/bash

rm output/monarch-kg.db || true
echo "Decompressing tsv files..."
tar zxf output/monarch-kg.tar.gz -C output
gunzip output/qc/monarch-kg-dangling-edges.tsv.gz

echo "Loading nodes..."
sqlite3 -cmd ".mode tabs" output/monarch-kg.db ".import output/monarch-kg_nodes.tsv nodes"
echo "Loading edges..."
sqlite3 -cmd ".mode tabs" output/monarch-kg.db ".import output/monarch-kg_edges.tsv edges"
echo "Loading dangling edges..."
sqlite3 -cmd ".mode tabs" output/monarch-kg.db ".import output/qc/monarch-kg-dangling-edges.tsv dangling_edges"

echo "Cleaning up..."
rm output/monarch-kg_*.tsv
gzip output/qc/monarch-kg-dangling-edges.tsv

echo "Compressing database"
gzip output/monarch-kg.db