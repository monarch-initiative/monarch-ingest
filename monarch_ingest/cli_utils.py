import os, glob, tarfile, tarfile
from pathlib import Path
from typing import List, Optional
import pandas as pd

from kgx.cli.cli_utils import transform as kgx_transform
from koza.cli_runner import transform_source
from koza.model.config.source_config import OutputFormat
from cat_merge.merge import merge

from monarch_ingest.helper import *

LOG = get_logger(__name__)
OUTPUT_DIR = "output"

def transform_one(
    tag,
    output_dir: str = f"{OUTPUT_DIR}/transformed_output",
    row_limit: int = None,
    force: bool = False,
    quiet: bool = False,
    debug: bool = False,
    log: bool = False
):

    if log:
        Path("logs").mkdir(parents=True, exist_ok=True)
    logfile = Path(f"logs/{tag}.log")
    _set_log_level(quiet, debug, log, logfile)

    ingests = get_ingests()

    if tag not in ingests:
        raise ValueError(
            f"{tag} is not a valid ingest - see ingests.yaml for a list of options"
        )

    source_file = os.path.join(os.path.dirname(__file__), (ingests[tag]['config']))

    if not os.path.exists(source_file):
        raise ValueError(f"Source file {source_file} does not exist")

    if ingest_output_exists(tag, output_dir) and not force:
        LOG.info(f"Transformed output exists - skipping ingest: {tag} - To run this ingest anyway, use --force")
        return

    LOG.info(f"Running ingest: {tag}...")

    transform_source(
        source=source_file,
        output_dir=output_dir,
        output_format=OutputFormat.tsv,
        local_table=None,
        global_table=None,
        row_limit=row_limit,
    )

    if not ingest_output_exists(tag, output_dir):
        raise ValueError(f"{tag} did not produce the the expected output")


def transform_ontology(output_dir: str = f"{OUTPUT_DIR}/transform_output", force=False):
    assert os.path.exists('data/monarch/monarch.json')

    edges = f"{output_dir}/monarch_ontology_edges.tsv"
    nodes = f"{output_dir}/monarch_ontology_nodes.tsv"

    # Since this is fairly slow, don't re-do it if the files exist unless forcing transforms
    # This shouldn't affect cloud builds, but will be handy for local runs
    if (
        not force
        and os.path.exists(edges)
        and os.path.exists(nodes)
        and os.path.getsize(edges) > 0
        and os.path.getsize(nodes)
    ):
        return

    kgx_transform(
        inputs=["data/monarch/monarch.json"],
        input_format="obojson",
        stream=False,
        output=f"{output_dir}/monarch_ontology",
        output_format="tsv",
    )

    if not file_exists(edges):
        raise ValueError("Ontology transform did not produce an edges file")
    if not file_exists(nodes):
        raise ValueError("Ontology transform did not produce a nodes file")


def transform_all(
    output_dir: str = f"{OUTPUT_DIR}/transform_output",
    row_limit: Optional[int] = None,
    force: bool = False,
    quiet: bool = False,
    debug: bool = False,
    log: bool = False,
):

    # TODO: check for data - download if missing (maybe y/n prompt?)

    try:
        transform_ontology(output_dir=output_dir, force=force)
    except Exception as e:
        LOG.error(f"Error running ontology ingest:\n{e}")
        pass

    ingests = get_ingests()
    for ingest in ingests:
        try:
            transform_one(
                tag=ingest,
                output_dir=output_dir,
                row_limit=row_limit,
                force=force,
                log=log,
                quiet=quiet,
                debug=debug,
            )
        except Exception as e:
            LOG.error(f"Error running ingest {ingest}:\n{e}")
            pass


def merge_files(
    name: str = "monarch-kg",
    input_dir: str = f"{OUTPUT_DIR}/transform_output",
    output_dir: str = OUTPUT_DIR,
):
    LOG.info("Merging knowledge graph...")
    
    merge(
        name = name,
        input_dir = input_dir,
        output_dir = output_dir
    )

def _set_log_level(
    quiet: bool = False, debug: bool = False, log: bool = False, logfile: str = 'logs/transform.log'
):

    if log:
        # Reset root logger in case it was configured elsewhere
        logger = logging.getLogger()
        logging.root.handlers = []

        # Set a handler for console output
        stream_handler = logging.StreamHandler()
        stream_formatter = logging.Formatter(':%(name)-20s: %(levelname)-8s: %(message)s')
        stream_handler.setFormatter(stream_formatter)
        stream_handler.setLevel(logging.ERROR)
        logger.addHandler(stream_handler)

        # Set a handler for file output
        file_handler = logging.FileHandler(logfile, mode='w')
        file_formatter = logging.Formatter("%(name)-26s: %(levelname)-8s: %(message)s")
        file_handler.setFormatter(file_formatter)
        file_handler.setLevel(logging.DEBUG)
        logger.addHandler(file_handler)

        # Set root logger level
        logger.setLevel(logging.DEBUG)
    elif quiet:
        logging.getLogger().setLevel(logging.WARNING)
    elif debug:
        logging.getLogger().setLevel(logging.DEBUG)
    else:
        logging.getLogger().setLevel(logging.INFO)
