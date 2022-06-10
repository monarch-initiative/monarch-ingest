from monarch_ingest.model.biolink import Pathway
from koza.cli_runner import koza_app

source_name = "reactome_pathway"

row = koza_app.get_row(source_name)

species = row['species']
taxon_id = koza_app.translation_table.local_table[species]

# We only continue of the species is in our local reactome_id_mapping table
if taxon_id:
    pathway = Pathway(
        id="REACT:" + row["ID"],
        name=row["Name"],
        type=koza_app.translation_table.resolve_term("pathway"),
        source="infores:reactome",

        # TODO: https://github.com/biolink/biolink-model/pull/1033 rationalizes the scoping of the
        #       biolink:ThingWithTaxon mixin, such that Pathways will now have this (optional) slot
        in_taxon=[taxon_id]
    )

    koza_app.write(pathway)
