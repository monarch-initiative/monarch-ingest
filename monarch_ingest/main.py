from typing import List, Optional

from monarch_ingest.cli_utils import *

import typer
typer_app = typer.Typer()

import logging
LOG = logging.getLogger(__name__)

OUTPUT_DIR = "output"

@typer_app.command()
def transform(ingest_config_file, output_dir: str = OUTPUT_DIR, row_limit: int = None,  ontology: bool = False, all: bool = False, force: bool = False):
    if ontology:
        LOG.debug(f"Running ontology transform")
        ontology_transform(output_dir, force)
    elif all:
        LOG.debug(f"Running all ingests")
        run_ingests(output_dir, row_limit=row_limit, force=force)
    else:
        LOG.debug(f"Running one ingest:\n{ingest_config_file}\n{row_limit}\n{force}")
        transform_one(ingest_config_file, output_dir, row_limit, force, all)

@typer_app.command()
def merge(edge_files: List[str], node_files: List[str], output_dir: str, file_root: str):
    LOG.info("Merging output directory")
    merge_files(edge_files, node_files, file_root, output_dir)
    
@typer_app.command()
def ontology_transform(output_dir: str, force=False):
    LOG.info("Testing ontology transform!!")

if __name__ == "__main__":
    typer_app()
