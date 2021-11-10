import uuid

from biolink_model_pydantic.model import (
    Gene,
    NamedThingToInformationContentEntityAssociation,
    Predicate,
    Publication,
)
from koza.cli_runner import koza_app

source_name = "sgd_gene_to_publication"

row = koza_app.get_row(source_name)

gene = Gene(id='SGD:' + row["gene name"], source="infores:sgd")

publication = Publication(
    id="PMID:" + row["PubMed ID"],
    type=koza_app.translation_table.resolve_term("publication"),
    source="infores:sgd"
)

association = NamedThingToInformationContentEntityAssociation(
    id="uuid:" + str(uuid.uuid1()),
    subject=gene.id,
    predicate=Predicate.mentions,
    object=publication.id,
    relation=koza_app.translation_table.resolve_term("mentions"),
    source="infores:sgd",
)

koza_app.write(gene, publication, association)
