import os, glob, tarfile, tarfile
from pathlib import Path
from typing import List, Optional
import pandas as pd

from kgx.cli.cli_utils import transform as kgx_transform
from koza.cli_runner import transform_source
from koza.model.config.source_config import OutputFormat

from monarch_ingest.helper import *

LOG = get_logger(__name__)

OUTPUT_DIR = "output"


def transform_one(
    source,
    output_dir: str = f"{OUTPUT_DIR}/transformed_output",
    row_limit: int = None,
    force: bool = False,
    quiet: bool = False,
    debug: bool = False,
    log: bool = False
):

    if log:
        Path("logs").mkdir(parents=True, exist_ok=True)
    logfile = Path(f"logs/{source}.log")
    _set_log_level(quiet, debug, log, logfile)

    ingests = get_ingests()

    if source not in ingests:
        raise ValueError(
            f"{source} is not a valid ingest - see ingests.yaml for a list of options"
        )

    source_file = os.path.join(os.path.dirname(__file__), (ingests[source]['config']))

    if not os.path.exists(source_file):
        raise ValueError(f"Source file {source_file} does not exist")

    if ingest_output_exists(source, output_dir) and not force:
        LOG.info(f"Transformed output exists - skipping ingest: {source} - To run this ingest anyway, use --force")
        return

    LOG.info(f"Running ingest: {source}...")

    transform_source(
        source=source_file,
        output_dir=output_dir,
        output_format=OutputFormat.tsv,
        local_table=None,
        global_table=None,
        row_limit=row_limit,
    )

    if not ingest_output_exists(source, output_dir):
        raise ValueError(f"{source} did not produce the the expected output")


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
                source=ingest,
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
    file_root: str = "monarch-kg",
    input_dir: str = f"{OUTPUT_DIR}/transform_output",
    output_dir: str = OUTPUT_DIR,
):
    LOG.info("Merging knowledge graph...")
    
    Path(f"{output_dir}/qc").mkdir(exist_ok=True, parents=True)

    # Get merged node and edge files
    edge_files = glob.glob(os.path.join(os.getcwd(), f"{input_dir}/*_edges.tsv"))
    node_files = glob.glob(os.path.join(os.getcwd(), f"{input_dir}/*_nodes.tsv"))

    edge_dfs = []
    node_dfs = []
    for edge_file in edge_files:
        edge_dfs.append(
            pd.read_csv(
                edge_file, sep="\t", dtype="string", lineterminator="\n", index_col='id'
            )
        )
    for node_file in node_files:
        node_dfs.append(
            pd.read_csv(
                node_file, sep="\t", dtype="string", lineterminator="\n", index_col='id'
            )
        )

    edges = pd.concat(edge_dfs, axis=0)
    nodes = pd.concat(node_dfs, axis=0)

    # Clean up nodes, dropping duplicates and merging on the same ID, 
    # which causes some weirdness with OMIM, where different categories use the same ID
    duplicate_nodes = nodes[nodes.index.duplicated(keep=False)]
    duplicate_nodes.to_csv(f"{output_dir}/qc/{file_root}-duplicate-nodes.tsv.gz", sep="\t")

    nodes.drop_duplicates(inplace=True)
    nodes.index.name = 'id'
    nodes.fillna("None", inplace=True)
    column_agg = {x: ' '.join for x in nodes.columns if x != 'id'}
    nodes.groupby(['id'], as_index=True).agg(column_agg)

    nodes_path = f"{output_dir}/{file_root}_nodes.tsv"
    nodes.to_csv(nodes_path, sep="\t")

    dangling_edges = edges[
        ~edges.subject.isin(nodes.index) | ~edges.object.isin(nodes.index)
    ]
    dangling_edges.to_csv(f"{output_dir}/qc/{file_root}-dangling-edges.tsv.gz", sep="\t")

    edges = edges[edges.subject.isin(nodes.index) & edges.object.isin(nodes.index)]

    edges_path = f"{output_dir}/{file_root}_edges.tsv"
    edges.to_csv(edges_path, sep="\t")

    # Tar zip final node and edge files
    tar = tarfile.open(f"{output_dir}/{file_root}.tar.gz", "w:gz")
    tar.add(nodes_path, arcname=f"{file_root}_nodes.tsv")
    tar.add(edges_path, arcname=f"{file_root}_edges.tsv")
    tar.close()

    # Clean up
    os.remove(nodes_path)
    os.remove(edges_path)

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
