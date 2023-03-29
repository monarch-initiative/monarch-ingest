import uuid

from koza.cli_runner import get_koza_app

from biolink.pydanticmodel import InformationContentEntityToNamedThingAssociation

koza_app = get_koza_app("flybase_publication_to_gene")

while (row := koza_app.get_row()) is not None:
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
