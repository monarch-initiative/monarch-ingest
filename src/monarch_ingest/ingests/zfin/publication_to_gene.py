
import uuid

from koza.cli_runner import get_koza_app

from biolink_model.datamodel.pydanticmodel_v2 import InformationContentEntityToNamedThingAssociation, AgentTypeEnum, \
    KnowledgeLevelEnum

from loguru import logger

koza_app = get_koza_app("zfin_publication_to_gene")

while (row := koza_app.get_row()) is not None:

    gene_id = "ZFIN:" + row["Gene ID"]

    publication_id = "ZFIN:" + row["Publication ID"]

    association = InformationContentEntityToNamedThingAssociation(
        id="uuid:" + str(uuid.uuid1()),
        subject=publication_id,
        predicate="biolink:mentions",
        object=gene_id,
        aggregator_knowledge_source=["infores:monarchinitiative"],
        primary_knowledge_source="infores:zfin",
        knowledge_level=KnowledgeLevelEnum.knowledge_assertion,
        agent_type=AgentTypeEnum.manual_agent
    )

    koza_app.write(association)
