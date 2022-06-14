import uuid

from koza.cli_runner import koza_app

from biolink_model.pydantic.model import (
    Gene,
    GeneToPhenotypicFeatureAssociation,
    PhenotypicFeature
)

source_name = "pombase_gene_to_phenotype"

row = koza_app.get_row(source_name)

gene = Gene(id="PomBase:" + row["Gene systematic ID"], source="infores:pombase")
phenotype = PhenotypicFeature(id=row["FYPO ID"], source="infores:pombase")
#relation = koza_app.translation_table.resolve_term("has phenotype")
association = GeneToPhenotypicFeatureAssociation(
    id="uuid:" + str(uuid.uuid1()),
    subject=gene.id,
    predicate="biolink:has_phenotype",
    object=phenotype.id,
    publications=[row["Reference"]],
    source="infores:pombase",
)

if row["Condition"]:
    association.qualifiers = row["Condition"].split(",")

koza_app.write(association)
