"""
Ingest of Reference Genome Orthologs from Xenbase
"""

import uuid
import koza
from biolink_model.datamodel.pydanticmodel_v2 import GeneToGeneHomologyAssociation, AgentTypeEnum, KnowledgeLevelEnum
from loguru import logger


@koza.transform_record()
def transform_record(koza_transform, row):
    genepage_id = row['xb_genepage_id']
    assert genepage_id

    predicate = "biolink:orthologous_to"

    ortholog_id = row['entrez_id']
    assert ortholog_id

    # TODO: Re-implement genepage_to_gene_map lookup when mapping file structure is clarified
    # For now, use the genepage_id directly as gene_id
    # genepage_to_gene_map = koza_transform.get_map("genepage-2-gene")
    # gene_ids = genepage_to_gene_map.get(genepage_id).values()
    gene_ids = [genepage_id]  # Simplified for now

    associations = []
    for gene_id in gene_ids:
        # Instantiate the instance of Gene-to-Gene Homology Association
        association = GeneToGeneHomologyAssociation(
            id=f"uuid:{str(uuid.uuid1())}",
            subject=f"Xenbase:{gene_id}",
            predicate=predicate,
            object=f"NCBIGene:{ortholog_id}",
            aggregator_knowledge_source=["infores:monarchinitiative"],
            primary_knowledge_source="infores:xenbase",
            knowledge_level=KnowledgeLevelEnum.knowledge_assertion,
            agent_type=AgentTypeEnum.manual_agent,
        )
        associations.append(association)

    return associations
