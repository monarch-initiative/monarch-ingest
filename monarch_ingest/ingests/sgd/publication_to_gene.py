import uuid

from koza.cli_runner import koza_app

from biolink.pydantic.model import (
    Gene,
    InformationContentEntityToNamedThingAssociation,
    Publication,
)

source_name = "sgd_publication_to_gene"

row = koza_app.get_row(source_name)

gene = Gene(id='SGD:' + row["gene name"], source="infores:sgd")

publication = Publication(
    id="PMID:" + row["PubMed ID"],
    type=koza_app.translation_table.resolve_term("publication"),
    source="infores:sgd",
)

relation = koza_app.translation_table.resolve_term("mentions")
association = InformationContentEntityToNamedThingAssociation(
    id="uuid:" + str(uuid.uuid1()),
    subject=gene.id,
    predicate="biolink:mentions",
    object=publication.id,
    aggregator_knowledge_source=["infores:monarchinitiative"],
    primary_knowledge_source="infores:sgd"
)

koza_app.write(association)
