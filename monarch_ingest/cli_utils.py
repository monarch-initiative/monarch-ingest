import logging
from pathlib import Path
from typing import Optional
import pandas
import csv, tarfile
import sh

from kgx.cli.cli_utils import transform as kgx_transform
from koza.cli_runner import transform_source
from koza.model.config.source_config import OutputFormat
from cat_merge.merge import merge
from closurizer.closurizer import add_closure

from monarch_ingest.utils.ingest_utils import ingest_output_exists, file_exists, get_ingests
from monarch_ingest.utils.log_utils import get_logger, set_log_config, add_log_fh

logger = logging.getLogger(__name__)

OUTPUT_DIR = "output"


def transform_one(
    tag: str = None,
    output_dir: str = OUTPUT_DIR,
    row_limit: int = None,
    rdf: bool = False,
    force: bool = False,
    verbose: bool = None,
    log: bool = False
):
    set_log_config(logging.INFO if (verbose is None) else logging.DEBUG if (verbose == True) else logging.WARNING)
    if log: fh = add_log_fh(logger, Path(f"logs/{tag}.log"))

    ingests = get_ingests()

    if tag not in ingests:
        if log: logger.removeHandler(fh)
        raise ValueError(f"{tag} is not a valid ingest - see ingests.yaml for a list of options")

    source_file = Path(Path(__file__).parent, ingests[tag]['config'])

    if not Path(source_file).is_file():
        if log: logger.removeHandler(fh)
        raise ValueError(f"Source file {source_file} does not exist")

    if ingest_output_exists(tag, output_dir) and not force:
        logger.info(f"Transformed output exists - skipping ingest: {tag} - To run this ingest anyway, use --force")
        if log: logger.removeHandler(fh)
        return

    logger.info(f"Running ingest: {tag}...")
    try:
        transform_source(
            source=source_file,
            output_dir=f"{output_dir}/transform_output",
            output_format=OutputFormat.tsv,
            row_limit=row_limit,
            verbose=False if verbose == None else verbose,
        )
    except ValueError as e:
        if log: logger.removeHandler(fh)
        raise ValueError(f"Missing data - {e}")

    if rdf is not None:
        logger.info(f"Creating rdf output {output_dir}/rdf/{tag}.nt.gz ...")

        Path(f"{output_dir}/rdf").mkdir(parents=True, exist_ok=True)

        src_files = []
        src_nodes = f"{output_dir}/transform_output/{tag}_nodes.tsv"
        src_edges = f"{output_dir}/transform_output/{tag}_edges.tsv"
        if Path(src_nodes).is_file():
            src_files.append(src_nodes)
        if Path(src_edges).is_file():
            src_files.append(src_edges)

        # logger.info(src_files)
        kgx_transform(
            inputs=src_files,
            input_format="tsv",
            stream=True,
            output=f"{output_dir}/rdf/{tag}.nt.gz",
            output_format="nt",
            output_compression="gz",
        )

    if not ingest_output_exists(tag, f"{output_dir}/transform_output"):
        if log: logger.removeHandler(fh) 
        raise FileNotFoundError(f"Ingest {tag} did not produce the the expected output")

    if log: logger.removeHandler(fh)


def transform_phenio(
    output_dir: str = OUTPUT_DIR,
    force: bool = False,
    verbose: bool = False,
    log: bool = False,
    ):

    set_log_config(logging.INFO if (verbose is None) else logging.DEBUG if (verbose == True) else logging.WARNING)
    if log: fh = add_log_fh(logger, "logs/phenio.log")

    phenio_tar = 'data/monarch/kg-phenio.tar.gz'
    if not Path(phenio_tar).is_file():
        if log: logger.removeHandler(fh)
        raise FileNotFoundError('data/monarch/kg-phenio.tar.gz')

    nodefile = 'merged-kg_nodes.tsv'
    edgefile = 'merged-kg_edges.tsv'

    tar = tarfile.open(phenio_tar)
    tar.extract(nodefile, 'data/monarch')
    tar.extract(edgefile, 'data/monarch')

    Path(f"{output_dir}/transform_output").mkdir(parents=True, exist_ok=True)

    nodes = f"{output_dir}/transform_output/phenio_nodes.tsv"
    edges = f"{output_dir}/transform_output/phenio_edges.tsv"

    if (force == False) and file_exists(nodes) and file_exists(edges):
        logger.info(f"Transformed output exists - skipping ingest: Phenio - To run this ingest anyway, use --force")
        if log: logger.removeHandler(fh)
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
    Path(f"data/monarch/{nodefile}").unlink()
    Path(f"data/monarch/{edgefile}").unlink()

    if (not file_exists(nodes) or not file_exists(edges)):
        if log: logger.removeHandler(fh)    
        raise FileNotFoundError("Phenio transform did not produce the expected output")

    if log: logger.removeHandler(fh)


