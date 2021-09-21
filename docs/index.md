## Monarch Ingest

The Monarch Ingest generates [KGX](https://github.com/biolink/kgx/blob/master/specification/kgx-format.md) formatted files conforming to the [BioLink Model](https://biolink.github.io/biolink-model/) from a wide variety of biomedical data sources. 


### Kozathon

[Get set up for Kozathon](kozathon/setup.md)

### Getting Started

First, clone the repository

```bash
gh repo clone monarch-initiative/monarch-ingest && cd monarch-ingest
```

The Monarch Ingest is built using [Poetry](https://python-poetry.org), which will create its own virtual environment. 

```bash
make all
```

This will install Poetry, create the virtual environment and fetch dependencies.

### Downloading data

Using the Google Cloud cli you can download the whole data bucket

```bash
gsutil -m cp -R gs://monarch-ingest/data .
```

### Running an ingest

```bash
poetry run koza transform --global-table monarch_ingest/translation_table.yaml --source monarch_ingest/alliance/metadata.yaml --output-format tsv  
```

### Validate the output

```bash
poetry run kgx validate -i tsv output/Alliance.gene-to-phenotype_nodes.tsv output/Alliance.gene-to-phenotype_edges.tsv 
```

### Running all transforms

```bash
make transform
```

### KGX Merge

To merge all of the transformed files with ontologies into a single pair of node and edge files

```bash
make merge
```

### TLDR

If you want to generate it all as `output/merged/monarch-kg.tar.gz`

```bash
make download transform merge
```
