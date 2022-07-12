import uuid

from koza.cli_runner import koza_app

from biolink.pydanticmodel import GeneToPhenotypicFeatureAssociation

source_name = "pombase_gene_to_phenotype"

row = koza_app.get_row(source_name)

gene_id = "PomBase:" + row["Gene systematic ID"]

phenotype_id = row["FYPO ID"]

association = GeneToPhenotypicFeatureAssociation(
    id="uuid:" + str(uuid.uuid1()),
    subject=gene_id,
    predicate="biolink:has_phenotype",
    object=phenotype_id,
    publications=[row["Reference"]],
    aggregator_knowledge_source=["infores:monarchinitiative"],
    primary_knowledge_source="infores:pombase"
)

if row["Condition"]:
    association.qualifiers = row["Condition"].split(",")

koza_app.write(association)
