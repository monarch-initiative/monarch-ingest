from pathlib import Path
from typing import List, Optional
import tarfile, pandas

from kgx.cli.cli_utils import transform as kgx_transform
from koza.cli_runner import transform_source
from koza.model.config.source_config import OutputFormat
from cat_merge.merge import merge
from monarch_gene_mapping.gene_mapping import main as generate_gene_mapping

from monarch_ingest.helper import *

LOG = get_logger(__name__)
OUTPUT_DIR = "output"


def transform_one(
    tag,
    output_dir: str = OUTPUT_DIR,
    row_limit: int = None,
    rdf: bool = False,
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
        output_dir=f"{output_dir}/transform_output",
        output_format=OutputFormat.tsv,
        local_table=None,
        global_table=None,
        row_limit=row_limit,
    )

    if rdf is not None:
        LOG.info(f"Creating rdf output {output_dir}/rdf/{tag}.nt.gz ...")

        Path(f"{output_dir}/rdf").mkdir(parents=True, exist_ok=True)

        src_files = []
        src_nodes = f"{output_dir}/transform_output/{tag}_nodes.tsv"
        src_edges = f"{output_dir}/transform_output/{tag}_edges.tsv"
        if os.path.exists(src_nodes):
            src_files.append(src_nodes)
        if os.path.exists(src_edges):
            src_files.append(src_edges)

        print(src_files)
        kgx_transform(
            inputs=src_files,
            input_format="tsv",
            stream=True,
            output=f"{output_dir}/rdf/{tag}.nt.gz",
            output_format="nt",
            output_compression="gz",
        )

    if not ingest_output_exists(tag, f"{output_dir}/transform_output"):
        raise ValueError(f"{tag} did not produce the the expected output")


def transform_phenio(output_dir: str = OUTPUT_DIR, force=False):

    phenio_tar = 'data/phenio/kg-phenio.tar.gz'
    assert os.path.exists(phenio_tar)

    nodefile = 'merged-kg_nodes.tsv'
    edgefile = 'merged-kg_edges.tsv'

    tar = tarfile.open(phenio_tar)
    tar.extract(nodefile, 'data/phenio')
    tar.extract(edgefile, 'data/phenio')

    os.makedirs(f"{output_dir}/transform_output", exist_ok=True)

    nodes = f"{output_dir}/transform_output/phenio_nodes.tsv"
    edges = f"{output_dir}/transform_output/phenio_edges.tsv"

    nodes_df = pandas.read_csv(f"data/phenio/{nodefile}", sep='\t', low_memory=False)
    nodes_df = nodes_df[['id', 'category', 'name', 'description', 'xref', 'provided_by', 'synonym']]
    nodes_df = nodes_df[~nodes_df["id"].str.contains("omim.org|hgnc_id")]
    nodes_df.to_csv(nodes, sep='\t', index=False)

    edges_df = pandas.read_csv(f"data/phenio/{edgefile}", sep='\t', low_memory=False)
    edges_df = edges_df[['id', 'subject', 'predicate', 'object', 'category', 'relation', 'knowledge_source']]
    edges_df.to_csv(edges, sep='\t', index=False)

    os.remove(f"data/phenio/{nodefile}")
    os.remove(f"data/phenio/{edgefile}")


def transform_all(
    output_dir: str = OUTPUT_DIR,
    row_limit: Optional[int] = None,
    rdf: bool = False,
    force: bool = False,
    quiet: bool = False,
    debug: bool = False,
    log: bool = False,
):

    # TODO: check for data - download if missing (maybe y/n prompt?)

    try:
        transform_phenio(output_dir=output_dir, force=force)
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
                rdf=rdf,
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
    LOG.info("Generate mappings...")

    mappings = []

    mappings.append("data/monarch/mondo.sssom.tsv")

    mapping_output_dir = f"{OUTPUT_DIR}/mappings"
    generate_gene_mapping(output_dir=mapping_output_dir)
    mappings.append(f"{mapping_output_dir}/gene_mappings.tsv")


    LOG.info("Merging knowledge graph...")

    merge(
        name=name,
        input_dir=input_dir,
        output_dir=output_dir,
        mappings=mappings
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
        stream_formatter = logging.Formatter(':%(levelname)-4s: %(name)-20s: %(message)s')
        stream_handler.setFormatter(stream_formatter)
        stream_handler.setLevel(logging.ERROR)
        logger.addHandler(stream_handler)

        # Set a handler for file output
        file_handler = logging.FileHandler(logfile, mode='w')
        file_formatter = logging.Formatter(":%(levelname)-4s:%(name)-26s: %(message)s")
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
