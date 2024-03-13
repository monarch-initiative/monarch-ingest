import uuid
from koza.cli_runner import get_koza_app

from biolink_model.datamodel.pydanticmodel_v2 import GeneToPathwayAssociation

koza_app = get_koza_app("reactome_gene_to_pathway")

while (row := koza_app.get_row()) is not None:

    species = row["species_nam"]
    try:
        taxon_id = koza_app.translation_table.local_table[species]
    except KeyError:
        # Move on if the taxon name isn't in the translation table
        koza_app.next_row()

    # We only continue of the species is in our local taxon_name_to_id_mapping table
    if taxon_id:

        gene_id = 'NCBIGene:' + row["component"]
        pathway_id = "Reactome:" + row["pathway_id"]  # pathways themselves are an independent ingest now...

        go_evidence_code = row["go_ecode"]
        evidence_code_term = koza_app.translation_table.resolve_term(go_evidence_code)

        association = GeneToPathwayAssociation(
            id="uuid:" + str(uuid.uuid1()),
            subject=gene_id,
            predicate="biolink:participates_in",
            object=pathway_id,
            has_evidence=[evidence_code_term],
            aggregator_knowledge_source=["infores:monarchinitiative"],
            primary_knowledge_source="infores:reactome",
        )

    koza_app.write(association)
