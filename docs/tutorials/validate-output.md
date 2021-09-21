### KGX: Validate and add to merge config

Run the transform to produce KGX files
```bash
poetry run koza transform --global-table monarch_ingest/translation_table.yaml --source monarch_ingest/alliance/metadata.yaml --output-format tsv
 ```

Validate the output with kgx
```bash
poetry run kgx validate -i tsv output/Somethingbase.gene-to-disease_nodes.tsv output/Somethingbase.gene-to-disease_edges.tsv
```

Finally, add the node and edge files to `merge.yaml` at the root of the project

### Next

Maybe double check that documentation one last time.
