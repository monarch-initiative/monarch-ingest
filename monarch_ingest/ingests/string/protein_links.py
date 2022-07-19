import uuid
import logging

from koza.cli_runner import get_koza_app

from biolink.pydanticmodel import PairwiseGeneToGeneInteraction

logger = logging.getLogger(__name__)
koza_app = get_koza_app("string_protein_links")

row = koza_app.get_row()
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

    for gid_a in gene_ids_a.split("|"):

        for gid_b in gene_ids_b.split("|"):

            gene_id_a = 'NCBIGene:' + gid_a

            gene_id_b = 'NCBIGene:' + gid_b

            association = PairwiseGeneToGeneInteraction(
                id="uuid:" + str(uuid.uuid1()),
                subject=gene_id_a,
                object=gene_id_b,
                predicate="biolink:interacts_with",
                aggregator_knowledge_source=["infores:monarchinitiative"],
                primary_knowledge_source="infores:string"
            )

            entities.append(association)

    koza_app.write(*entities)
