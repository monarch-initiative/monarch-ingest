import uuid

from biolink_model_pydantic.model import (
    Gene,
    NamedThingToInformationContentEntityAssociation,
    Predicate,
    Publication,
)
from koza.cli_runner import koza_app

source_name = "flybase_gene_to_publication"

row = koza_app.get_row(source_name)

if not row["entity_id"].startswith('FBgn'):
    koza_app.next_row()


gene = Gene(id='FB:' + row["entity_id"])

if row["PubMed_id"]:
    publication_id = "PMID:" + row["PubMed_id"]
else:
    publication_id = "FB:" + row["FlyBase_publication_id"]

publication = Publication(
        id=publication_id,
        type=koza_app.translation_table.resolve_term("publication"),
        source="FB",
)

association = NamedThingToInformationContentEntityAssociation(
    id="uuid:" + str(uuid.uuid1()),
    subject=gene.id,
    predicate=Predicate.mentions,
    object=publication.id,
    relation=koza_app.translation_table.resolve_term("mentions"),
    source="FB"
)

koza_app.write(gene, publication, association)
