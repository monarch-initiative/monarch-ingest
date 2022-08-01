"""
Ingest of Reference Genome Orthologs from Xenbase
"""
import logging
import uuid

from koza.cli_runner import get_koza_app

from biolink.pydanticmodel import GeneToGeneHomologyAssociation

logger = logging.getLogger(__name__)

koza_app = get_koza_app("xenbase_orthologs")

row = koza_app.get_row()

try:
    # TODO: we don't current capture the taxon of the subject gene
    #       nor the object ortholog. Maybe as a qualifier in Biolink 3.0?

    gene_id = row['SUBJECT']
    predicate = "biolink:orthologous_to"
    ortholog_id = row['OBJECT']
    evidence = row['EVIDENCE']

    # Instantiate the instance of Gene-to-Gene Homology Association
    association = GeneToGeneHomologyAssociation(
        id=f"uuid:{str(uuid.uuid1())}",
        subject=gene_id,
        predicate=predicate,
        object=ortholog_id,
        has_evidence=[evidence],
        aggregator_knowledge_source=["infores:monarchinitiative"],
        primary_knowledge_source="infores:xenbase"
    )

    # Write the captured Association out
    koza_app.write(association)

except RuntimeError as rte:
    logger.debug(f"{str(rte)} in data row:\n\t'{str(row)}'")
