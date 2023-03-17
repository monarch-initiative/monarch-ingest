# Monarch Ingest

## Introduction

The Monarch Ingest generates [KGX](https://github.com/biolink/kgx/blob/master/specification/kgx-format.md) formatted files conforming to the [BioLink Model](https://biolink.github.io/biolink-model/) from a wide variety of biomedical data sources.

The eventual output of the Monarch Ingest process is the **Monarck KG**. The latest version of this can be found at:

- https://data.monarchinitiative.org/monarch-kg-dev/latest/monarch-kg.tar.gz

The Monarch Ingest is built using [Poetry](https://python-poetry.org), which will create its own virtual environment. 

## Installation

monarch-ingest is a Python 3.8+ package, installable via [Poetry](https://python-poetry.org).  

1. <a href="https://python-poetry.org/docs/" target="_blank">Install Poetry</a>, if you don't already have it:  
```bash
curl -sSL https://install.python-poetry.org | python3 -

# Optional: Have poetry create its venvs in your project directories
poetry config virtualenvs.in-project true
```

1. Clone the repo and build the code:
```bash
git clone git@github.com/monarch-initiative/monarch-ingest
cd monarch-ingest
poetry install
```

That's it! You're now ready for ingests.  

For a detailed tutorial on ingests and how to make one, see the [Create an Ingest tab](Create-an-Ingest/index.md). 

### Quickstart

For usage details, see [CLI](CLI.md),  
or run `ingest --help` or `ingest <command> --help`.

??? tip "Run the whole pipeline!"
    - Download the source data:
    ```bash
    ingest download --all
    ```

    - Run all transforms:  
    ```bash
    ingest transform --all
    ```

    - Merge all transformed output into a tar.gz containing one node and one edge file
    ```bash
    ingest merge
    ```

    - Upload the results to the Monarch Ingest Google bucket
    ```bash
    ingest release
    ```

