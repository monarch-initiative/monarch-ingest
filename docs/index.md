# Monarch Ingest

## Overview

The Monarch Ingest generates [KGX](https://github.com/biolink/kgx/blob/master/specification/kgx-format.md) formatted files conforming to the [BioLink Model](https://biolink.github.io/biolink-model/) from a wide variety of biomedical data sources. 

The Monarch Ingest is built using [Poetry](https://python-poetry.org), which will create its own virtual environment. 

## Getting Started

### Set up the environment

Clone the repo and build the code:
```bash
$ git clone git@github.com/monarch-initiative/monarch-ingest
$ cd monarch-ingest
$ make all
```
This will install Poetry, create the virtual environment and fetch dependencies.

You're ready for ingests!

???+ example "Quick commands"
    - Download the entire Monarch data bucket:
    ```bash
    make download
    ```

    - Run all transforms:  
    ```bash
    make transform
    ```

    - Merge all of the transformed files with ontologies into a single pair of node and edge files
    ```bash
    make merge # result - output/merged/monarch-kg.tar.gz
    ```

    - Or you can do all 3 in one line!
    ```bash
    make download transform merge
    ```

### Ingests

!!! info ""
    For a detailed tutorial on ingests and how to make one, see the [Create an Ingest tab](Create-an-Ingest/1-Configure.md).  
    Here, we'll go through the general process in broad strokes.

!!! tip "Ingest Overview"
    An ingest consists of 3 main steps:  

    - Downloading the data  
    - Transforming the data  
    - Validating the output

    With a 4th post-processing step:  

    - Merging the output into a KGX knowledge graph

Now let's go through the process for running an existing monarch ingest!

**Step 1. Download**

Download the dataset from the source, for example:
```bash
wget http://www.informatics.jax.org/downloads/reports/MRK_Reference.rpt
```

Using the Google Cloud CLI you can download the whole Monarch data bucket:
```bash
gsutil -m cp -R gs://monarch-ingest/data .
```

**Step 2. Transform**

Use Koza to transform the dataset, based on a user-designed configuration  
(See [Create an Ingest](Create-an-Ingest/1-Configure.md) for more info)
```bash
poetry run koza transform --source monarch_ingest/mgi/publication_to_gene.yaml --output-format tsv --row-limit 10
```

**Step 3. Validate**

Make sure the output is valid and has the expected format:
```bash
poetry run kgx validate -i tsv output/mgi_publication_to_gene_edges.tsv 
```
