## Kozathon

### Setup

First, clone the repository

```bash
git clone https://github.com/monarch-initiative/monarch-ingest.git && cd monarch-ingest
```

The Monarch Ingest is built using [Poetry](https://python-poetry.org), which will create its own virtual environment.

```bash
make all
```

This will install Poetry, create the virtual environment and fetch dependencies.

### Downloading data

Download the PomBase data

```bash
poetry run downloader --tag pombase_gene_to_phenotype
```

### Make sure the PomBase ingest is working

```bash
poetry run koza transform --source monarch_ingest/pombase/gene_to_phenotype.yaml --row-limit 1000
```

### Validate the output*

```bash
poetry run kgx validate -i tsv output/pombase_gene_to_phenotype_nodes.tsv output/pombase_gene_to_phenotype_edges.tsv 
```

### 👍 You're ready for Kozathon

In the meantime, [check out the tutorial](../tutorials/configure-ingest.md)
