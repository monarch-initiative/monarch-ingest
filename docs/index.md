# Monarch Ingest

## Overview

The Monarch Ingest generates [KGX](https://github.com/biolink/kgx/blob/master/specification/kgx-format.md) formatted files conforming to the [BioLink Model](https://biolink.github.io/biolink-model/) from a wide variety of biomedical data sources.

The eventual output of the Monarch Ingest process is the **Monarck KG**. The latest version of this can be found at:

- https://data.monarchinitiative.org/monarch-kg-dev/latest/monarch-kg.tar.gz

The Monarch Ingest is built using [Poetry](https://python-poetry.org), which will create its own virtual environment. 

## Getting Started

### Set up the environment

1. (Optional) Create a Python virtual environment for ingests:
```bash
virtualenv ingest-env
source ./ingest-env/bin/activate
```

1. <a href="https://python-poetry.org/docs/" target="_blank">Install Poetry</a>, if you don't already have it:
```bash
pip install poetry
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
| `ingest download` | `--tags <tags>`: Which ingest to download dataset for<br>`--all`: Download all datasets | Downloads source data to be transformed |
| `ingest transform` | `--tag`: Specify an ingest to run<br>`--ontology`: Runs the Monarch ontology ingest<br>`--all`: Runs all ingests `--output_dir`: Directory to output data<br>`--merge`: Merge output directory after transform<br>`--row-limit`: Number of rows to process<br>`--force`: Run ingest, even if output exists<br>`--quiet`: Suppress LOG output<br>`--log`: Write logs to ./logs/ for each ingest run | Perform a transform on source data |
| `ingest merge` | | Merge output/ into a tar.gz containg a single node and edge file |
| `ingest release` | `--update-latest`: Also replaces latest/ | Upload results to Monarch Google bucket as dated release |
