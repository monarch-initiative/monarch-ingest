from koza.cli_runner import get_koza_app

from biolink.pydanticmodel import Gene

koza_app = get_koza_app("dictybase_gene")
taxon_labels = koza_app.get_map("taxon-labels")

while (row := koza_app.get_row()) is not None:
    
    synonyms = []
    if row['Synonyms'] is not None:
        synonyms = row['Synonyms'].split(", ")

    in_taxon = "NCBITaxon:44689"

    gene = Gene(
        id='dictyBase:' + row['GENE ID'],
        symbol=row['Gene Name'],
        name=row['Gene Name'],
        # full name is not yet available in biolink
        # full_name=row['Gene Name'],
        synonym=synonyms,
        in_taxon=[in_taxon],
        in_taxon_label=taxon_labels[in_taxon]['label'],
        provided_by=["infores:dictybase"]
    )

    koza_app.write(gene)
