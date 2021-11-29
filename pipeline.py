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

        assert self.source
        assert self.transform
        assert exists(f"./monarch_ingest/{source}/{transform}.yaml")



@dagster.op
def pombase_gene_to_phenotype() -> Ingest:
    return Ingest("pombase", "gene_to_phenotype")

@dagster.op
def xenbase_gene_information() -> Ingest:
    return Ingest("xenbase", "gene_information")

@dagster.op
def xenbase_gene_to_phenotype() -> Ingest:
    return Ingest("xenbase", "gene_to_phenotype")

#TODO: the rest:
# ingest_xenbase_gene_literature(),
# ingest_alliance_literature(),
# ingest_alliance_gene_information(),
# ingest_alliance_gene2phenotype(),
# ingest_rgd_gene2publication(),
# ingest_hgnc_gene_information(),
# ingest_flybase_gene2publication(),
# ingest_sgd_gene2publication(),
# ingest_pombase_gene2phenotype(),
# ingest_zfin_gene2publication(),
# ingest_zfin_gene2phenotype()



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
    # TODO: call merge from python directly, only including sources defined here?
    os.system("kgx merge --merge-config merge.yaml --processes 4")

@dagster.job
def monarch_ingest_pipeline():
    # TODO:
    #  Rather than exhaustively enumerating with biolerplate code, this should be coming
    #  from configuration https://docs.dagster.io/concepts/configuration/config-schema
    merge([
        validate.alias("validate_pombase_gene_to_phenotype")(
            transform.alias("transform_pombase_gene_to_phenotype")(pombase_gene_to_phenotype())),
        validate.alias("validate_xenbase_gene_information")(
            transform.alias("transform_xenbase_gene_information")(xenbase_gene_information())),
        validate.alias("validate_xenbase_gene_to_phenotype")(
            transform.alias("transform_xenbase_gene_to_phenotype")(xenbase_gene_to_phenotype()))
    ])





