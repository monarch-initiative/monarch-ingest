import csv
import gc
import os
import pathlib
import tarfile
from pathlib import Path
from typing import Optional
from biolink import model  # import the pythongen biolink model to get the version
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
from monarch_ingest.utils.export_utils import export

# from koza.utils.log_utils import get_logger


OUTPUT_DIR = "output"


def transform_one(
    ingest: str = None,
    output_dir: str = OUTPUT_DIR,
    row_limit: int = None,
    rdf: bool = False,
    force: bool = False,
    verbose: bool = None,
    log: bool = False,
):
    logger = get_logger(name=ingest if log else None, verbose=verbose)

    ingests = get_ingests()

    if ingest not in ingests:
        # if log: logger.removeHandler(fh)
        raise ValueError(f"{ingest} is not a valid ingest - see ingests.yaml for a list of options")

    source_file = Path(Path(__file__).parent, ingests[ingest]["config"])

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
    logger = get_logger(name="phenio" if log else None, verbose=verbose)

    # TODO: can this be fetched from a purl?
    biolink_model_schema = SchemaView(
        f"https://raw.githubusercontent.com/biolink/biolink-model/v{model.version}/biolink-model.yaml"
    )

    phenio_tar = "data/monarch/kg-phenio.tar.gz"
    if not Path(phenio_tar).is_file():
        # if log: logger.removeHandler(fh)
        raise FileNotFoundError("data/monarch/kg-phenio.tar.gz")

    nodefile = "merged-kg_nodes.tsv"
    edgefile = "merged-kg_edges.tsv"

    tar = tarfile.open(phenio_tar)
    tar.extract(nodefile, "data/monarch")
    tar.extract(edgefile, "data/monarch")

    Path(f"{output_dir}/transform_output").mkdir(parents=True, exist_ok=True)

    nodes = f"{output_dir}/transform_output/phenio_nodes.tsv"
    edges = f"{output_dir}/transform_output/phenio_edges.tsv"

    if (force == False) and file_exists(nodes) and file_exists(edges):
        logger.info(f"Transformed output exists - skipping ingest: Phenio - To run this ingest anyway, use --force")
        # if log: logger.removeHandler(fh)
        return

    nodes_df = pandas.read_csv(
        f"data/monarch/{nodefile}", sep="\t", dtype="string", quoting=csv.QUOTE_NONE, lineterminator="\n"
    )
    nodes_df = nodes_df[~nodes_df["id"].str.contains("omim.org|hgnc_id")]
    nodes_df = nodes_df[~nodes_df["id"].str.startswith("MGI:")]

    # Hopefully this won't be necessary long term, but these IDs are coming
    # in with odd OBO prefixes from Phenio currently.
    obo_prefixes_to_repair = ["FBbt", "WBbt", "ZFA", "XAO"]
    for prefix in obo_prefixes_to_repair:
        nodes_df["id"] = nodes_df["id"].str.replace(f"OBO:{prefix}_", f"{prefix}:")

    # These bring in nodes necessary for other ingests, but won't capture the same_as / equivalentClass
    # associations that we'll also need
    exclude_prefixes = ["HGNC", "FlyBase", "http", "biolink"]

    pathlib.Path(f"{output_dir}/qc/").mkdir(parents=True, exist_ok=True)
    excluded_nodes = nodes_df[nodes_df["id"].str.startswith(tuple(exclude_prefixes))]
    nodes_df = nodes_df[~nodes_df["id"].str.startswith(tuple(exclude_prefixes))]

    # Replace biolink:Occurrent category with biolink:BiologicalProcessOrActivity as a fallback to rescue
    # GO nodes that are getting a mixin category of Occurrent that we don't want to exclude all of
    nodes_df["category"] = nodes_df["category"].str.replace("biolink:Occurrent", "biolink:BiologicalProcessOrActivity")

    valid_node_categories = {
        f"biolink:{camelcase(cat)}" for cat in biolink_model_schema.class_descendants("named thing")
    }
    phenio_node_categories = set(nodes_df["category"].unique())
    invalid_node_categories = phenio_node_categories - valid_node_categories
    if invalid_node_categories:
        logger.error(f"Invalid node categories: {invalid_node_categories}")
        invalid_node_categories_df = nodes_df[nodes_df["category"].isin(invalid_node_categories)]
        excluded_nodes = pandas.concat([excluded_nodes, invalid_node_categories_df])
        logger.error(f"Removing {len(invalid_node_categories_df)} nodes with invalid categories")
        nodes_df = nodes_df[~nodes_df["category"].isin(invalid_node_categories)]

    excluded_nodes.to_csv(f"{output_dir}/qc/excluded_phenio_nodes.tsv", sep="\t", index=False)

    nodes_df.to_csv(nodes, sep="\t", index=False)

    edges_df = pandas.read_csv(
        f"data/monarch/{edgefile}", sep="\t", dtype="string", quoting=csv.QUOTE_NONE, lineterminator="\n"
    )
    edges_df.drop(
        edges_df.columns.difference(
            [
                "id",
                "subject",
                "predicate",
                "object",
                "category",
                "relation",
                "primary_knowledge_source",
                "aggregator_knowledge_source",
            ]
        ),
        axis=1,
        inplace=True,
    )

    edges_df = edges_df[edges_df["predicate"].str.contains(":")]

    # assign level association category if edge category is empty
    edges_df["category"].fillna("biolink:Association", inplace=True)

    # Hopefully this won't be necessary long term, but these IDs are coming
    # in with odd OBO prefixes from Phenio currently.
    for prefix in obo_prefixes_to_repair:
        for field in ["subject", "object"]:
            edges_df[field] = edges_df[field].str.replace(f"OBO:{prefix}_", f"{prefix}:")

    # Only keep edges where the subject and object both are within our allowable prefix list
    edges_df = edges_df[
        ~edges_df["subject"].str.startswith(tuple(exclude_prefixes))
        & ~edges_df["object"].str.startswith(tuple(exclude_prefixes))
    ]

    # Remove edges where the subject or object is NA
    edges_df = edges_df[~edges_df["subject"].isna() & ~edges_df["object"].isna()]

    valid_predicates = {
        f"biolink:{convert_to_snake_case(pred)}" for pred in biolink_model_schema.slot_descendants("related to")
    }
    phenio_predicates = set(edges_df["predicate"].unique())
    invalid_predicates = phenio_predicates - valid_predicates
    if invalid_predicates:
        logger.error(f"Invalid predicates found in Phenio associations: {invalid_predicates}")
        invalid_edges_df = edges_df[edges_df["predicate"].isin(invalid_predicates)]
        logger.error(f"Removing {invalid_edges_df.shape[0]} edges with invalid predicates")
        edges_df = edges_df[~edges_df["predicate"].isin(invalid_predicates)]

    valid_edge_categories = {
        f"biolink:{camelcase(cat)}" for cat in biolink_model_schema.class_descendants("association")
    }
    phenio_edge_categories = set(edges_df["category"].unique())
    invalid_edge_categories = phenio_edge_categories - valid_edge_categories
    if invalid_edge_categories:
        logger.error(f"Invalid edge categories: {invalid_edge_categories}")
        invalid_edge_categories_df = edges_df[edges_df["category"].isin(invalid_edge_categories)]
        logger.error(f"Removing {len(invalid_edge_categories_df)} edges with invalid categories")
        edges_df = edges_df[~edges_df["category"].isin(invalid_edge_categories)]

    edges_df.to_csv(edges, sep="\t", index=False)
    Path(f"data/monarch/{nodefile}").unlink()
    Path(f"data/monarch/{edgefile}").unlink()

    if not file_exists(nodes) or not file_exists(edges):
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
    logger = get_logger(name="all_ingests" if log else None, verbose=verbose)

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
    mappings.append("data/monarch/gene_mappings.sssom.tsv")
    mappings.append("data/monarch/mesh_chebi_biomappings.sssom.tsv")

    logger.info("Merging knowledge graph...")

    merge(name=name, source=input_dir, output_dir=output_dir, mappings=mappings)


