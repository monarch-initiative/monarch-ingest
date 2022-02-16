import uuid

from biolink_model_pydantic.model import (
    ChemicalEntity,
    MacromolecularMachineToBiologicalProcessAssociation,
    Pathway,
    Predicate,
)
from koza.cli_runner import koza_app

source_name = "reactome_chemical_to_pathway"

row = koza_app.get_row(source_name)


chemical = ChemicalEntity(id='CHEBI:' + row["component"], source="infores:reactome")

pathway = Pathway(
    id="REACT:" + row["pathway_id"],
    type=koza_app.translation_table.resolve_term("pathway"),
    source="infores:reactome",
)

association = MacromolecularMachineToBiologicalProcessAssociation(
    id="uuid:" + str(uuid.uuid1()),
    subject=chemical.id,
    predicate=Predicate.participates_in,
    object=pathway.id,
    relation=koza_app.translation_table.resolve_term("participates_in"),
    source="infores:reactome",
)

koza_app.write(chemical, pathway, association)
