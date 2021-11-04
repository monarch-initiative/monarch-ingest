import uuid

from biolink_model_pydantic.model import (
    Gene,
    GeneToPhenotypicFeatureAssociation,
    PhenotypicFeature,
    Predicate,
)
from koza.cli_runner import koza_app

source_name = "xenbase_gene_to_phenotype"

row = koza_app.get_row(source_name)

# Not including qualifiers, as none are present in the input file. If they show up,
# we'll want to examine the values before including them in the output of this transform
if row["QUALIFIER"]:
    raise ValueError("Didn't expect a qualifier value, found: " + row["QUALIFIER"])

gene = Gene(id=row["SUBJECT"], source="Xenbase")

phenotype = PhenotypicFeature(id=row["OBJECT"], source="Xenbase")

association = GeneToPhenotypicFeatureAssociation(
    id="uuid:" + str(uuid.uuid1()),
    subject=gene.id,
    predicate=Predicate.has_phenotype,
    object=phenotype.id,
    publications=row["SOURCE"],
    relation=row["RELATION"].replace("_", ":"),
    source="Xenbase",
)

if row["SOURCE"]:
    association.publications = [row["SOURCE"]]

koza_app.write(gene, association, phenotype)
