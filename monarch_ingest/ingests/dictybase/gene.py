from koza.cli_runner import get_koza_app

from biolink.pydanticmodel import Gene

koza_app = get_koza_app("dictybase_gene")

while (row := koza_app.get_row()) is not None:
    
    synonyms = []
    if row['Synonyms'] is not None:
        synonyms = row['Synonyms'].split(", ")

    gene = Gene(
        id='dictyBase:' + row['GENE ID'],
        symbol=row['Gene Name'],
        name=row['Gene Name'],
        synonym=synonyms,
        in_taxon=["NCBITaxon:44689"],
        provided_by=["infores:dictybase"]
    )

    koza_app.write(gene)
