
import uuid
from typing import List

from biolink.pydanticmodel import (
    Gene,
    GeneToPhenotypicFeatureAssociation,
    PhenotypicFeature,
)
from koza.cli_runner import koza_app

# include logging if necessary
from loguru import logger

# the source name is used below to manage the reading and writing of files
source_name = "gene-to-phenotype"

# get a row
row = koza_app.get_row(source_name)
# inject a map by name, assuming it's been configured by path in the yaml
# koza_app.get_map('map_name')

# Why not log something!
if row["some"]["property"] != 'what I expected':
    logger.warning("Whoa dude, let's log it")

# create entities
gene_id = row["gene_id"]
phenotypicFeature_id = row["phenotype"]["id"]

# Optionally, add publications
publications: List[str] =["PMID:1", "PMID:2"]

# create the association
association = GeneToPhenotypicFeatureAssociation(
    id="uuid:" + str(uuid.uuid1()),
    subject=gene_id,
    predicate="biolink:has_phenotype",
    object=phenotypicFeature_id,
    publications=publications,
    aggregator_knowledge_source=["infores:monarchinitiative"],
    primary_knowledge_source="infores:model_organism_db"
)

koza_app.write(association)
