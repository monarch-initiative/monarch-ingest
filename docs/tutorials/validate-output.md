### KGX: Validate and add to merge config

Run the transform to produce KGX files
```bash
poetry run koza transform --source monarch_ingest/alliance/gene2phenotype.yaml 
 ```

Validate the output with kgx
```bash
poetry run kgx validate -i tsv output/somethingbase_gene_to_disease_nodes.tsv output/somethingbase_gene_to_disease_edges.tsv
```

Finally, add the node and edge files to `merge.yaml` at the root of the project

### Next

Maybe double check that documentation one last time.
