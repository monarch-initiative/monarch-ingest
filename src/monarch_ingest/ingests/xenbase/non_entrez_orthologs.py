"""
Ingest of Reference Genome Orthologs from Xenbase
"""

import uuid

from koza.cli_utils import get_koza_app

from biolink_model.datamodel.pydanticmodel_v2 import GeneToGeneHomologyAssociation, AgentTypeEnum, KnowledgeLevelEnum

from loguru import logger

koza_app = get_koza_app("xenbase_non_entrez_orthologs")

while (row := koza_app.get_row()) is not None:

    try:
        gene_id = row['Xenbase']

        predicate = "biolink:orthologous_to"

        omim_id = row['OMIM']
        mgi_id = row['MGI']
        zfin_id = row['ZFIN']

        # Instantiate the instance of Gene-to-Gene Homology Associations for each ortholog
        if omim_id:
            association = GeneToGeneHomologyAssociation(
                id=f"uuid:{str(uuid.uuid1())}",
                subject=f"Xenbase:{gene_id}",
                predicate=predicate,
                object=f"OMIM:{omim_id}",
                aggregator_knowledge_source=["infores:monarchinitiative"],
                primary_knowledge_source="infores:xenbase",
                knowledge_level=KnowledgeLevelEnum.knowledge_assertion,
                agent_type=AgentTypeEnum.manual_agent
            )

            # Write the captured Association out
            koza_app.write(association)

        if mgi_id:
            association = GeneToGeneHomologyAssociation(
                id=f"uuid:{str(uuid.uuid1())}",
                subject=f"Xenbase:{gene_id}",
                predicate=predicate,
                object=f"MGI:{mgi_id}",
                aggregator_knowledge_source=["infores:monarchinitiative"],
                primary_knowledge_source="infores:xenbase",
                knowledge_level=KnowledgeLevelEnum.knowledge_assertion,
                agent_type=AgentTypeEnum.manual_agent
            )

            # Write the captured Association out
            koza_app.write(association)

        if zfin_id:
            association = GeneToGeneHomologyAssociation(
                id=f"uuid:{str(uuid.uuid1())}",
                subject=f"Xenbase:{gene_id}",
                predicate=predicate,
                object=f"ZFIN:{zfin_id}",
                aggregator_knowledge_source=["infores:monarchinitiative"],
                primary_knowledge_source="infores:xenbase",
                knowledge_level=KnowledgeLevelEnum.knowledge_assertion,
                agent_type=AgentTypeEnum.manual_agent
            )

            # Write the captured Association out
            koza_app.write(association)

    except (RuntimeError, AssertionError) as rte:
        logger.debug(f"{str(rte)} in data row:\n\t'{str(row)}'")
