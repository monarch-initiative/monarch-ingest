import uuid

from koza.cli_utils import get_koza_app

from biolink_model.datamodel.pydanticmodel_v2 import (
    InformationContentEntityToNamedThingAssociation,
    AgentTypeEnum,
    KnowledgeLevelEnum,
)

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
        knowledge_level=KnowledgeLevelEnum.knowledge_assertion,
        agent_type=AgentTypeEnum.manual_agent,
    )

    koza_app.write(association)
