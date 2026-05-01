# Monarch Ingest

## Overview

The Monarch Ingest generates [KGX](https://github.com/biolink/kgx/blob/master/specification/kgx-format.md) formatted files conforming to the [BioLink Model](https://biolink.github.io/biolink-model/) from a wide variety of biomedical data sources.

The eventual output of the Monarch Ingest process is the **Monarch KG**.  
The latest version of this can be found at [data.monarchinitiative.org](https://data.monarchinitiative.org/monarch-kg-dev/latest/monarch-kg.tar.gz)

See also the folder [monarch-kg-dev/latest](https://data.monarchinitiative.org/monarch-kg-dev/latest/)

Monarch Ingest is managed with [uv](https://docs.astral.sh/uv/), which creates and manages its own virtual environment.

## Installation

monarch-ingest is a Python 3.10+ package, managed with [uv](https://docs.astral.sh/uv/).

1. <a href="https://docs.astral.sh/uv/getting-started/installation/" target="_blank">Install uv</a>, if you don't already have it:
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

1. Clone the repo:
```bash
git clone git@github.com:monarch-initiative/monarch-ingest
```

1. Install monarch-ingest:
```bash
cd monarch-ingest
uv sync
```

1. (Optional) Activate the virtual environment:
```bash
# This step removes the need to prefix all commands with `uv run`
source .venv/bin/activate
```

## Usage

For a detailed tutorial on ingests and how to make one, see the [Create an Ingest tab](Create-an-Ingest/index.md). 

CLI usage is available in the [CLI tab](CLI.md), gcor by running `ingest --help`.

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

<meta http-equiv='cache-control' content='no-cache'> 
<meta http-equiv='expires' content='0'> 
<meta http-equiv='pragma' content='no-cache'>
