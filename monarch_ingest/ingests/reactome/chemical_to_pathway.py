import uuid
from koza.cli_runner import koza_app
from monarch_ingest.model.biolink import ChemicalToPathwayAssociation

source_name = "reactome_chemical_to_pathway"

row = koza_app.get_row(source_name)

species = row["species_nam"]
taxon_id = koza_app.translation_table.local_table[species]

# We only continue of the species is in our local reactome_id_mapping table
if taxon_id:

    chemical_id = "CHEBI:" + row["component"]
    pathway_id = "REACT:" + row["pathway_id"]  # pathways themselves are an independent ingest now...

    go_evidence_code = row["go_ecode"]
    evidence_code_term = koza_app.translation_table.resolve_term(go_evidence_code)

    association = ChemicalToPathwayAssociation(
        id="uuid:" + str(uuid.uuid1()),
        subject=chemical_id,
        predicate="biolink:participates_in",
        object=pathway_id,
        has_evidence=[evidence_code_term],
        source="infores:reactome"
    )

    koza_app.write(association)
