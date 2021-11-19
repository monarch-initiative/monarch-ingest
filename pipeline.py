
import os
from dagster import ModeDefinition, InputDefinition, Nothing, default_executors, multiprocess_executor, fs_io_manager, pipeline, solid, composite_solid
from koza.cli_runner import transform_source

mode_defs = [
    ModeDefinition(
        resource_defs={"io_manager": fs_io_manager},
        executor_defs=[multiprocess_executor],
    )
]


@solid
def ingest_xenbase_gene_literature():
    transform_source("./monarch_ingest/xenbase/gene_literature.yaml",
                     "output", "tsv", None, None)
    return 1 # This is a hack, we don't really have natural return values, but Dagster wants them


@solid
def ingest_xenbase_gene_information():
    transform_source("./monarch_ingest/xenbase/gene_information.yaml",
                     "output", "tsv", None, None)
    return 1 # This is a hack, we don't really have natural return values, but Dagster wants them


@solid
def ingest_xenbase_gene2phenotype():
    transform_source("./monarch_ingest/xenbase/gene2phenotype.yaml",
                     "output", "tsv", None, None)
    return 1 # This is a hack, we don't really have natural return values, but Dagster wants them


@solid
def ingest_alliance_literature():
    transform_source("./monarch_ingest/alliance/literature.yaml",
                     "output", "tsv", None, None)
    return 1 # This is a hack, we don't really have natural return values, but Dagster wants them


@solid
def ingest_alliance_gene_information():
    transform_source("./monarch_ingest/alliance/gene_information.yaml",
                     "output", "tsv", None, None)
    return 1 # This is a hack, we don't really have natural return values, but Dagster wants them

# @solid
# def ingest_alliance_gene2disease():
#     transform_source("./monarch_ingest/alliance/gene2disease.yaml",
#                      "output", "tsv", None, None)
#     return 1 # This is a hack, we don't really have natural return values, but Dagster wants them


@solid
def ingest_alliance_gene2phenotype():
    transform_source("./monarch_ingest/alliance/gene2phenotype.yaml",
                     "output", "tsv", None, None)
    return 1 # This is a hack, we don't really have natural return values, but Dagster wants them


@solid
def ingest_rgd_gene2publication():
    transform_source("./monarch_ingest/rgd/gene2publication.yaml",
                     "output", "tsv", None, None)
    return 1 # This is a hack, we don't really have natural return values, but Dagster wants them


@solid
def ingest_hgnc_gene_information():
    transform_source("./monarch_ingest/hgnc/gene_information.yaml",
                     "output", "tsv", None, None)
    return 1 # This is a hack, we don't really have natural return values, but Dagster wants them


@solid
def ingest_flybase_gene2publication():
    transform_source("./monarch_ingest/flybase/gene2publication.yaml",
                     "output", "tsv", None, None)
    return 1 # This is a hack, we don't really have natural return values, but Dagster wants them


@solid
def ingest_sgd_gene2publication():
    transform_source("./monarch_ingest/sgd/gene2publication.yaml",
                     "output", "tsv", None, None)
    return 1 # This is a hack, we don't really have natural return values, but Dagster wants them


@solid
def ingest_pombase_gene2phenotype():
    transform_source("./monarch_ingest/pombase/gene2phenotype.yaml",
                     "output", "tsv", None, None)
    return 1 # This is a hack, we don't really have natural return values, but Dagster wants them


@solid
def ingest_zfin_gene2publication():
    transform_source("./monarch_ingest/zfin/gene2publication.yaml",
                     "output", "tsv", None, None)
    return 1 # This is a hack, we don't really have natural return values, but Dagster wants them


@solid
def ingest_zfin_gene2phenotype():
    transform_source("./monarch_ingest/zfin/gene2phenotype.yaml",
                     "output", "tsv", None, None)
    return 1 # This is a hack, we don't really have natural return values, but Dagster wants them


@solid
def merge(placeholder_input):
    os.system("kgx merge --merge-config merge.yaml --processes 4")

@pipeline(mode_defs=mode_defs)
def monarch_ingest_pipeline():
    merge([ingest_xenbase_gene_literature(), ingest_xenbase_gene_information(), ingest_xenbase_gene2phenotype(), ingest_alliance_literature(), ingest_alliance_gene_information(), ingest_alliance_gene2phenotype(), ingest_rgd_gene2publication(), ingest_hgnc_gene_information(), ingest_flybase_gene2publication(), ingest_sgd_gene2publication(), ingest_pombase_gene2phenotype(), ingest_zfin_gene2publication(), ingest_zfin_gene2phenotype()])

