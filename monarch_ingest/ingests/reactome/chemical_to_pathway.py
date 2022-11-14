import uuid
from koza.cli_runner import get_koza_app
from biolink.pydanticmodel import ChemicalToPathwayAssociation

koza_app = get_koza_app("reactome_chemical_to_pathway")

while (row := koza_app.get_row()) is not None:

    species = row["species_nam"]
    try:
        taxon_id = koza_app.translation_table.local_table[species]
    except KeyError:
        # Move on if the taxon name isn't in the translation table
        koza_app.next_row()

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
            aggregator_knowledge_source=["infores:monarchinitiative"],
            primary_knowledge_source="infores:reactome"
        )

    koza_app.write(association)
