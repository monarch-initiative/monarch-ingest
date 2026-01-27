# monarch-ingest

[![documentation](https://img.shields.io/badge/-Documentation-purple?logo=read-the-docs&logoColor=white&style=for-the-badge)](https://monarch-initiative.github.io/monarch-ingest/)

Monarch Ingest generates [KGX](https://github.com/biolink/kgx/blob/master/specification/kgx-format.md) formatted files conforming to the [BioLink Model](https://biolink.github.io/biolink-model/) from a wide variety of biomedical data sources.

The output of the Monarch Ingest process is the **Monarch KG**, available at [data.monarchinitiative.org](https://data.monarchinitiative.org/monarch-kg-dev/latest/monarch-kg.tar.gz).

## Installation

monarch-ingest is a Python 3.8+ package, installable via [Poetry](https://python-poetry.org).

1. Install Poetry:
```bash
curl -sSL https://install.python-poetry.org | python3 -

# Optional: Have poetry create its venvs in your project directories
poetry config virtualenvs.in-project true
```

2. Clone and install:
```bash
git clone git@github.com:monarch-initiative/monarch-ingest
cd monarch-ingest
poetry install
```

3. (Optional) Activate the virtual environment:
```bash
poetry shell
```

## Quick Start

Run the full pipeline:

```bash
# Download source data
ingest download --all

# Run all transforms
ingest transform --all

# Merge into single node/edge files
ingest merge

# Upload to Monarch bucket
ingest release
```

## CLI Reference

```
ingest [OPTIONS] COMMAND [ARGS]...

Commands:
  download   Downloads data defined in download.yaml
  transform  Run Koza transformation on specified Monarch ingests
  merge      Merge nodes and edges into kg
  release    Copy data to Monarch GCP data buckets
  closure    Generate closure files
  jsonl      Convert to JSONL format
  solr       Load Solr index
  sqlite     Create SQLite database
```

### Common Options

**download:**
- `--ingests TEXT` - Which ingests to download data for
- `--all` - Download all ingest datasets

**transform:**
- `-i, --ingest TEXT` - Run a single ingest
- `-a, --all` - Ingest all sources
- `-o, --output-dir TEXT` - Directory to output data (default: output)
- `-f, --force` - Force ingest even if output exists
- `-n, --row-limit INTEGER` - Number of rows to process
- `-l, --log` - Write DEBUG logs to ./logs/

**merge:**
- `--input-dir TEXT` - Directory with nodes/edges (default: output/transform_output)
- `--output-dir TEXT` - Output directory (default: output)

## Creating an Ingest

An ingest has two main steps:
1. **Download** - Fetch source data
2. **Transform** - Convert to KGX format

To run an existing ingest:
```bash
# Download data for a specific ingest
ingest download --ingests ncbi_gene

# Transform with row limit for testing
ingest transform --ingest ncbi_gene --row-limit 20 --log
```

For detailed ingest creation instructions, see the [Create an Ingest documentation](https://monarch-initiative.github.io/monarch-ingest/Create-an-Ingest/).

## KG Build Process

The build process includes:

1. **Download** - Weekly job fetches source data to cloud storage
2. **Transform** - Each ingest produces KGX TSV and RDF output
3. **Merge** - Join all transforms, normalize IDs via SSSOM mappings, prune dangling edges
4. **Post-processing** - Generate Neo4j dump, denormalized edges, SQLite, and Solr index

For detailed architecture, see the [KG Build Process documentation](https://monarch-initiative.github.io/monarch-ingest/KG-Build-Process/kg-build-process/).

## Modular Ingests

Some ingests are maintained in separate repositories and referenced as pass-through URLs:

| Ingest | Repository |
|--------|------------|
| Xenbase | [xenbase-ingest](https://github.com/monarch-initiative/xenbase-ingest) |
| ZFIN | [zfin-ingest](https://github.com/monarch-initiative/zfin-ingest) |
| Alliance | [alliance-ingest](https://github.com/monarch-initiative/alliance-ingest) |
| ClinGen | [clingen-ingest](https://github.com/monarch-initiative/clingen-ingest) |
| ClinVar | [clinvar-ingest](https://github.com/monarch-initiative/clinvar-ingest) |
| OMIM | [omim-ingest](https://github.com/monarch-initiative/omim-ingest) |
| GO | [go-ingest](https://github.com/monarch-initiative/go-ingest) |
| BioGRID | [biogrid-ingest](https://github.com/monarch-initiative/biogrid-ingest) |
| PantherDB | [pantherdb-orthologs-ingest](https://github.com/monarch-initiative/pantherdb-orthologs-ingest) |

## Resources

- [Full Documentation](https://monarch-initiative.github.io/monarch-ingest/)
- [Monarch KG Downloads](https://data.monarchinitiative.org/monarch-kg-dev/latest/)
- [QC Dashboard](https://monarch-initiative.github.io/monarch-qc/)
