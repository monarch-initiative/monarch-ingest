from biolink_model_pydantic.model import Pathway

from koza.cli_runner import koza_app

source_name = "reactome_pathway"

row = koza_app.get_row(source_name)

pathway = Pathway(
    id="REACT:" + row["ID"],
    name=row["Name"],
    type=koza_app.translation_table.resolve_term("pathway"),
    source="infores:reactome",
)

koza_app.write(pathway)
