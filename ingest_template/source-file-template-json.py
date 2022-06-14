import logging
import uuid

from biolink_model_pydantic.model import (
    Gene,
    GeneToPhenotypicFeatureAssociation,
    PhenotypicFeature,
)
from koza.cli_runner import koza_app

# include logging if necessary
LOG = logging.getLogger(__name__)

# the source name is used below to manage the reading and writing of files
source_name = "gene-to-phenotype"

# get a row
row = koza_app.get_row(source_name)
# inject a map by name, assuming it's been configured by path in the yaml
# koza_app.get_map('map_name')

# Why not log something!
if row["some"]["property"] != 'what I expected':
    LOG.warning("Whoa dude, let's log it")

# create entities
gene = Gene(id=row["gene_id"])
phenotypicFeature = PhenotypicFeature(id=row["phenotype"]["id"])

# create the association
association = GeneToPhenotypicFeatureAssociation(
    id="uuid:" + str(uuid.uuid1()),
    subject=gene.id,
    predicate="biolink:has_phenotype",
    object=phenotypicFeature.id,
    relation=koza_app.translation_table.resolve_term("has phenotype"),
)

# don't forget to pass the source_name as the first argument, followed by entities
koza_app.write(gene, phenotypicFeature, association)
