from typing import List, Optional
from kghub_downloader.download_utils import download_from_yaml
from monarch_ingest.cli_utils import *
from monarch_ingest.utils.log_utils import set_log_config, get_logger

import typer
typer_app = typer.Typer()

OUTPUT_DIR = "output"

@typer_app.command()
def download(
    tags: Optional[List[str]] = typer.Option(None,  help="Which tags to download data for"),
    all: bool = typer.Option(False, help="Download all ingest datasets")
    ):
    """Downloads data defined in download.yaml"""

    if tags:
        download_from_yaml(
            yaml_file='monarch_ingest/download.yaml',
            output_dir='.',
            tags=tags,
        )
    elif all:
        download_from_yaml(
            yaml_file='monarch_ingest/download.yaml',
            output_dir='.'
        )

@typer_app.command()
def transform(
    # data_dir: str = typer.Option('data', help='Path to data to ingest),
    output_dir: str = typer.Option(OUTPUT_DIR, help="Directory to output data"),
    tag: str = typer.Option(None, help="Which ingest to run (see ingests.yaml for a list)"),
    phenio: bool = typer.Option(False, help="Option: pass to run the phenio transform"),
    all: bool = typer.Option(False, help="Ingest all sources"),
    row_limit: int = typer.Option(None, help="Number of rows to process"),
    do_merge: bool = typer.Option(False, "--merge", help="Merge output dir after ingest"),
    force: bool = typer.Option(None,help="Force ingest, even if output exists (on by default for single ingests)"),
    rdf: bool = typer.Option(None, help="Output rdf files along with tsv"),
    verbose: Optional[bool] = typer.Option(None, "--debug/--quiet", help="Use --quiet to suppress log output, --debug for verbose, including Koza logs"),
    log: bool = typer.Option(False, help="Write DEBUG level logs to ./logs/ for each ingest"),
    parallel: bool = typer.Option(False, help="Utilize Dask to perform multiple ingests in parallel")
):
    """Run Koza transformation on specified Monarch ingests"""
    
    set_log_config(logging.INFO if (verbose is None) else logging.DEBUG if (verbose == True) else logging.WARNING)

    if parallel:
        parallel_all(
            output_dir = output_dir,
            row_limit = row_limit,
            rdf = rdf,
            force = force,
            verbose=verbose,
            log = log,
        )
        return

    if phenio:
        transform_phenio(
            output_dir=output_dir,
            force=force,
            verbose=verbose
        )
    elif tag:
        transform_one(
            tag = tag,
            output_dir = output_dir,
            row_limit = row_limit,
            rdf = rdf,
            force = True if force is None else force,
            verbose = verbose,
            log = log,
        )
    elif all:
        transform_all(
            output_dir = output_dir,
            row_limit = row_limit,
            rdf = rdf,
            force = force,
            verbose=verbose,
            log = log,
        )
    if do_merge:
        merge(f"{output_dir}/transform_output", output_dir)


@typer_app.command()
def merge(
    input_dir: str = typer.Option(f"{OUTPUT_DIR}/transform_output", help="Directory with nodes and edges to be merged",),
    output_dir: str = typer.Option(f"{OUTPUT_DIR}", help="Directory to output data"),
    ):
    """Merge nodes and edges into kg"""
    
    merge_files(input_dir=input_dir, output_dir=output_dir)


@typer_app.command()
def closure():
    apply_closure()

@typer_app.command()
def sqlite():
    load_sqlite()


@typer_app.command()
def solr(run: bool = typer.Option(False, help="Load and run solr, no artifact created")):
    load_solr(node_schema="solr/entity-index.yaml",
              edge_schema="solr/association-index.yaml",
              node_file=f"{OUTPUT_DIR}/monarch-kg_nodes.tsv",
              edge_file=f"{OUTPUT_DIR}/monarch-kg-denormalized-edges.tsv.gz",
              run=run)


@typer_app.command()
def release():
    """Copy data to Monarch GCP data buckets"""
    do_release()


if __name__ == "__main__":
    typer_app()
