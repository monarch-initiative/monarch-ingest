import uuid
import koza
from biolink_model.datamodel.pydanticmodel_v2 import (
    GeneToPhenotypicFeatureAssociation,
    KnowledgeLevelEnum,
    AgentTypeEnum,
)


@koza.transform_record()
def transform_record(koza_transform, row):
    gene_id = "PomBase:" + row["Gene systematic ID"]

    phenotype_id = row["FYPO ID"]

    association = GeneToPhenotypicFeatureAssociation(
        id="uuid:" + str(uuid.uuid1()),
        subject=gene_id,
        predicate="biolink:has_phenotype",
        object=phenotype_id,
        publications=[row["Reference"]],
        aggregator_knowledge_source=["infores:monarchinitiative"],
        primary_knowledge_source="infores:pombase",
        knowledge_level=KnowledgeLevelEnum.knowledge_assertion,
        agent_type=AgentTypeEnum.manual_agent,
    )

    if row["Condition"]:
        association.qualifiers = row["Condition"].split(",")

    return [association]
