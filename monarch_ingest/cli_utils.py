import subprocess
from pathlib import Path

from typing import Optional
import tarfile
import pandas
import csv

from kgx.cli.cli_utils import transform as kgx_transform
from koza.cli_runner import transform_source
from koza.model.config.source_config import OutputFormat
from cat_merge.merge import merge
from monarch_gene_mapping.gene_mapping import main as generate_gene_mapping
from closurizer.closurizer import add_closure
from linkml_solr.cli import start_server, add_cores, create_schema, bulkload

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

    nodes_df = pandas.read_csv(f"data/phenio/{nodefile}", sep='\t', dtype="string",
                               quoting=csv.QUOTE_NONE, lineterminator="\n")
    nodes_df.drop(
        nodes_df.columns.difference(['id', 'category', 'name', 'description', 'xref', 'provided_by', 'synonym']),
        axis=1,
        inplace=True
    )
    nodes_df = nodes_df[~nodes_df["id"].str.contains("omim.org|hgnc_id")]
    nodes_df = nodes_df[~nodes_df["id"].str.startswith("MGI:")]

    # Hopefully this won't be necessary long term, but these IDs are coming
    # in with odd OBO prefixes from Phenio currently.
    obo_prefixes_to_repair = ['FBbt', 'WBbt', 'ZFA', 'XAO']
    for prefix in obo_prefixes_to_repair:
        nodes_df["id"] = nodes_df["id"].str.replace(f"OBO:{prefix}_", f"{prefix}:")


    # These bring in nodes necessary for other ingests, but won't capture the same_as / equivalentClass
    # associations that we'll also need
    prefixes = ["MONDO", "OMIM", "HP", "ZP", "MP", "CHEBI", "FBbt",
                "FYPO", "WBPhenotype", "GO", "MESH", "XPO",
                "ZFA", "UBERON", "WBbt", "ORPHA", "EMAPA"]

    nodes_df = nodes_df[nodes_df["id"].str.startswith(tuple(prefixes))]

    nodes_df.to_csv(nodes, sep='\t', index=False)

    edges_df = pandas.read_csv(f"data/phenio/{edgefile}", sep='\t', dtype="string",
                               quoting=csv.QUOTE_NONE, lineterminator="\n")
    edges_df.drop(
        edges_df.columns.difference(['id', 'subject', 'predicate', 'object',
                                      'category', 'relation', 'knowledge_source']),
        axis=1,
        inplace=True
    )

    edges_df = edges_df[edges_df["predicate"].str.contains(":")]

    # Hopefully this won't be necessary long term, but these IDs are coming
    # in with odd OBO prefixes from Phenio currently.
    for prefix in obo_prefixes_to_repair:
        for field in ["subject", "object"]:
            edges_df[field] = edges_df[field].str.replace(f"OBO:{prefix}_", f"{prefix}:")

    # Only keep edges where the subject and object both are within our allowable prefix list
    edges_df = edges_df[edges_df["subject"].str.startswith(tuple(prefixes))
                        and edges_df["object"].str.startswith(tuple(prefixes))]

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


def apply_closure(
        name: str = "monarch-kg",
        closure_file: str = f"data/phenio/phenio-relations-non-redundant.tsv",
        output_dir: str = OUTPUT_DIR
):
    add_closure(node_file=f"{name}_nodes.tsv",
                edge_file=f"{name}_edges.tsv",
                kg_archive=f"{name}.tar.gz",
                closure_file=closure_file,
                path=output_dir,
                output_file=f"{name}-with-closure_edges.tsv",
                fields=["subject", "object"])


def load_solr(node_schema,
              edge_schema,
              node_file,
              edge_file,
              output_dir: str = OUTPUT_DIR,
              run: bool = False):

    node_core = "entity"
    edge_core = "association"

    # awkwardly handle there not being a closurized/solrized version of the nodes file yet
    subprocess.call(['tar', 'zxf', f"{output_dir}/monarch-kg.tar.gz", 'monarch-kg_nodes.tsv'])
    subprocess.call(['mv', 'monarch-kg_nodes.tsv', output_dir])

    # Start the server without specifying a schema
    subprocess.call(['lsolr', 'start-server'])
    subprocess.call(['lsolr', 'add-cores', node_core, edge_core])
    subprocess.call(['lsolr', 'create-schema', '--core', node_core, '--schema', node_schema])
    subprocess.call(['lsolr', 'create-schema', '--core', edge_core, '--schema', edge_schema])
    subprocess.call(['lsolr', 'bulkload', node_file, '--core', 'entity', '--schema', node_schema])
    subprocess.call(['lsolr', 'bulkload', edge_file, '--core', 'association', '--schema', edge_schema])

    # Run mode just loads into the docker container, doesn't export and shut down
    if not run:
        subprocess.call(['docker', 'cp', 'my_solr:/var/solr/', 'output/'])
        subprocess.call(['tar', 'czf', 'solr.tar.gz', 'solr'], cwd='output')

        # clean up the nodes file that was pulled out of the tar
        os.remove(f"{output_dir}/monarch-kg_nodes.tsv")

        # remove the solr docker container
        subprocess.call(['docker', 'rm', '-f', 'my_solr'])


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
