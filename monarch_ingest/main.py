from typing import List
import datetime
from kghub_downloader.download_utils import download_from_yaml
from monarch_ingest.cli_utils import *

import typer
import logging

typer_app = typer.Typer()

logging.basicConfig()
LOG = logging.getLogger(__name__)

OUTPUT_DIR = "output"


@typer_app.command()
def download(
    tags: Optional[List[str]] = typer.Option(None,  help="Which tags to download data for"),
    all: bool = typer.Option(False, help="Download all ingest datasets")
    ):
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
    output_dir: str = typer.Option(OUTPUT_DIR, help="Directory to output data"),
    # data_dir: str = typer.Option('data', help='Path to data to ingest),
    tag: str = typer.Option(None, help="Which ingest to run (see ingests.yaml for a list)"),
    phenio: bool = typer.Option(False, help="Option: pass to run the phenio transform"),
    all: bool = typer.Option(False, help="Ingest all sources"),
    row_limit: int = typer.Option(None, help="Number of rows to process"),
    do_merge: bool = typer.Option(False, "--merge", help="Merge output dir after ingest"),
    force: bool = typer.Option(None,help="Force ingest, even if output exists (on by default for single ingests)"),
    rdf: bool = typer.Option(None, help="Output rdf files along with tsv"),
    quiet: bool = typer.Option(False, help="Suppress LOG output"),
    debug: bool = typer.Option(False, help="Print additional debug output to console"),
    log: bool = typer.Option(False, help="Write DEBUG level logs to ./logs/ for each ingest run"),
):
    """
    Something descriptive
    """
    if phenio:
        LOG.info(f"Running phenio transform...")
        transform_phenio(
            output_dir=output_dir,
            force=force
        )
    elif all:
        LOG.info(f"Running all ingests...")
        transform_all(
            output_dir=output_dir,
            row_limit=row_limit,
            rdf=rdf,
            force=force,
            quiet=quiet,
            debug=debug,
            log=log,
        )
    elif tag:
        if force is None:
            force = True
        transform_one(
            tag=tag,
            output_dir=output_dir,
            row_limit=row_limit,
            rdf=rdf,
            force=force,
            quiet=quiet,
            debug=debug,
            log=log,
        )
    if do_merge:
        merge(f"{output_dir}/transform_output", output_dir)


@typer_app.command()
def merge(
    input_dir: str = typer.Option(
        f"{OUTPUT_DIR}/transform_output",
        help="Directory containing nodes and edges to be merged",
        ),
    output_dir: str = typer.Option(f"{OUTPUT_DIR}", help="Directory to output data"),
    ):
    """
    Something descriptive
    """
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

    release_name = datetime.datetime.now()
    release_name = release_name.strftime("%Y-%m-%d")

    LOG.info(f"Creating dated release: {release_name}...")

    try:
        LOG.debug(f"Uploading release to Google bucket...")
        subprocess.run(['touch', f"output/{release_name}"])

        # copy to monarch-archive bucket
        subprocess.run(['gsutil', '-m', 'cp', '-r', 'output/*', f"gs://monarch-archive/monarch-kg-dev/{release_name}"])
        subprocess.run(['gsutil', '-q', '-m', 'rm', '-rf', 'gs://monarch-archive/monarch-kg-dev/latest'])
        subprocess.run(['gsutil', '-q', '-m', 'cp', '-r', f"gs://monarch-archive/monarch-kg-dev/{release_name}","gs://monarch-archive/monarch-kg-dev/latest",])

        # copy to data-public bucket
        subprocess.run(['gsutil', '-q', '-m', 'cp', '-r', f"gs://monarch-archive/monarch-kg-dev/{release_name}",f"gs://data-public-monarchinitiative/monarch-kg-dev/{release_name}",])
        subprocess.run(['gsutil', '-q', '-m', 'rm', '-rf', 'gs://data-public-monarchinitiative/monarch-kg-dev/latest'])
        subprocess.run(['gsutil', '-q', '-m', 'cp', '-r', f"gs://data-public-monarchinitiative/monarch-kg-dev/{release_name}","gs://data-public-monarchinitiative/monarch-kg-dev/latest",])

        LOG.debug("Cleaning up files...")
        subprocess.run(['rm', f"output/{release_name}"])

        LOG.info(f"Successfuly uploaded release!")
    except BaseException as e:
        LOG.error(f"Oh no! Something went wrong:\n{e}")


if __name__ == "__main__":
    typer_app()
