import csv
import tarfile
from pathlib import Path
from typing import Optional
from biolink import model # import the pythongen biolink model to get the version
from linkml_runtime import SchemaView
from linkml.utils.helpers import convert_to_snake_case

# from loguru import logger

import pandas
import sh

from cat_merge.merge import merge
from closurizer.closurizer import add_closure
from kgx.cli.cli_utils import transform as kgx_transform
from koza.cli_runner import transform_source
from koza.model.config.source_config import OutputFormat
from linkml_runtime.utils.formatutils import camelcase

from monarch_ingest.utils.ingest_utils import ingest_output_exists, file_exists, get_ingests
from monarch_ingest.utils.log_utils import get_logger
# from koza.utils.log_utils import get_logger


OUTPUT_DIR = "output"


def transform_one(
    ingest: str = None,
    output_dir: str = OUTPUT_DIR,
    row_limit: int = None,
    rdf: bool = False,
    force: bool = False,
    verbose: bool = None,
    log: bool = False
):
    logger = get_logger(name = ingest if log else None, verbose = verbose)

    ingests = get_ingests()

    if ingest not in ingests:
        # if log: logger.removeHandler(fh)
        raise ValueError(f"{ingest} is not a valid ingest - see ingests.yaml for a list of options")

    source_file = Path(Path(__file__).parent, ingests[ingest]['config'])

    if not Path(source_file).is_file():
        # if log: logger.removeHandler(fh)
        raise ValueError(f"Source file {source_file} does not exist")

    if ingest_output_exists(ingest, output_dir) and not force:
        logger.info(f"Transformed output exists - skipping ingest: {ingest} - To run this ingest anyway, use --force")
        # if log: logger.removeHandler(fh)
        return

    logger.info(f"Running ingest: {ingest}")
    try:
        transform_source(
            source=source_file,
            output_dir=f"{output_dir}/transform_output",
            output_format=OutputFormat.tsv,
            row_limit=row_limit,
            verbose=verbose,
            # verbose=False if verbose == None else verbose,
            # log=log
        )
    except ValueError as e:
        # if log: logger.removeHandler(fh)
        raise ValueError(f"Missing data - {e}")

    if rdf:
        logger.info(f"Creating rdf output {output_dir}/rdf/{ingest}.nt.gz ...")

        Path(f"{output_dir}/rdf").mkdir(parents=True, exist_ok=True)

        src_files = []
        src_nodes = f"{output_dir}/transform_output/{ingest}_nodes.tsv"
        src_edges = f"{output_dir}/transform_output/{ingest}_edges.tsv"
        if Path(src_nodes).is_file():
            src_files.append(src_nodes)
        if Path(src_edges).is_file():
            src_files.append(src_edges)

        kgx_transform(
            inputs=src_files,
            input_format="tsv",
            stream=True,
            output=f"{output_dir}/rdf/{ingest}.nt.gz",
            output_format="nt",
            output_compression="gz",
        )

    if not ingest_output_exists(ingest, f"{output_dir}/transform_output"):
        # if log: logger.removeHandler(fh) 
        raise FileNotFoundError(f"Ingest {ingest} did not produce the the expected output")

    # if log: logger.removeHandler(fh)


def transform_phenio(
    output_dir: str = OUTPUT_DIR,
    force: bool = False,
    verbose: bool = False,
    log: bool = False,
    ):

    # if log: fh = add_log_fh(logger, "logs/phenio.log")
    logger = get_logger(name = "phenio" if log else None, verbose=verbose)

    # TODO: can this be fetched from a purl?
    biolink_model_schema = SchemaView(
        f"https://raw.githubusercontent.com/biolink/biolink-model/v{model.version}/biolink-model.yaml")

    phenio_tar = 'data/monarch/kg-phenio.tar.gz'
    if not Path(phenio_tar).is_file():
        # if log: logger.removeHandler(fh)
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
        # if log: logger.removeHandler(fh)
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

    valid_node_categories = {f"biolink:{camelcase(cat)}" for cat in biolink_model_schema.class_descendants("named thing")}
    phenio_node_categories = set(nodes_df['category'].unique())
    invalid_node_categories = phenio_node_categories - valid_node_categories
    if invalid_node_categories:
        logger.error(f"Invalid node categories: {invalid_node_categories}")
        invalid_node_categories_df = nodes_df[nodes_df['category'].isin(invalid_node_categories)]
        logger.error(f"Removing {len(invalid_node_categories_df)} nodes with invalid categories")
        nodes_df = nodes_df[~nodes_df['category'].isin(invalid_node_categories)]

    nodes_df.to_csv(nodes, sep='\t', index=False)

    edges_df = pandas.read_csv(f"data/monarch/{edgefile}", sep='\t', dtype="string",
                               quoting=csv.QUOTE_NONE, lineterminator="\n")
    edges_df.drop(
        edges_df.columns.difference(['id', 'subject', 'predicate', 'object',
                                     'category', 'relation', 'primary_knowledge_source',
                                     'aggregator_knowledge_source']),
        axis=1,
        inplace=True
    )

    edges_df = edges_df[edges_df["predicate"].str.contains(":")]

    # assign level association category if edge category is empty
    edges_df['category'].fillna('biolink:Association', inplace=True)
    valid_predicates = {f"biolink:{convert_to_snake_case(pred)}" for pred in biolink_model_schema.slot_descendants("related to")}
    phenio_predicates = set(edges_df['predicate'].unique())
    invalid_predicates = phenio_predicates - valid_predicates
    if invalid_predicates:
        logger.error(f"Invalid predicates found in Phenio associations: {invalid_predicates}")
        invalid_edges_df = edges_df[edges_df['predicate'].isin(invalid_predicates)]
        logger.error(f"Removing {invalid_edges_df.shape[0]} edges with invalid predicates")
        edges_df = edges_df[~edges_df['predicate'].isin(invalid_predicates)]

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
        # if log: logger.removeHandler(fh)    
        raise FileNotFoundError("Phenio transform did not produce the expected output")

    # if log: logger.removeHandler(fh)


