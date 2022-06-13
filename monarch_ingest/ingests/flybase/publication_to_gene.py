import uuid

from koza.cli_runner import koza_app

from monarch_ingest.model.biolink import (
    Gene,
    InformationContentEntityToNamedThingAssociation,
    Publication,
)

source_name = "flybase_publication_to_gene"

row = koza_app.get_row(source_name)

if not row["entity_id"].startswith('FBgn'):
    koza_app.next_row()


gene = Gene(id='FB:' + row["entity_id"], source="infores:flybase")

if row["PubMed_id"]:
    publication_id = "PMID:" + row["PubMed_id"]
else:
    publication_id = "FB:" + row["FlyBase_publication_id"]

publication = Publication(
    id=publication_id,
    type=koza_app.translation_table.resolve_term("publication"),
    source="infores:flybase",
)
relation = koza_app.translation_table.resolve_term("mentions")

association = InformationContentEntityToNamedThingAssociation(
    id="uuid:" + str(uuid.uuid1()),
    subject=gene.id,
    predicate="biolink:mentions",
    object=publication.id,
    aggregating_knowledge_source="infores:monarchinitiative",
    primary_knowledge_source="infores:flybase",
)

koza_app.write(association)
