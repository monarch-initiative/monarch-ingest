from koza.cli_runner import get_koza_app

from biolink.pydanticmodel import Gene

koza_app = get_koza_app("ncbi_gene")

while (row := koza_app.get_row()) is not None:
    
    gene = Gene(
        id='NCBIGene:' + row["GeneID"],
        symbol=row["Symbol"],
        name=row["Symbol"],
        # full name is not yet available in biolink
        # full_name=row["Full_name_from_nomenclature_authority"],
        description=row["description"],
        in_taxon=['NCBITaxon:' + row["tax_id"]],
        provided_by=["infores:ncbi-gene"]
    )

    koza_app.write(gene)
