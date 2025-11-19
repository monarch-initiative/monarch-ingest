import uuid
import koza
from biolink_model.datamodel.pydanticmodel_v2 import (
    GeneToPhenotypicFeatureAssociation,
    KnowledgeLevelEnum,
    AgentTypeEnum,
)


@koza.transform_record()
def transform_record(koza_transform, row):
    # Only process single gene entries
    gene_ids = row['DDB_G_ID'].split("|")
    if len(gene_ids) != 1 or not row.get("Phenotypes"):
        return []

    gene_id = f"dictyBase:{gene_ids[0]}"

    # Parse and lookup phenotypes
    phenotype_ids = [
        pid for name in (p.strip() for p in row["Phenotypes"].split('|') if p.strip())
        if (pid := koza_transform.lookup(name, 'id', 'dictybase_phenotype_names_to_ids'))
        and pid.startswith('DDPHENO:')
    ]

    if not phenotype_ids:
        return []

    # Create associations
    return [
        
        GeneToPhenotypicFeatureAssociation(
            id=f"uuid:{uuid.uuid1()}",
            subject=gene_id,
            predicate='biolink:has_phenotype',
            object=phenotype_id,
            aggregator_knowledge_source=["infores:monarchinitiative"],
            primary_knowledge_source="infores:dictybase",
            knowledge_level=KnowledgeLevelEnum.knowledge_assertion,
            agent_type=AgentTypeEnum.manual_agent,
        )
        for phenotype_id in phenotype_ids
    ]
