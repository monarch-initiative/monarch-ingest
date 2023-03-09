from typing import List, Optional

from kghub_downloader.download_utils import download_from_yaml
from monarch_ingest.cli_utils import *
from monarch_ingest.utils.log_utils import set_log_config, get_logger

import typer
typer_app = typer.Typer()

OUTPUT_DIR = "output"


@typer_app.command()
def download(
    ingests: Optional[List[str]] = typer.Option(None,  help="Which ingests to download data for"),
    all: bool = typer.Option(False, help="Download all ingest datasets")
    ):
    """Downloads data defined in download.yaml"""

    if ingests:
        download_from_yaml(
            yaml_file='monarch_ingest/download.yaml',
            output_dir='.',
            tags=ingests,
        )
    elif all:
        download_from_yaml(
            yaml_file='monarch_ingest/download.yaml',
            output_dir='.'
        )


@typer_app.command()
def transform(
    # data_dir: str = typer.Option('data', help='Path to data to ingest),
    output_dir: str = typer.Option(OUTPUT_DIR, "--output-dir", "-o", help="Directory to output data"),
    ingest: str = typer.Option(None, "--ingest", "-i", help="Run a single ingest (see ingests.yaml for a list)"),
    phenio: bool = typer.Option(False, help="Run the phenio transform"),
    all: bool = typer.Option(False, "--all", "-a", help="Ingest all sources"),
    force: bool = typer.Option(False, "--force", "-f", help="Force ingest, even if output exists (on by default for single ingests)"),
    rdf: bool = typer.Option(False, help="Output rdf files along with tsv"),
    verbose: Optional[bool] = typer.Option(None, "--debug/--quiet", "-d/-q", help="Use --quiet to suppress log output, --debug for verbose, including Koza logs"),
    log: bool = typer.Option(False, "--log", "-l", help="Write DEBUG level logs to ./logs/ for each ingest"),
    row_limit: int = typer.Option(None, "--row-limit", "-n", help="Number of rows to process"),
    # parallel: int = typer.Option(None, "--parallel", "-p", help="Utilize Dask to perform multiple ingests in parallel"),
):
    """Run Koza transformation on specified Monarch ingests"""

    set_log_config(logging.INFO if (verbose is None) else logging.DEBUG if (verbose == True) else logging.WARNING)

    if phenio:
        transform_phenio(
            output_dir=output_dir,
            force=force,
            verbose=verbose
        )
    elif ingest:
        transform_one(
            ingest = ingest,
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
def solr():
    load_solr()


@typer_app.command()
def release(kghub: bool = typer.Option(False, help="Also release to kghub S3 bucket")):
    """Copy data to Monarch GCP data buckets"""
    do_release(kghub)


if __name__ == "__main__":
    typer_app()