def apply_closure(
    name: str = "monarch-kg",
    closure_file: str = f"data/monarch/phenio-relation-filtered.tsv",
    output_dir: str = OUTPUT_DIR,
):
    output_file = f"{output_dir}/{name}-denormalized-edges.tsv"
    add_closure(
        kg_archive=f"{output_dir}/{name}.tar.gz",
        closure_file=closure_file,
        output_file=output_file,
        fields=[
            "subject",
            "object",
            "qualifiers",
            "frequency_qualifier",
            "onset_qualifier",
            "sex_qualifier",
            "stage_qualifier",
        ],
        evidence_fields=["has_evidence", "publications"],
        grouping_fields=["subject", "negated", "predicate", "object"],
    )
    sh.pigz(output_file, force=True)


def load_sqlite():
    sh.bash("scripts/load_sqlite.sh")


def load_solr():
    sh.bash("scripts/load_solr.sh")


def load_jsonl():
    biolink_model = SchemaView(
        f"https://raw.githubusercontent.com/biolink/biolink-model/v{model.version}/biolink-model.yaml"
    )

    class_ancestor_dict = {}
    for c in biolink_model.all_classes().values():
        class_ancestor_dict[f"biolink:{camelcase(c.name)}"] = [
            f"biolink:{camelcase(a)}" for a in biolink_model.class_ancestors(c.name)
        ]
    all_slot_names = biolink_model.all_slots().keys()

    with tarfile.open("output/monarch-kg.tar.gz", "r:*") as tar:
        node_path = tar.getmember("monarch-kg_nodes.tsv")
        edge_path = tar.getmember("monarch-kg_edges.tsv")

        with tar.extractfile(node_path) as node_file:  # type: ignore
            nodes_df = pandas.read_csv(node_file, sep="\t", dtype="string", lineterminator="\n", quoting=csv.QUOTE_NONE)
            nodes_df["category"] = nodes_df["category"].map(class_ancestor_dict)
            # for each column in nodes_df, if schemaview says it's multivalued, convert the contents to a list splitting on |
            for col in nodes_df.columns:
                if col.replace("_", " ") in all_slot_names:
                    slot = biolink_model.induced_slot(col.replace("_", " "))
                    if slot and slot.multivalued and col != "category":
                        nodes_df[col] = nodes_df[col].str.split("|")
            nodes_df.to_json("output/monarch-kg_nodes.jsonl", orient="records", lines=True)
            del nodes_df
            gc.collect()

        with tar.extractfile(edge_path) as edge_file:  # type: ignore
            edges_df = pandas.read_csv(
                edge_file, sep="\t", dtype="string", lineterminator="\n", quoting=csv.QUOTE_NONE, comment="#"
            )
            edges_df["category"] = edges_df["category"].map(class_ancestor_dict)

            for col in edges_df.columns:
                if col.replace("_", " ") in all_slot_names:
                    # lookup using spaces rather than underscores
                    slot = biolink_model.induced_slot(col.replace("_", " "))
                    if slot and slot.multivalued and col != "category":
                        edges_df[col] = edges_df[col].str.split("|")

            # Prefixing only these two fields is an odd thing that Translator needs, so
            # they're being duplicated with the prefixes here
            edges_df["biolink:primary_knowledge_source"] = edges_df["primary_knowledge_source"]
            edges_df["biolink:aggregator_knowledge_source"] = edges_df["aggregator_knowledge_source"]
            edges_df.to_json("output/monarch-kg_edges.jsonl", orient="records", lines=True)
            del edges_df
            gc.collect()

    jsonl_tar = tarfile.open("output/monarch-kg.jsonl.tar.gz", "w:gz")
    jsonl_tar.add("output/monarch-kg_nodes.jsonl", arcname="monarch-kg_nodes.jsonl")
    jsonl_tar.add("output/monarch-kg_edges.jsonl", arcname="monarch-kg_edges.jsonl")
    jsonl_tar.close()

    os.remove("output/monarch-kg_nodes.jsonl")
    os.remove("output/monarch-kg_edges.jsonl")


