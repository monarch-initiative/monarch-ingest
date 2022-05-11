import uuid

from koza.cli_runner import koza_app

from model.biolink import Gene, GeneToPhenotypicFeatureAssociation, PhenotypicFeature

source_name = "pombase_gene_to_phenotype"

row = koza_app.get_row(source_name)

gene = Gene(id="PomBase:" + row["Gene systematic ID"], source="infores:pombase")
phenotype = PhenotypicFeature(id=row["FYPO ID"], source="infores:pombase")
association = GeneToPhenotypicFeatureAssociation(
    id="uuid:" + str(uuid.uuid1()),
    subject=gene.id,
    predicate="biolink:has_phenotype",
    object=phenotype.id,
    relation=koza_app.translation_table.resolve_term("has phenotype"),
    publications=[row["Reference"]],
    source="infores:pombase",
)

if row["Condition"]:
    association.qualifiers = row["Condition"].split(",")

koza_app.write(association)
