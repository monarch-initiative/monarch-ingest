from koza.cli_runner import koza_app

from biolink_model.pydantic.model import Pathway

source_name = "reactome_pathway"

row = koza_app.get_row(source_name)

species = row['species']
taxon_id = koza_app.translation_table.local_table[species]
pathway = Pathway(
    id="REACT:" + row["ID"],
    name=row["Name"],
    type=koza_app.translation_table.resolve_term("pathway"),
    source="infores:reactome",
    # in_taxon=[taxon_id] TODO: this isn't an allowed attribute on pathway.  We need to request adding in biolink if we do need this
)

koza_app.write(pathway)
