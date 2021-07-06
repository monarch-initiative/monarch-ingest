import uuid

from biolink_model_pydantic.model import (
    Gene,
    GeneToPhenotypicFeatureAssociation,
    PhenotypicFeature,
    Predicate,
)
from koza.manager.data_collector import write
from koza.manager.data_provider import inject_row, inject_translation_table

source_name = "gene-to-phenotype"

translation_table = inject_translation_table()
row = inject_row(source_name)

gene = Gene(id="POMBASE:" + row["Gene systematic ID"])
phenotype = PhenotypicFeature(id=row["FYPO ID"])
association = GeneToPhenotypicFeatureAssociation(
    id="uuid:" + str(uuid.uuid1()),
    subject=gene.id,
    predicate=Predicate.has_phenotype,
    object=phenotype.id,
    relation=translation_table.resolve_term("has phenotype"),
    publications=[row["Reference"]],
)

if row["Condition"]:
    association.qualifiers = row["Condition"].split(",")

write(source_name, gene, phenotype, association)
