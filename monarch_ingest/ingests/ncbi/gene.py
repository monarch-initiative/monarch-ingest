from monarch_ingest.model.biolink import Gene
from koza.cli_runner import koza_app

source_name = "ncbi_gene"

row = koza_app.get_row(source_name)

gene = Gene(
    id='NCBIGene:' + row["GeneID"],
    symbol=row["Symbol"],
    description=row["description"],
    in_taxon=['NCBITaxon:' + row["tax_id"]],
    source="infores:ncbi-gene"
)

koza_app.write(gene)
