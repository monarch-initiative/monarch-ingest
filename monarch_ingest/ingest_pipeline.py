import os
from os.path import exists
from typing import List

import dagster
from kgx.cli import cli_utils
from koza.cli_runner import transform_source

from monarch_ingest.utils.download_utils import download_from_yaml


@dagster.usable_as_dagster_type
class KgxGraph:
    def __init__(self, name, nodes_file, edges_file):
        self.name = name
        self.nodes_file = nodes_file
        self.edges_file = edges_file
        assert exists(nodes_file)
        assert exists(edges_file)


@dagster.usable_as_dagster_type
class Ingest:
    def __init__(self, source, transform):
        self.source = source
        self.transform = transform
        self.name = f"{source}_{transform}"

        assert self.source
        assert self.transform
        assert exists(f"./monarch_ingest/{source}/{transform}.yaml")


@dagster.op
def transform(ingest: Ingest) -> KgxGraph:
    transform_source(
        f"./monarch_ingest/{ingest.source}/{ingest.transform}.yaml",
        "output",
        "tsv",
        None,
        None,
    )
    return KgxGraph(
        ingest.name,
        f"output/{ingest.source}_{ingest.transform}_nodes.tsv",
        f"output/{ingest.source}_{ingest.transform}_edges.tsv",
    )


@dagster.op
def validate(kgx: KgxGraph) -> KgxGraph:
    cli_utils.validate([kgx.nodes_file, kgx.edges_file], "tsv", None, None, True, None)
    return kgx


@dagster.op
def summarize(kgx: KgxGraph) -> KgxGraph:
    cli_utils.graph_summary(
        [kgx.nodes_file, kgx.edges_file],
        "tsv",
        None,
        f"output/{kgx.name}_graph_stats.yaml",
        "kgx-map",
    )
    return kgx


@dagster.op
def merge(context, merge_files: List[KgxGraph]):
    # TODO:
    #  Consider writing a merge.yaml using a jinja template
    #  This is successfuly filtering what goes into the merge, but it has to exist in the merge.yaml
    #  which limits the benefit.

    sources_to_include = [kgx_graph.name for kgx_graph in merge_files]
    cli_utils.merge("merge.yaml", sources_to_include, processes=4)


@dagster.graph
def process(ingest: Ingest) -> KgxGraph:
    return summarize(validate(transform(ingest)))


@dagster.op(
    ins={"start": dagster.In(dagster.Nothing)},
    out=dagster.DynamicOut(Ingest),
)
def ingests(context):
    ingests = [
        Ingest("alliance", "publication"),
        Ingest("alliance", "gene"),
        Ingest("alliance", "gene_to_phenotype"),
        Ingest("rgd", "gene_to_publication"),
        Ingest("hgnc", "gene"),
        Ingest("flybase", "gene_to_publication"),
        Ingest("pombase", "gene"),
        Ingest("pombase", "gene_to_phenotype"),
        Ingest("sgd", "gene_to_publication"),
        Ingest("xenbase", "gene"),
        Ingest("xenbase", "gene_to_phenotype"),
        Ingest("xenbase", "gene_to_publication"),
        Ingest("zfin", "gene_to_phenotype"),
        Ingest("zfin", "gene_to_publication"),
    ]

    for ingest in ingests:
        yield dagster.DynamicOutput(ingest, mapping_key=ingest.name)


@dagster.op()
def download():
    download_from_yaml(yaml_file="download.yaml", output_dir="data")

    # Until we have an explicit place for pre-ETL steps, they can go here.
    if not os.path.exists("./data/alliance/alliance_gene_ids.txt.gz"):
        os.system(
            "gzcat data/alliance/BGI_*.gz | jq '.data[].basicGeneticEntity.primaryId' | gzip > data/alliance/alliance_gene_ids.txt.gz"
        )


@dagster.job
def monarch_ingest_pipline():
    processed_ingests = ingests(start=download()).map(process)
    merge(processed_ingests.collect())