def transform_all(
    output_dir: str = OUTPUT_DIR,
    row_limit: Optional[int] = None,
    rdf: bool = False,
    force: bool = False,
    verbose: bool = None,
    log: bool = False,
    ):

    # if log: fh = add_log_fh(logger, Path(f"logs/all_ingests.log"))
    logger = get_logger(name = "all_ingests" if log else None, verbose=verbose)
    
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
                ingest=ingest,
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
        
    # if log: logger.removeHandler(fh)


def merge_files(
    name: str = "monarch-kg",
    input_dir: str = f"{OUTPUT_DIR}/transform_output",
    output_dir: str = OUTPUT_DIR,
    verbose: bool = None,
    ):
    logger = get_logger(None, verbose)
    logger.info("Generating mappings...")

    mappings = []
    mappings.append("data/monarch/mondo.sssom.tsv")
    mappings.append("data/monarch/gene_mappings.tsv")
    mappings.append("data/monarch/chebi-mesh.biomappings.sssom.tsv")

    logger.info("Merging knowledge graph...")

    merge(
        name=name,
        source=input_dir,
        output_dir=output_dir,
        mappings=mappings
    )


def apply_closure(
        name: str = "monarch-kg",
        closure_file: str = f"data/monarch/phenio-relation-filtered.tsv",
        output_dir: str = OUTPUT_DIR
    ):
    
    output_file = f"{output_dir}/{name}-denormalized-edges.tsv"
    add_closure(kg_archive=f"{output_dir}/{name}.tar.gz",
                closure_file=closure_file,
                output_file=output_file)
    sh.gzip(output_file)


def load_sqlite():
    sh.bash("scripts/load_sqlite.sh")


def load_solr():
    sh.bash("scripts/load_solr.sh")


def do_release(dir: str = OUTPUT_DIR, kghub: bool = False):
    import datetime
    release_name = datetime.datetime.now().strftime("%Y-%m-%d")
    
    logger = get_logger()
    logger.info(f"Creating dated release: {release_name}...")

    try:
        logger.debug(f"Uploading release to Google bucket...")

        sh.touch(f"{dir}/{release_name}")
        
        # copy to monarch-archive bucket
        sh.gsutil('-q', '-m', 'cp', '-r', f"{dir}/*", f'gs://monarch-archive/monarch-kg-dev/{release_name}')

        # copy to data-public bucket
        sh.gsutil("-q", "-m", "cp", "-r", f"gs://monarch-archive/monarch-kg-dev/{release_name}", f"gs://data-public-monarchinitiative/monarch-kg-dev/{release_name}")

        # update "latest" 
        sh.gsutil("-q", "-m", "rm", "-rf", f"gs://data-public-monarchinitiative/monarch-kg-dev/latest")
        sh.gsutil("-q", "-m", "cp", "-r", f"gs://data-public-monarchinitiative/monarch-kg-dev/{release_name}", "gs://data-public-monarchinitiative/monarch-kg-dev/latest")
        
        # index and upload to kghub s3 bucket
        if kghub:
            sh.multi_indexer('-v', '--directory', dir, '--prefix', f'https://kg-hub.berkeleybop.io/kg-monarch/{release_name}', '-x', '-u')
            sh.gsutil("-q", "-m", "cp", "-r", f"{dir}/*", f"s3://kg-hub-public-data/kg-monarch/{release_name}")
            sh.gsutil("-q", "-m", "cp", "-r", f"{dir}/*", f"s3://kg-hub-public-data/kg-monarch/current")


        logger.debug("Cleaning up files...")
        sh.rm(f"output/{release_name}")

        logger.info(f"Successfuly uploaded release!")
    except BaseException as e:
        logger.error(f"Oh no! Something went wrong:\n\t{e}")
