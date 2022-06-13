import uuid

from koza.cli_runner import koza_app

from monarch_ingest.model.biolink import ChemicalEntity, ChemicalToPathwayAssociation, Pathway

source_name = "reactome_chemical_to_pathway"

row = koza_app.get_row(source_name)


chemical = ChemicalEntity(id='CHEBI:' + row["component"], source="infores:reactome")

pathway = Pathway(
    id="REACT:" + row["pathway_id"],
    type=koza_app.translation_table.resolve_term("pathway"),
    source="infores:reactome",
)


#relation = koza_app.translation_table.resolve_term("participates_in")
association = ChemicalToPathwayAssociation(
    id="uuid:" + str(uuid.uuid1()),
    subject=chemical.id,
    predicate="biolink:participates_in",
    object=pathway.id,
    aggregating_knowledge_source="infores:monarchinitiative",
    primary_knowledge_source="infores:reactome"
)

koza_app.write(association)
