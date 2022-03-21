import uuid

from biolink_model_pydantic.model import (
    ChemicalToPathwayAssociation,
    Gene,
    Pathway,
    Predicate,
)
from koza.cli_runner import koza_app

source_name = "reactome_gene_to_pathway"

row = koza_app.get_row(source_name)


gene = Gene(id='ENSEMBL:' + row["component"], source="infores:reactome")

pathway = Pathway(
    id="REACT:" + row["pathway_id"],
    type=koza_app.translation_table.resolve_term("pathway"),
    source="infores:reactome",
)

association = ChemicalToPathwayAssociation(
    id="uuid:" + str(uuid.uuid1()),
    subject=gene.id,
    predicate=Predicate.participates_in,
    object=pathway.id,
    relation=koza_app.translation_table.resolve_term("participates_in"),
    source="infores:reactome",
)

koza_app.write(gene, pathway, association)
