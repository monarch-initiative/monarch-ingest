import multiprocessing
import os
from os.path import exists
from typing import List

import dagster
import yaml
from kghub_downloader.download_utils import download_from_yaml
from kgx.cli import cli_utils
from koza.cli_runner import transform_source
from koza.model.config.source_config import OutputFormat


@dagster.usable_as_dagster_type
class KgxGraph:
    def __init__(
        self, name, nodes_file, edges_file, has_node_properties, has_edge_properties
    ):
        self.name = name
        self.nodes_file = nodes_file
        self.edges_file = edges_file
        self.has_node_properties = has_node_properties
        self.has_edge_properties = has_edge_properties
        assert has_node_properties or has_edge_properties
        if has_node_properties:
            assert exists(nodes_file)
        if has_edge_properties:
            assert exists(edges_file)


@dagster.usable_as_dagster_type
class Ingest:
    def __init__(self, source, transform):
        self.source = source
        self.transform = transform
        self.name = f"{source}_{transform}"
        self.source_file = f"./monarch_ingest/{source}/{transform}.yaml"

        assert exists(self.source_file)

        with open(self.source_file) as sfh:
            self.source_config = yaml.load(sfh, yaml.FullLoader)
        self.has_node_properties = "node_properties" in self.source_config
        self.has_edge_properties = "edge_properties" in self.source_config

        assert self.source
        assert self.transform

        assert self.has_edge_properties or self.has_node_properties


@dagster.op
def transform(ingest: Ingest) -> KgxGraph:

    nodes_file = f"output/{ingest.source}_{ingest.transform}_nodes.tsv"
    edges_file = f"output/{ingest.source}_{ingest.transform}_edges.tsv"

    # For efficiency, only run the transform if the files output kgx files aren't there
    # This matches the current download behavior of only downloading files when they
    # aren't present - which expects that when running on a server as a production
    # job this happens in a fresh Docker container with no data.
    if not os.path.exists(nodes_file) or not os.path.exists(edges_file):
        transform_source(
            source=f"./monarch_ingest/{ingest.source}/{ingest.transform}.yaml",
            output_dir="output",
            output_format=OutputFormat.tsv,
            local_table=None,
            global_table=None,
            # row_limit=100  # TODO: Ideally we can make this a part of running the pipeline in a developer mode
        )

    return KgxGraph(
        ingest.name,
        nodes_file,
        edges_file,
        ingest.has_node_properties,
        ingest.has_edge_properties,
    )


@dagster.op
def validate(kgx: KgxGraph) -> KgxGraph:

    files = []
    if kgx.has_node_properties:
        files.append(kgx.nodes_file)
    if kgx.has_edge_properties:
        files.append(kgx.edges_file)

    cli_utils.validate(
        inputs=files,
        input_format="tsv",
        input_compression=None,
        output=None,
        stream=True,
        biolink_release="2.2.13",
    )  # TODO: we should put the biolink version in the model class
    return kgx


@dagster.op
def summarize(kgx: KgxGraph) -> KgxGraph:

    files = []
    if kgx.has_node_properties:
        files.append(kgx.nodes_file)
    if kgx.has_edge_properties:
        files.append(kgx.edges_file)

    cli_utils.graph_summary(
        inputs=files,
        input_format="tsv",
        input_compression=None,
        output=f"output/{kgx.name}_graph_stats.yaml",
        report_type="kgx-map",
        report_format="yaml",
        stream=True
    )
    return kgx


@dagster.op
def merge(context, merge_files: List[KgxGraph]):
    # TODO:
    #  Consider writing a merge.yaml using a jinja template
    #  This multiprocessing statement may not be meaningful longer term
    cli_utils.merge("merge.yaml", processes=multiprocessing.cpu_count())


@dagster.graph
def process(ingest: Ingest) -> KgxGraph:
    # temporarily removing validation for performance reasons, it's taking 2-3x as long as the ingest
    return summarize(transform(ingest))


@dagster.op(
    ins={"start": dagster.In(dagster.Nothing)},
    out=dagster.DynamicOut(Ingest),
)
def ingests(context):
    ingests = [
        Ingest("alliance", "gene"),
        Ingest("alliance", "gene_to_phenotype"),
        Ingest("alliance", "publication"),
        Ingest("ctd", "chemical_to_disease"),
        Ingest("flybase", "publication_to_gene"),
        Ingest("goa", "go_annotation"),
        Ingest("hgnc", "gene"),
        Ingest("hpoa", "disease_phenotype"),
        Ingest("mgi", "publication_to_gene"),
        Ingest("omim", "gene_to_disease"),
        Ingest("panther", "ref_genome_orthologs"),
        Ingest("pombase", "gene"),
        Ingest("pombase", "gene_to_phenotype"),
        Ingest("reactome", "chemical_to_pathway"),
        Ingest("reactome", "gene_to_pathway"),
        Ingest("rgd", "publication_to_gene"),
        Ingest("sgd", "publication_to_gene"),
        Ingest("string", "protein_links"),
        Ingest("xenbase", "gene"),
        Ingest("xenbase", "gene_to_phenotype"),
        Ingest("xenbase", "publication_to_gene"),
        Ingest("zfin", "gene_to_phenotype"),
        Ingest("zfin", "publication_to_gene"),
    ]

    for ingest in ingests:
        yield dagster.DynamicOutput(ingest, mapping_key=ingest.name)


@dagster.op()
def download():
    download_from_yaml(yaml_file="download.yaml", output_dir=".")

    # Until we have an explicit place for pre-ETL steps, they can go here.
    if not os.path.exists("./data/alliance/alliance_gene_ids.txt.gz"):
        os.system(
            "gzcat data/alliance/BGI_*.gz | jq '.data[].basicGeneticEntity.primaryId' | gzip > data/alliance/alliance_gene_ids.txt.gz"
        )



@dagster.job
def monarch_ingest_pipeline():
    processed_ingests = ingests(start=download()).map(process)
    merge(processed_ingests.collect())
