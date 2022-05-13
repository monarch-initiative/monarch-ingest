"""
Ingest of Reference Genome Orthologs from Panther
"""
import logging
import uuid

from koza.cli_runner import koza_app

from model.biolink import Gene, GeneToGeneHomologyAssociation
from monarch_ingest.ingests.panther.orthology_utils import parse_gene

logger = logging.getLogger(__name__)

row = koza_app.get_row()

try:
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
    #relation = koza_app.translation_table.resolve_term("in orthology relationship with")

    # Instantiate the instance of Gene-to-Gene Homology Association
    panther_ortholog_id = row["Panther Ortholog ID"]
    association = GeneToGeneHomologyAssociation(
        id=f"uuid:{str(uuid.uuid1())}",
        subject=gene_id,
        object=ortholog_id,
        predicate=predicate,
        source="infores:panther",
        has_evidence=f"PANTHER.FAMILY:{panther_ortholog_id}",
    )

    # Write the captured Association out
    koza_app.write(association)

except RuntimeError as rte:
    logger.error(f"{str(rte)} in data row:\n\t'{str(row)}'")
