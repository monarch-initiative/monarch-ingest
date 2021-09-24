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

Download data files for our demo ingests. PomBase's phenotype annotations, a mini-StringDB file, and the HPOA file.

```bash
#Assuming you are still in monarch-ingest dir
mkdir -p data
cd data
curl -OJ https://www.pombase.org/data/annotations/Phenotype_annotations/phenotype_annotations.pombase.phaf.gz
curl -OJ https://raw.githubusercontent.com/monarch-initiative/koza/main/tests/resources/source-files/string.tsv
curl -OJ http://purl.obolibrary.org/obo/hp/hpoa/phenotype.hpoa
cd ..
```

### Make sure the PomBase ingest is working

```bash
poetry run koza transform --global-table monarch_ingest/translation_table.yaml --source monarch_ingest/pombase/metadata.yaml --output-format tsv  
```

### Validate the output*

```bash
poetry run kgx validate -i tsv output/PomBase.gene-to-phenotype_nodes.tsv output/PomBase.gene-to-phenotype_edges.tsv 
```

### 👍 You're ready for Kozathon

In the meantime, [check out the tutorial](../tutorials/configure-ingest.md)
