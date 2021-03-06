from biolink.pydanticmodel import Pathway
from koza.cli_runner import get_koza_app

koza_app = get_koza_app('reactome_pathway')

row = koza_app.get_row()

species = row['species']

try:
    taxon_id = koza_app.translation_table.local_table[species]
except KeyError:
    # Move on if the taxon name isn't in the translation table
    koza_app.next_row()

# We only continue of the species is in our local reactome_id_mapping table
if taxon_id:
    pathway = Pathway(
        id="REACT:" + row["ID"],
        name=row["Name"],
        type=koza_app.translation_table.resolve_term("pathway"),
        source="infores:reactome",
        in_taxon=[taxon_id],
        provided_by=["infores:reactome"]
    )

    koza_app.write(pathway)
