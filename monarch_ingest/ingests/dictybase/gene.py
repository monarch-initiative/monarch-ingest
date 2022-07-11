from typing import Optional, Tuple

from koza.cli_runner import koza_app
from monarch_ingest.ingests.dictybase.utils import parse_gene_id

from biolink.pydanticmodel import Gene

source_name = "dictybase_gene"

row = koza_app.get_row(source_name)

gene_names_to_ids = koza_app.get_map("dictybase_gene_names_to_ids")

gene_identifier: Optional[Tuple[str, str]] = parse_gene_id(row, gene_names_to_ids)
if gene_identifier:

    gene = Gene(
        id=gene_identifier[0],
        symbol=gene_identifier[1],
        name=gene_identifier[1],
        in_taxon=["NCBITaxon:44689"],
        source="infores:dictybase"
    )

    koza_app.write(gene)
