import subprocess, datetime
#from asyncio import subprocess
from monarch_ingest.cli_utils import *

import typer
typer_app = typer.Typer()

import logging
LOG = logging.getLogger(__name__)

OUTPUT_DIR = "output"

@typer_app.command()
def transform(
    source: str = typer.Option(None, help="Which ingest to run (see ingests.yaml for a list)"),
    #data_dir: str = typer.Option('data', help='Path to data to ingest),
    output_dir: str = typer.Option(OUTPUT_DIR, help="Directory to putput data"),
    row_limit: int = typer.Option(None, help="Number of rows to process"),
    ontology: bool = typer.Option(False, help="Option: pass to run the ontology ingest"),
    all: bool = typer.Option(False, help="Ingest all sources"),
    do_merge: bool = typer.Option(False, "--merge", help="Merge output dir after ingest"),
    force: bool = typer.Option(None, help="Force ingest, even if output exists (on by default for single ingests)")
    ):
    """
    Something descriptive 
    """
    if ontology:
        LOG.info(f"Running ontology transform")
        transform_ontology(output_dir, force)
    if all:
        LOG.info(f"Running all ingests")
        transform_all(f"{output_dir}/transform_output", row_limit=row_limit, force=force)
    elif source:
        if force is None:
            force = True
        LOG.info(f"Running ingest: {source}")
        transform_one(source, f"{output_dir}/transform_output", row_limit, force)
    if do_merge:
            merge(f"{output_dir}/transform_output", output_dir)

@typer_app.command()
def merge(
    input_dir: str = typer.Option(f"{OUTPUT_DIR}/transform_output", help="Directory containing nodes and edges to be merged"),
    output_dir: str = typer.Option(f"{OUTPUT_DIR}", help="Directory to output data")
    ):
    """
    Something descriptive 
    """
    LOG.info("Merging output directory")
    merge_files(input_dir=input_dir, output_dir=output_dir)

@typer_app.command()
def release(update_latest: bool = typer.Option(False, help="Pass to update latest/ as well")):
    release_name = datetime.datetime.now()
    release_name = release_name.strftime("%Y-%m-%d")
    
    subprocess.run(['touch', f"output/{release_name}"])
    subprocess.run(['gsutil', '-m', 'cp', '-r', 'output/*', f"gs://monarch-ingest/{release_name}"])

    subprocess.run(['gsutil', '-m', 'rm', '-rf', 'gs://monarch-ingest/latest'])
    subprocess.run(['gsutil', '-m', 'cp', '-r', f"gs://monarch-ingest/{release_name}", "gs://monarch-ingest/latest"])  

    subprocess.run(['rm', f"output/{release_name}"])

if __name__ == "__main__":
    typer_app()
