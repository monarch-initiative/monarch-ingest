import uuid

from koza.cli_runner import koza_app

from model.biolink import GeneToPathwayAssociation

source_name = "reactome_gene_to_pathway"

row = koza_app.get_row(source_name)

species = row["species_nam"]
taxon_id = koza_app.translation_table.local_table[species]

# We only continue of the species is in our local taxon_name_to_id_mapping table
if taxon_id:

    gene_id = 'NCBIGene:' + row["component"]
    pathway_id = "REACT:" + row["pathway_id"]  # pathways themselves are an independent ingest now...

    go_evidence_code = row["go_ecode"]
    evidence_code_term = koza_app.translation_table.resolve_term(go_evidence_code)

    # TODO: https://github.com/biolink/biolink-model/pull/1031 introduces a
    #       GeneToPathwayAssociation class which should be in the next Biolink Model release
    association = GeneToPathwayAssociation(
        id="uuid:" + str(uuid.uuid1()),
        subject=gene_id,
        predicate="biolink:participates_in",
        object=pathway_id,
        has_evidence=[evidence_code_term],
        source="infores:reactome"
    )

    koza_app.write(association)
