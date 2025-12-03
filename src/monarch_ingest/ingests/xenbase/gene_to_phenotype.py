import uuid
import koza
from biolink_model.datamodel.pydanticmodel_v2 import (
    Gene,
    GeneToPhenotypicFeatureAssociation,
    PhenotypicFeature,
    KnowledgeLevelEnum,
    AgentTypeEnum,
)


@koza.transform_record()
def transform_record(koza_transform, row):
    # Not including qualifiers, as none are present in the input file. If they show up,
    # we'll want to examine the values before including them in the output of this transform
    if row["QUALIFIER"]:
        raise ValueError("Didn't expect a qualifier value, found: " + row["QUALIFIER"])

    gene = Gene(id=row["SUBJECT"], provided_by=["infores:xenbase"])

    phenotype = PhenotypicFeature(id=row["OBJECT"], provided_by=["infores:xenbase"])

    # relation = row["RELATION"].replace("_", ":"),
    association = GeneToPhenotypicFeatureAssociation(
        id="uuid:" + str(uuid.uuid1()),
        subject=gene.id,
        predicate="biolink:has_phenotype",
        object=phenotype.id,
        publications=[row["SOURCE"]] if row["SOURCE"] else None,
        aggregator_knowledge_source=["infores:monarchinitiative"],
        primary_knowledge_source="infores:xenbase",
        knowledge_level=KnowledgeLevelEnum.knowledge_assertion,
        agent_type=AgentTypeEnum.manual_agent,
    )

    return [gene, phenotype, association]
