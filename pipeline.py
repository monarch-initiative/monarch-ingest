import os
from os.path import exists
from typing import List
import dagster
from koza.cli_runner import transform_source
from kgx.cli import cli_utils


@dagster.usable_as_dagster_type
class ValidatedKozaOutput:
    def __init__(self, nodes_file, edges_file):
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
def transform(ingest: Ingest) -> ValidatedKozaOutput:
   transform_source(f"./monarch_ingest/{ingest.source}/{ingest.transform}.yaml", "output", "tsv", None, None)
   return ValidatedKozaOutput(f"output/{ingest.source}_{ingest.transform}_nodes.tsv", f"output/{ingest.source}_{ingest.transform}_edges.tsv")

@dagster.op
def validate(kgx: ValidatedKozaOutput) -> ValidatedKozaOutput:
    cli_utils.validate([kgx.nodes_file, kgx.edges_file], "tsv", None, None, True, None)
    return kgx

@dagster.op
def merge(merge_files: List[ValidatedKozaOutput]):
    # TODO: call merge from python directly, only including sources passed in here?
    os.system("kgx merge --merge-config merge.yaml --processes 4")

@dagster.graph
def process(ingest: Ingest) -> ValidatedKozaOutput:
    return validate(transform(ingest))

# TODO: replace this hardcoded list with configuration
@dagster.op(
    out=dagster.DynamicOut(Ingest),
)
def ingests(context):
    ingests = [
        Ingest("alliance", "literature"),
        Ingest("alliance", "gene_information"),
        Ingest("alliance", "gene_to_phenotype"),
        Ingest("rgd", "gene_to_publication"),
        Ingest("hgnc", "gene_information"),
        Ingest("flybase", "gene_to_publication"),
        Ingest("pombase", "gene_to_phenotype"),
        Ingest("sgd", "gene_to_publication"),
        Ingest("xenbase", "gene_information"),
        Ingest("xenbase", "gene_to_phenotype"),
        Ingest("xenbase", "gene_to_publication"),
        Ingest("zfin","gene_to_phenotype"),
        Ingest("zfin","gene_to_publication"),
    ]

    for ingest in ingests:
        yield dagster.DynamicOutput(ingest, mapping_key=ingest.name)

@dagster.job
def monarch_ingest_pipline():
    processed_ingests = ingests().map(process)
    merge(processed_ingests.collect())






