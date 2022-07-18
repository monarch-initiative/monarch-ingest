import uuid

from koza.cli_runner import get_koza_app

from biolink.pydanticmodel import InformationContentEntityToNamedThingAssociation

koza_app = get_koza_app("sgd_publication_to_gene")

row = koza_app.get_row()

gene_id = "SGD:" + row["gene name"]

publication_id = "PMID:" + row["PubMed ID"]

association = InformationContentEntityToNamedThingAssociation(
    id="uuid:" + str(uuid.uuid1()),
    subject=gene_id,
    predicate="biolink:mentions",
    object=publication_id,
    aggregator_knowledge_source=["infores:monarchinitiative"],
    primary_knowledge_source="infores:sgd"
)

koza_app.write(association)
