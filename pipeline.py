import os
from dagster import op, job
from koza.cli_runner import transform_source

@op
def ingest_xenbase_gene_literature():
    transform_source("./monarch_ingest/xenbase/gene_literature.yaml",
                     "output", "tsv", None, None)
    return 1 # This is a hack, we don't really have natural return values, but Dagster wants them


@op
def ingest_xenbase_gene_information():
    transform_source("./monarch_ingest/xenbase/gene_information.yaml",
                     "output", "tsv", None, None)
    return 1 # This is a hack, we don't really have natural return values, but Dagster wants them


@op
def ingest_xenbase_gene2phenotype():
    transform_source("./monarch_ingest/xenbase/gene2phenotype.yaml",
                     "output", "tsv", None, None)
    return 1 # This is a hack, we don't really have natural return values, but Dagster wants them


@op
def ingest_alliance_literature():
    transform_source("./monarch_ingest/alliance/literature.yaml",
                     "output", "tsv", None, None)
    return 1 # This is a hack, we don't really have natural return values, but Dagster wants them


@op
def ingest_alliance_gene_information():
    transform_source("./monarch_ingest/alliance/gene_information.yaml",
                     "output", "tsv", None, None)
    return 1 # This is a hack, we don't really have natural return values, but Dagster wants them

# @op
# def ingest_alliance_gene2disease():
#     transform_source("./monarch_ingest/alliance/gene2disease.yaml",
#                      "output", "tsv", None, None)
#     return 1 # This is a hack, we don't really have natural return values, but Dagster wants them


@op
def ingest_alliance_gene2phenotype():
    transform_source("./monarch_ingest/alliance/gene2phenotype.yaml",
                     "output", "tsv", None, None)
    return 1 # This is a hack, we don't really have natural return values, but Dagster wants them


@op
def ingest_rgd_gene2publication():
    transform_source("./monarch_ingest/rgd/gene2publication.yaml",
                     "output", "tsv", None, None)
    return 1 # This is a hack, we don't really have natural return values, but Dagster wants them


@op
def ingest_hgnc_gene_information():
    transform_source("./monarch_ingest/hgnc/gene_information.yaml",
                     "output", "tsv", None, None)
    return 1 # This is a hack, we don't really have natural return values, but Dagster wants them


@op
def ingest_flybase_gene2publication():
    transform_source("./monarch_ingest/flybase/gene2publication.yaml",
                     "output", "tsv", None, None)
    return 1 # This is a hack, we don't really have natural return values, but Dagster wants them


@op
def ingest_sgd_gene2publication():
    transform_source("./monarch_ingest/sgd/gene2publication.yaml",
                     "output", "tsv", None, None)
    return 1 # This is a hack, we don't really have natural return values, but Dagster wants them


@op
def ingest_pombase_gene2phenotype():
    transform_source("./monarch_ingest/pombase/gene2phenotype.yaml",
                     "output", "tsv", None, None)
    return 1 # This is a hack, we don't really have natural return values, but Dagster wants them


@op
def ingest_zfin_gene2publication():
    transform_source("./monarch_ingest/zfin/gene2publication.yaml",
                     "output", "tsv", None, None)
    return 1 # This is a hack, we don't really have natural return values, but Dagster wants them


@op
def ingest_zfin_gene2phenotype():
    transform_source("./monarch_ingest/zfin/gene2phenotype.yaml",
                     "output", "tsv", None, None)
    return 1 # This is a hack, we don't really have natural return values, but Dagster wants them


@op
def merge(placeholder_input):
    os.system("kgx merge --merge-config merge.yaml --processes 4")

@job()
def monarch_ingest_pipeline():
    merge([ingest_xenbase_gene_literature(),
           ingest_xenbase_gene_information(),
           ingest_xenbase_gene2phenotype(),
           ingest_alliance_literature(),
           ingest_alliance_gene_information(),
           ingest_alliance_gene2phenotype(),
           ingest_rgd_gene2publication(),
           ingest_hgnc_gene_information(),
           ingest_flybase_gene2publication(),
           ingest_sgd_gene2publication(),
           ingest_pombase_gene2phenotype(),
           ingest_zfin_gene2publication(),
           ingest_zfin_gene2phenotype()])

