"""
Ingest of Reference Genome Orthologs from Panther
"""
import logging
import uuid

from biolink_model_pydantic.model import Gene, GeneToGeneHomologyAssociation, Predicate
from koza.cli_runner import koza_app

from monarch_ingest.panther.orthology_utils import parse_gene

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
    predicate = Predicate.orthologous_to
    relation = koza_app.translation_table.resolve_term("in orthology relationship with")

    # build the Gene and Orthologous Gene nodes
    gene = Gene(id=gene_id, in_taxon=gene_ncbitaxon, source="infores:panther")
    ortholog = Gene(id=ortholog_id, in_taxon=ortholog_ncbitaxon, source="infores:panther")

    # Instantiate the instance of Gene-to-Gene Homology Association
    panther_ortholog_id = row["Panther Ortholog ID"]
    association = GeneToGeneHomologyAssociation(
        id=f"uuid:{str(uuid.uuid1())}",
        subject=gene.id,
        object=ortholog.id,
        predicate=predicate,
        relation=relation,
        source="infores:panther",
        has_evidence=f"PANTHER.FAMILY:{panther_ortholog_id}",
    )

    # Write the captured Association out
    koza_app.write(gene, ortholog, association)

except RuntimeError as rte:
    logger.error(f"{str(rte)} in data row:\n\t'{str(row)}'")