def export_tsv():
    export()


def do_release(dir: str = OUTPUT_DIR, kghub: bool = False):
    import datetime

    release_name = datetime.datetime.now().strftime("%Y-%m-%d")

    logger = get_logger()
    logger.info(f"Creating dated release: {release_name}...")

    try:
        logger.debug(f"Uploading release to Google bucket...")

        sh.touch(f"{dir}/{release_name}")

        # copy to monarch-archive bucket
        sh.gsutil(*f"-q -m cp -r {dir}/* gs://monarch-archive/monarch-kg-dev/{release_name}".split(" "))

        # copy to data-public bucket
        sh.gsutil(
            *"-q -m cp -r".split(" "),
            f"gs://monarch-archive/monarch-kg-dev/{release_name}",
            f"gs://data-public-monarchinitiative/monarch-kg-dev/{release_name}",
        )

        # update "latest"
        sh.gsutil(*"-q -m rm -rf gs://data-public-monarchinitiative/monarch-kg-dev/latest".split(" "))
        sh.gsutil(
            *"-q -m cp -r".split(" "),
            f"gs://data-public-monarchinitiative/monarch-kg-dev/{release_name}",
            "gs://data-public-monarchinitiative/monarch-kg-dev/latest",
        )

        # copy data to monarch-archive bucket only, so that we don't keep so many copies of the same huge files
        sh.gsutil(*f"-q -m cp data gs://monarch-archive/monarch-kg-dev/{release_name}/".split(" "))

        # index and upload to kghub s3 bucket
        if kghub:
            kghub_release_name = release_name.replace("-", "")
            sh.mkdir("-p", f"{dir}/stats")
            sh.mv(f"{dir}/merged_graph_stats.yaml", f"{dir}/stats")
            sh.multi_indexer(
                *f"-v --directory {dir} --prefix https://kg-hub.berkeleybop.io/kg-monarch/{kghub_release_name} -x -u".split(
                    " "
                )
            )
            sh.gsutil(
                *"-q -m -cp -r -a public-read".split(" "),
                f"{dir}/*",  # source files
                f"s3://kg-hub-public-data/kg-monarch/{kghub_release_name}",  # destination
            )
            sh.gsutil(
                *"-q -m cp -r -a public-read".split(" "),  # make public
                f"{dir}/*",  # source files
                "s3://kg-hub-public-data/kg-monarch/current",  # destination
            )

        logger.debug("Cleaning up files...")
        sh.rm(f"output/{release_name}")

        logger.info(f"Successfuly uploaded release!")
    except BaseException as e:
        logger.error(f"Oh no! Something went wrong:\n\t{e}")
