# `ingest`

**Usage**:

```console
$ ingest [OPTIONS] COMMAND [ARGS]...
```

**Options**:

* `--version`
* `--install-completion`: Install completion for the current shell.
* `--show-completion`: Show completion for the current shell, to copy it or customize the installation.
* `--help`: Show this message and exit.

**Commands**:

* `closure`
* `download`: Downloads data defined in download.yaml
* `jsonl`
* `merge`: Merge nodes and edges into kg
* `release`: Copy data to Monarch GCP data buckets
* `solr`
* `sqlite`
* `transform`: Run Koza transformation on specified...

## `ingest closure`

**Usage**:

```console
$ ingest closure [OPTIONS]
```

**Options**:

* `--help`: Show this message and exit.

## `ingest download`

Downloads data defined in download.yaml

**Usage**:

```console
$ ingest download [OPTIONS]
```

**Options**:

* `--ingests TEXT`: Which ingests to download data for
* `--all / --no-all`: Download all ingest datasets  [default: no-all]
* `--help`: Show this message and exit.

## `ingest jsonl`

**Usage**:

```console
$ ingest jsonl [OPTIONS]
```

**Options**:

* `--help`: Show this message and exit.

## `ingest merge`

Merge nodes and edges into kg

**Usage**:

```console
$ ingest merge [OPTIONS]
```

**Options**:

* `--input-dir TEXT`: Directory with nodes and edges to be merged  [default: output/transform_output]
* `--output-dir TEXT`: Directory to output data  [default: output]
* `-d, --debug / -q, --quiet`: Use --quiet to suppress log output, --debug for verbose
* `--help`: Show this message and exit.

## `ingest release`

Copy data to Monarch GCP data buckets

**Usage**:

```console
$ ingest release [OPTIONS]
```

**Options**:

* `--dir TEXT`: Directory with kg to be released  [default: output]
* `--kghub / --no-kghub`: Also release to kghub S3 bucket  [default: no-kghub]
* `--help`: Show this message and exit.

## `ingest solr`

**Usage**:

```console
$ ingest solr [OPTIONS]
```

**Options**:

* `--help`: Show this message and exit.

## `ingest sqlite`

**Usage**:

```console
$ ingest sqlite [OPTIONS]
```

**Options**:

* `--help`: Show this message and exit.

## `ingest transform`

Run Koza transformation on specified Monarch ingests

**Usage**:

```console
$ ingest transform [OPTIONS]
```

**Options**:

* `-o, --output-dir TEXT`: Directory to output data  [default: output]
* `-i, --ingest TEXT`: Run a single ingest (see ingests.yaml for a list)
* `--phenio / --no-phenio`: Run the phenio transform  [default: no-phenio]
* `-a, --all`: Ingest all sources
* `-f, --force`: Force ingest, even if output exists (on by default for single ingests)
* `--rdf / --no-rdf`: Output rdf files along with tsv  [default: no-rdf]
* `-d, --debug / -q, --quiet`: Use --quiet to suppress log output, --debug for verbose, including Koza logs
* `-l, --log`: Write DEBUG level logs to ./logs/ for each ingest
* `-n, --row-limit INTEGER`: Number of rows to process
* `--help`: Show this message and exit.
