import uuid
from typing import List

from koza.cli_utils import get_koza_app

from biolink_model.datamodel.pydanticmodel_v2 import PairwiseGeneToGeneInteraction, KnowledgeLevelEnum, AgentTypeEnum

from loguru import logger

from string_utils import map_evidence_codes

koza_app = get_koza_app("string_protein_links")

seen_rows = set([])


def sorted_id_pair(row) -> str:
    sorted([row['protein1'], row['protein2']])


while (row := koza_app.get_row()) is not None and sorted_id_pair(row) not in seen_rows:

    entrez_2_string = koza_app.get_map('entrez_2_string')

    pid_a = row['protein1']
    gene_ids_a = entrez_2_string[pid_a]['entrez']
    if not gene_ids_a:
        logger.debug(f"protein1 PID '{str(pid_a)}' has no Entrez mappings?")

    pid_b = row['protein2']
    gene_ids_b = entrez_2_string[pid_b]['entrez']
    if not gene_ids_b:
        logger.debug(f"protein2 PID '{str(pid_b)}' has no Entrez mappings?")

    # Some proteins may not have gene Entrez ID mappings.
    # Only process the record if both gene id's are found
    if gene_ids_a and gene_ids_b:

        entities = []

        has_evidence: List[str] = map_evidence_codes(row)

        for gid_a in gene_ids_a.split("|"):

            for gid_b in gene_ids_b.split("|"):

                gene_id_a = 'NCBIGene:' + gid_a

                gene_id_b = 'NCBIGene:' + gid_b

                association = PairwiseGeneToGeneInteraction(
                    id="uuid:" + str(uuid.uuid1()),
                    subject=gene_id_a,
                    object=gene_id_b,
                    predicate="biolink:interacts_with",
                    # sanity check: set to 'None' if empty list
                    has_evidence=has_evidence if has_evidence else None,
                    aggregator_knowledge_source=["infores:monarchinitiative"],
                    primary_knowledge_source="infores:string",
                    knowledge_level=KnowledgeLevelEnum.knowledge_assertion,
                    agent_type=AgentTypeEnum.not_provided,
                )
                seen_rows.add(sorted_id_pair(row))
                entities.append(association)

        koza_app.write(*entities)
