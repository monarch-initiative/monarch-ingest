import uuid

from biolink_model_pydantic.model import (
    Gene,
    GeneToPhenotypicFeatureAssociation,
    PhenotypicFeature,
    Predicate,
)
from koza.cli_runner import koza_app

source_name = "pombase_gene_to_phenotype"

row = koza_app.get_row(source_name)

gene = Gene(id="POMBASE:" + row["Gene systematic ID"])
phenotype = PhenotypicFeature(id=row["FYPO ID"])
association = GeneToPhenotypicFeatureAssociation(
    id="uuid:" + str(uuid.uuid1()),
    subject=gene.id,
    predicate=Predicate.has_phenotype,
    object=phenotype.id,
    relation=koza_app.translation_table.resolve_term("has phenotype"),
    publications=[row["Reference"]],
)

if row["Condition"]:
    association.qualifiers = row["Condition"].split(",")

koza_app.write(gene, phenotype, association)
