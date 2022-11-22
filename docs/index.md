# Monarch Ingest

## Overview

The Monarch Ingest generates [KGX](https://github.com/biolink/kgx/blob/master/specification/kgx-format.md) formatted files conforming to the [BioLink Model](https://biolink.github.io/biolink-model/) from a wide variety of biomedical data sources.

The eventual output of the Monarch Ingest process is the **Monarck KG**. The latest version of this can be found at:

- https://data.monarchinitiative.org/monarch-kg-dev/latest/monarch-kg.tar.gz

The Monarch Ingest is built using [Poetry](https://python-poetry.org), which will create its own virtual environment. 

## Getting Started

### Set up the environment

1. <a href="https://python-poetry.org/docs/" target="_blank">Install Poetry</a>, if you don't already have it:
```bash
curl -sSL https://install.python-poetry.org | python3 -

# Optionally, have poetry create its venvs in your project directories
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

### Commands

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
    
| Command | Arguments/Options | Usage |
| :--- | :--- | :--- |
| `ingest download` | `--ingests <ingests>`: Which ingests to download dataset for (can be multiple)<br>`--all`: Download all datasets | Downloads source data to be transformed |
| `ingest transform` | `--ingest, -i`: Specify an ingest to run<br>`--phenio`: Runs the Monarch ontology ingest<br>`--all, -a`: Runs all ingests<br>`--output_dir, -o`: Directory to output data<br>`--rdf`: Output rdf files along with tsv<br>`--row-limit, -n`: Number of rows to process<br>`--force, -f`: Run ingest, even if output exists<br>`--debug, -d`: Verbose log output<br>`--quiet, -q`: Suppress LOG output<br>`--log, -l`: Write logs to ./logs/ for each ingest | Perform a transform on source data |
| `ingest merge` | | Merge output/ into a tar.gz containg a single node and edge file |
| `ingest release` | `--update-latest`: Also replaces `latest` release | Upload results to Monarch Google bucket as dated release |
| `ingest closure` | | Apply closures |
| `ingest sqlite` | | Load sqlite |
| `ingest solr` | | Load and run solr, no artifact created |
