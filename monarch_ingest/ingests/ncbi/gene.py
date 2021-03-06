from koza.cli_runner import get_koza_app

from biolink.pydanticmodel import Gene

koza_app = get_koza_app("ncbi_gene")

row = koza_app.get_row()

gene = Gene(
    id='NCBIGene:' + row["GeneID"],
    symbol=row["Symbol"],
    description=row["description"],
    in_taxon=['NCBITaxon:' + row["tax_id"]],
    provided_by=["infores:ncbi-gene"]
)

koza_app.write(gene)
