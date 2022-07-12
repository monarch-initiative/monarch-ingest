from koza.cli_runner import koza_app

from biolink.pydanticmodel import Pathway

source_name = "reactome_pathway"

row = koza_app.get_row(source_name)

species = row['species']

taxon_id = koza_app.translation_table.local_table[species]

pathway = Pathway(
    id="REACT:" + row["ID"],
    name=row["Name"],
    in_taxon=[taxon_id],
    provided_by=["infores:reactome"]
)

koza_app.write(pathway)
