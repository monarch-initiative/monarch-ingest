"""
Ingest of Reference Genome Orthologs from Xenbase
"""

import uuid

from koza.cli_utils import get_koza_app

from biolink_model.datamodel.pydanticmodel_v2 import GeneToGeneHomologyAssociation, AgentTypeEnum, KnowledgeLevelEnum

from loguru import logger

koza_app = get_koza_app("xenbase_orthologs")

while (row := koza_app.get_row()) is not None:

    try:
        gene_id = row['xb_genepage_id']
        assert gene_id

        predicate = "biolink:orthologous_to"

        ortholog_id = row['entrez_id']
        assert ortholog_id

        # Instantiate the instance of Gene-to-Gene Homology Association
        association = GeneToGeneHomologyAssociation(
            id=f"uuid:{str(uuid.uuid1())}",
            subject=f"Xenbase:{gene_id}",
            predicate=predicate,
            object=f"NCBIGene:{ortholog_id}",
            aggregator_knowledge_source=["infores:monarchinitiative"],
            primary_knowledge_source="infores:xenbase",
            knowledge_level=KnowledgeLevelEnum.knowledge_assertion,
            agent_type=AgentTypeEnum.manual_agent
        )

        # Write the captured Association out
        koza_app.write(association)

    except (RuntimeError, AssertionError) as rte:
        logger.debug(f"{str(rte)} in data row:\n\t'{str(row)}'")
