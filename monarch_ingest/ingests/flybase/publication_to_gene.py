import uuid

from koza.cli_runner import koza_app

from biolink.pydanticmodel import InformationContentEntityToNamedThingAssociation

source_name = "flybase_publication_to_gene"

row = koza_app.get_row(source_name)

if not row["entity_id"].startswith('FBgn'):
    koza_app.next_row()

gene_id = 'FB:' + row["entity_id"]

if row["PubMed_id"]:
    publication_id = "PMID:" + row["PubMed_id"]
else:
    publication_id = "FB:" + row["FlyBase_publication_id"]

association = InformationContentEntityToNamedThingAssociation(
    id="uuid:" + str(uuid.uuid1()),
    subject=gene_id,
    predicate="biolink:mentions",
    object=publication_id,
    aggregator_knowledge_source=["infores:monarchinitiative"],
    primary_knowledge_source="infores:flybase",
)

koza_app.write(association)
