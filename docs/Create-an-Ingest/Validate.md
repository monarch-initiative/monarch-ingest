### KGX: Validate and add to merge config

1. Run the transform to produce KGX files:  
```
poetry run koza transform --source monarch_ingest/mgi/publication_to_gene.yaml
```

1. Validate the output with kgx:  
```bash
poetry run kgx validate -i tsv output/mgi_publication_to_gene_edges.tsv
```

1.  Finally, add the node and edge files to `merge.yaml` at the root of the project
