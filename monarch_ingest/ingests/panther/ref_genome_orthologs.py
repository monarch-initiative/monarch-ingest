"""
Ingest of Reference Genome Orthologs from Panther
"""
import logging
import uuid

from koza.cli_runner import get_koza_app

from biolink.pydanticmodel import GeneToGeneHomologyAssociation

from monarch_ingest.ingests.panther.orthology_utils import parse_gene

logger = logging.getLogger(__name__)

koza_app = get_koza_app("panther_ref_genome_orthologs")

row = koza_app.get_row()

try:
    # TODO: we don't current capture the taxon of the subject gene
    #       nor the object ortholog. Maybe as a qualifier in Biolink 3.0?

    species_and_gene_id = parse_gene(row['Gene'])

    # unpack the species and gene id
    gene_ncbitaxon, gene_id = species_and_gene_id

    species_and_ortholog_id = parse_gene(row['Ortholog'])

    # unpack the orthogous gene id and its species
    ortholog_ncbitaxon, ortholog_id = species_and_ortholog_id

    # TODO: how do I discriminate between LDO and O? I don't care for now??
    #       However, this may result in KGX record duplication?
    # ortholog_type = row["Type of ortholog"]
    predicate = "biolink:orthologous_to"

    # Instantiate the instance of Gene-to-Gene Homology Association
    panther_ortholog_id = row["Panther Ortholog ID"]
    association = GeneToGeneHomologyAssociation(
        id=f"uuid:{str(uuid.uuid1())}",
        subject=gene_id,
        object=ortholog_id,
        predicate=predicate,
        has_evidence=[f"PANTHER.FAMILY:{panther_ortholog_id}"],
        aggregator_knowledge_source=["infores:monarchinitiative"],
        primary_knowledge_source="infores:panther"
    )

    # Write the captured Association out
    koza_app.write(association)

except RuntimeError as rte:
    logger.debug(f"{str(rte)} in data row:\n\t'{str(row)}'")
