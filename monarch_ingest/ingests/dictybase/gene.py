from typing import Optional, Tuple

from koza.cli_runner import get_koza_app
from monarch_ingest.ingests.dictybase.utils import parse_gene_id

from biolink.pydanticmodel import Gene

koza_app = get_koza_app("dictybase_gene")

row = koza_app.get_row()

gene_names_to_ids = koza_app.get_map("dictybase_gene_names_to_ids")
dicty_symbols_to_ncbi_genes = koza_app.get_map("dicty_symbols_to_ncbi_genes")

gene_identifier: Optional[Tuple[str, str]] = parse_gene_id(row, gene_names_to_ids, dicty_symbols_to_ncbi_genes)
if gene_identifier:

    gene = Gene(
        id=gene_identifier[0],
        symbol=gene_identifier[1],
        name=gene_identifier[1],
        in_taxon=["NCBITaxon:44689"],
        provided_by=["infores:dictybase"]
    )

    koza_app.write(gene)
