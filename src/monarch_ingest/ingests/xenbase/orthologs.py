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

    # Look up each gene ID from the mapping (tropicalis, laevis_l, laevis_s)
    gene_ids = []
    for field in ['tropicalis_id', 'laevis_l_id', 'laevis_s_id']:
        gene_id = koza_transform.lookup(genepage_id, field, 'genepage-2-gene')
        if gene_id:  # Filter out None/empty values
            gene_ids.append(gene_id)

    # Fallback to genepage_id if no mappings found
    if not gene_ids:
        gene_ids = [genepage_id]

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