def transform_all(
    output_dir: str = OUTPUT_DIR,
    row_limit: Optional[int] = None,
    rdf: bool = False,
    force: bool = False,
    verbose: bool = None,
    log: bool = False,
    ):

    set_log_config(logging.INFO if (verbose is None) else logging.DEBUG if (verbose == True) else logging.WARNING)
    if log: fh = add_log_fh(logger, Path(f"logs/all_ingests.log"))

    # TODO:
    # - check for data - download if missing (maybe y/n prompt?)
    # - check for difference in data? maybe implement in kghub downloder instead?
    
    try:
        transform_phenio(output_dir=output_dir, force=force)
    except Exception as e:
        logger.error(f"Error running Phenio ingest: {e}")

    ingests = get_ingests()
    for ingest in ingests:
        try:
            transform_one(
                tag=ingest,
                output_dir=output_dir,
                row_limit=row_limit,
                rdf=rdf,
                force=force,
                verbose=verbose,
                log=log,
            )
        except Exception as e:
            logger.error(f"Error running ingest {ingest}: {e}")
            pass
        
    if log: logger.removeHandler(fh)


def merge_files(
    name: str = "monarch-kg",
    input_dir: str = f"{OUTPUT_DIR}/transform_output",
    output_dir: str = OUTPUT_DIR,
    ):

    logger.info("Generating mappings...")

    mappings = []
    mappings.append("data/monarch/mondo.sssom.tsv")
    mappings.append("data/monarch/gene_mappings.tsv")

    logger.info("Merging knowledge graph...")

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
    sh.gzip(output_file)


def load_sqlite():
    sh.bash("scripts/load_sqlite.sh")


def load_solr(node_schema,
              edge_schema,
              node_file,
              edge_file,
              output_dir: str = OUTPUT_DIR,
              run: bool = False):

    node_core = "entity"
    edge_core = "association"

    if edge_file.endswith(".gz"):
        sh.gunzip(edge_file)
        edge_file = edge_file[:-len(".gz")]

    # awkwardly handle there not being a closurized/solrized version of the nodes file yet

    sh.tar("zxf", f"{output_dir}/monarch-kg.tar.gz", 'monarch-kg_nodes.tsv')
    sh.mv('monarch-kg_nodes.tsv', output_dir)

    # Start the server without specifying a schema
    print("Starting server...")
    sh.lsolr('start-server')

    print("Adding cores and schema...")
    sh.lsolr('add-cores', node_core, edge_core)
    sh.lsolr('create-schema', core=node_core, schema=node_schema)
    sh.lsolr('create-schema', core=edge_core, schema=edge_schema)
    print("Loading nodes...")
    sh.lsolr('bulkload', node_file, core='entity', schema=node_schema)
    print("Loading edges...")
    sh.lsolr('bulkload', edge_file, core='association', schema=edge_schema)

    # Run mode just loads into the docker container, doesn't export and shut down
    if not run:
        print("Copying data and removing container...")
        logging.info(sh.docker('cp', 'my_solr:/var/solr/', 'output/'))
        sh.tar('czf', 'output/solr.tar.gz', "-C", '/solr', '.')

        # remove the solr docker container
        sh.docker('rm', '-f', 'my_solr')

    # cleanup
    sh.gzip(edge_file)
    Path(f"{output_dir}/monarch-kg_nodes.tsv").unlink()


def do_release():
    import datetime
    release_name = datetime.datetime.now().strftime("%Y-%m-%d")
    
    logger.info(f"Creating dated release: {release_name}...")

    try:
        logger.debug(f"Uploading release to Google bucket...")

        sh.touch(f"output/{release_name}")
        
        # copy to monarch-archive bucket
        sh.gsutil('gsutil', '-m', 'cp', '-r', 'output/*', f'gs://monarch-archive/monarch-kg-dev/{release_name}')

        sh.gsutil("-q", "-m", "cp", "-r", "output/*", f"gs://monarch-archive/monarch-kg-dev/{release_name}")

        sh.gsutil("-q", "-m", "rm", "-rf", f"gs://monarch-archive/monarch-kg-dev/latest")
        sh.gsutil("-q", "-m", "cp", "-r", f"gs://monarch-archive/monarch-kg-dev/{release_name} gs://monarch-archive/monarch-kg-dev/latest")

        # copy to data-public bucket
        sh.gsutil("-q", "-m", "cp", "-r", f"gs://monarch-archive/monarch-kg-dev/{release_name} gs://data-public-monarchinitiative/monarch-kg-dev/{release_name}")
        sh.gsutil("-q", "-m", "rm", "-rf", f"gs://data-public-monarchinitiative/monarch-kg-dev/latest")
        sh.gsutil("-q", "-m", "cp", "-r", f"gs://data-public-monarchinitiative/monarch-kg-dev/{release_name} gs://data-public-monarchinitiative/monarch-kg-dev/latest")
        
        logger.debug("Cleaning up files...")
        sh.rm(f"output/{release_name}")

        logger.info(f"Successfuly uploaded release!")
    except BaseException as e:
        logger.error(f"Oh no! Something went wrong:\n\t{e}")
