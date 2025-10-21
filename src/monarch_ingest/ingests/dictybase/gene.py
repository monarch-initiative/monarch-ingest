import koza
from biolink_model.datamodel.pydanticmodel_v2 import Gene


@koza.transform_record()
def transform_record(koza_transform, row):
    in_taxon = "NCBITaxon:44689"
    in_taxon_label = "Dictyostelium discoideum"

    synonyms = []
    if row.get('Synonyms') and row['Synonyms'].strip():
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

    return [gene]

