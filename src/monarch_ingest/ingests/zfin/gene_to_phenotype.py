import uuid
import koza
from biolink_model.datamodel.pydanticmodel_v2 import (
    GeneToPhenotypicFeatureAssociation,
    KnowledgeLevelEnum,
    AgentTypeEnum,
)
from loguru import logger


@koza.transform_record()
def transform_record(koza_transform, row):
    if row["Phenotype Tag"] == "abnormal":
        zp_key_elements = [
            row["Affected Structure or Process 1 subterm ID"],
            row["Post-composed Relationship ID"],
            row["Affected Structure or Process 1 superterm ID"],
            row["Phenotype Keyword ID"],
            row["Affected Structure or Process 2 subterm ID"],
            row["Post-composed Relationship (rel) ID"],
            row["Affected Structure or Process 2 superterm ID"],
        ]

        zp_key = "-".join([element or "0" for element in zp_key_elements])

        try:
            zp_term = koza_transform.lookup(zp_key, 'iri', 'eqe2zp')

        except (KeyError, AttributeError) as e:

            logger.debug("ZP concatenation " + zp_key + " did not match a ZP term")
            return []

        if not zp_term:
            logger.debug("ZP concatenation " + zp_key + " did not match a ZP term")
            return []
        else:
            gene_id = "ZFIN:" + row["Gene ID"]

            association = GeneToPhenotypicFeatureAssociation(
                id="uuid:" + str(uuid.uuid1()),
                subject=gene_id,
                predicate="biolink:has_phenotype",
                object=zp_term,
                publications=["ZFIN:" + row["Publication ID"]],
                aggregator_knowledge_source=["infores:monarchinitiative"],
                primary_knowledge_source="infores:zfin",
                knowledge_level=KnowledgeLevelEnum.knowledge_assertion,
                agent_type=AgentTypeEnum.manual_agent,
            )

            return [association]

    return []  # Skip non-abnormal phenotype tags
