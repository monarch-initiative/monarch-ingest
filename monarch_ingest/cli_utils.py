import subprocess
from typing import Optional
import csv, tarfile
import pandas
import shlex, datetime
from sh import gzip, gunzip, tar, mv, lsolr, docker

from kgx.cli.cli_utils import transform as kgx_transform
from koza.cli_runner import transform_source
from koza.model.config.source_config import OutputFormat
from cat_merge.merge import merge
from closurizer.closurizer import add_closure

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

        # LOG.info(src_files)
        kgx_transform(
            inputs=src_files,
            input_format="tsv",
            stream=True,
            output=f"{output_dir}/rdf/{tag}.nt.gz",
            output_format="nt",
            output_compression="gz",
        )

    if not ingest_output_exists(tag, f"{output_dir}/transform_output"):
        raise FileNotFoundError(f"Ingest {tag} did not produce the the expected output")


def transform_phenio(output_dir: str = OUTPUT_DIR, force=False):

    phenio_tar = 'data/monarch/kg-phenio.tar.gz'
    assert os.path.exists(phenio_tar)

    nodefile = 'merged-kg_nodes.tsv'
    edgefile = 'merged-kg_edges.tsv'

    tar = tarfile.open(phenio_tar)
    tar.extract(nodefile, 'data/monarch')
    tar.extract(edgefile, 'data/monarch')

    os.makedirs(f"{output_dir}/transform_output", exist_ok=True)

    nodes = f"{output_dir}/transform_output/phenio_nodes.tsv"
    edges = f"{output_dir}/transform_output/phenio_edges.tsv"

    if (force == False) and file_exists(nodes) and file_exists(edges):
        LOG.info(f"Transformed output exists - skipping ingest: Phenio - To run this ingest anyway, use --force")
        return

    nodes_df = pandas.read_csv(f"data/monarch/{nodefile}", sep='\t', dtype="string",
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

    edges_df = pandas.read_csv(f"data/monarch/{edgefile}", sep='\t', dtype="string",
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
                        & edges_df["object"].str.startswith(tuple(prefixes))]

    edges_df.to_csv(edges, sep='\t', index=False)
    os.remove(f"data/monarch/{nodefile}")
    os.remove(f"data/monarch/{edgefile}")

    if (not file_exists(nodes) or not file_exists(edges)):
        raise FileNotFoundError("Phenio transform did not produce the expected output")


def transform_all(
    output_dir: str = OUTPUT_DIR,
    row_limit: Optional[int] = None,
    rdf: bool = False,
    force: bool = False,
    quiet: bool = False,
    debug: bool = False,
    log: bool = False,
    ):

    # TODO:
    # - check for data - download if missing (maybe y/n prompt?)
    # - check for difference in data? maybe implement in kghub downloder instead?

    try:
        transform_phenio(output_dir=output_dir, force=force)
    except Exception as e:
        LOG.error(f"Error running Phenio ingest:\n{e}")

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
    mappings.append("data/monarch/gene_mappings.tsv")

    LOG.info("Merging knowledge graph...")

    merge(
        name=name,
        source=input_dir,
        output_dir=output_dir,
        mappings=mappings
    )


def apply_closure(
        name: str = "monarch-kg",
        closure_file: str = f"data/monarch/phenio-relations-non-redundant.tsv",
        output_dir: str = OUTPUT_DIR
):
    output_file = f"{output_dir}/{name}-denormalized-edges.tsv"
    add_closure(kg_archive=f"{output_dir}/{name}.tar.gz",
                closure_file=closure_file,
                output_file=output_file)
    gzip(output_file)


def load_sqlite():
    subprocess.call("scripts/load_sqlite.sh")


def load_solr(node_schema,
              edge_schema,
              node_file,
              edge_file,
              output_dir: str = OUTPUT_DIR,
              run: bool = False):

    node_core = "entity"
    edge_core = "association"

    if edge_file.endswith(".gz"):
        gunzip(edge_file)
        edge_file = edge_file[:-len(".gz")]

    # awkwardly handle there not being a closurized/solrized version of the nodes file yet

    tar("zxf", f"{output_dir}/monarch-kg.tar.gz", 'monarch-kg_nodes.tsv')
    mv('monarch-kg_nodes.tsv', output_dir)

    # Start the server without specifying a schema
    print("Starting server...")
    lsolr('start-server')

    print("Adding cores and schema...")
    lsolr('add-cores', node_core, edge_core)
    lsolr('create-schema', core=node_core, schema=node_schema)
    lsolr('create-schema', core=edge_core, schema=edge_schema)
    print("Loading nodes...")
    lsolr('bulkload', node_file, core='entity', schema=node_schema)
    print("Loading edges...")
    lsolr('bulkload', edge_file, core='association', schema=edge_schema)

    # Run mode just loads into the docker container, doesn't export and shut down
    if not run:
        print("Copying data and removing container...")
        logging.info(docker('cp', 'my_solr:/var/solr/', 'output/'))
        subprocess.call(['tar', 'czf', 'solr.tar.gz', 'solr'], cwd='output')

        # remove the solr docker container
        docker('rm', '-f', 'my_solr')

    # cleanup
    gzip(edge_file)
    os.remove(f"{output_dir}/monarch-kg_nodes.tsv")

def do_release():
    release_name = datetime.datetime.now()
    release_name = release_name.strftime("%Y-%m-%d")

    LOG.info(f"Creating dated release: {release_name}...")

    try:
        LOG.debug(f"Uploading release to Google bucket...")

        subprocess.run(shlex.split(f"touch output/{release_name}"))
        
        # copy to monarch-archive bucket
        subprocess.run(shlex.split(f"gsutil -m cp -r output/* gs://monarch-archive/monarch-kg-dev/{release_name}"))
        subprocess.run(shlex.split(f"gsutil -q -m rm -rf gs://monarch-archive/monarch-kg-dev/latest"))
        subprocess.run(shlex.split(f"gsutil -q -m cp -r gs://monarch-archive/monarch-kg-dev/{release_name} gs://monarch-archive/monarch-kg-dev/latest"))
        
        # copy to data-public bucket
        subprocess.run(shlex.split(f"gsutil -q -m cp -r gs://monarch-archive/monarch-kg-dev/{release_name} gs://data-public-monarchinitiative/monarch-kg-dev/{release_name}"))
        subprocess.run(shlex.split(f"gsutil -q -m rm -rf gs://data-public-monarchinitiative/monarch-kg-dev/latest"))
        subprocess.run(shlex.split(f"gsutil -q -m cp -r gs://data-public-monarchinitiative/monarch-kg-dev/{release_name} gs://data-public-monarchinitiative/monarch-kg-dev/latest"))
        
        LOG.debug("Cleaning up files...")
        subprocess.run(shlex.split(f"rm output/{release_name}"))

        LOG.info(f"Successfuly uploaded release!")
    except BaseException as e:
        LOG.error(f"Oh no! Something went wrong:\n{e}")


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
