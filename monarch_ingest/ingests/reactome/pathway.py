from model.biolink import Pathway
from koza.cli_runner import koza_app

source_name = "reactome_pathway"

row = koza_app.get_row(source_name)

species = row['species']
taxon_id = koza_app.translation_table.local_table[species]
pathway = Pathway(
    id="REACT:" + row["ID"],
    name=row["Name"],
    type=koza_app.translation_table.resolve_term("pathway"),
    source="infores:reactome",

    # TODO: this isn't an allowed attribute on pathway. Biolink Model may soon add.
    #       See Issue https://github.com/biolink/biolink-model/issues/1032
    # in_taxon=[taxon_id]
)

koza_app.write(pathway)
