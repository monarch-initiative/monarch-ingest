from koza.cli_runner import get_koza_app

from biolink.pydanticmodel import Gene

koza_app = get_koza_app("ncbi_gene")
taxon_labels = koza_app.get_map("taxon-labels")

while (row := koza_app.get_row()) is not None:

    in_taxon = 'NCBITaxon:' + row["tax_id"]
    in_taxon_label = taxon_labels[in_taxon]["label"]
    gene = Gene(
        id='NCBIGene:' + row["GeneID"],
        symbol=row["Symbol"],
        description=row["description"],
        in_taxon=[in_taxon],
        in_taxon_label=in_taxon_label,
        provided_by=["infores:ncbi-gene"]
    )

    koza_app.write(gene)
