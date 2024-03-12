from koza.cli_runner import get_koza_app

from biolink_model.datamodel.pydanticmodel_v2 import Gene

koza_app = get_koza_app("ncbi_gene")
taxon_labels = koza_app.get_map("taxon-labels")

# If a taxon label we need isn't in phenio's NCBITaxon subset, we can add it here
extra_taxon_labels = {
    'NCBITaxon:227321': 'Dictyostelium discoideum'
}

while (row := koza_app.get_row()) is not None:

    in_taxon = 'NCBITaxon:' + row["tax_id"]


    if in_taxon in taxon_labels:
        in_taxon_label = taxon_labels[in_taxon]['label']
    elif in_taxon in extra_taxon_labels:
        in_taxon_label = extra_taxon_labels[in_taxon]
    else:
        raise ValueError(f"Taxon {in_taxon} not found in taxon-labels")

    gene = Gene(
        id='NCBIGene:' + row["GeneID"],
        symbol=row["Symbol"],
        name=row["Symbol"],
        full_name=row["Full_name_from_nomenclature_authority"],
        description=row["description"],
        in_taxon=[in_taxon],
        in_taxon_label=in_taxon_label,
        provided_by=["infores:ncbi-gene"]
    )

    koza_app.write(gene)
