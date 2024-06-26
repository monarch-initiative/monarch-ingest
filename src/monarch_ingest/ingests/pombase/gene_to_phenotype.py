import uuid

from koza.cli_utils import get_koza_app

from biolink_model.datamodel.pydanticmodel_v2 import (
    GeneToPhenotypicFeatureAssociation,
    KnowledgeLevelEnum,
    AgentTypeEnum,
)

koza_app = get_koza_app("pombase_gene_to_phenotype")

while (row := koza_app.get_row()) is not None:

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

    koza_app.write(association)
