from koza.cli_utils import get_koza_app

from biolink_model.datamodel.pydanticmodel_v2 import Gene

koza_app = get_koza_app("dictybase_gene")
taxon_labels = koza_app.get_map("taxon-labels")

in_taxon = "NCBITaxon:44689"
in_taxon_label = taxon_labels[in_taxon]['label'] if in_taxon in taxon_labels else "Dictyostelium discoideum"

while (row := koza_app.get_row()) is not None:

    synonyms = []
    if row['Synonyms'] is not None:
        synonyms = row['Synonyms'].split(", ")

    gene = Gene(
        id='dictyBase:' + row['GENE ID'],
        symbol=row['Gene Name'],
        name=row['Gene Name'],
        full_name=row['Gene Name'],
        synonym=synonyms,
        in_taxon=[in_taxon],
        in_taxon_label=in_taxon_label,
        provided_by=["infores:dictybase"],
    )

    koza_app.write(gene)
