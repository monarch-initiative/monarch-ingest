import koza
from biolink_model.datamodel.pydanticmodel_v2 import Gene


@koza.transform_record()
def transform_record(koza_transform, row):
    in_taxon = "NCBITaxon:4896"
    # For now, hardcode the label since mapping files need more research
    # TODO: Re-implement taxon_labels lookup when mapping file structure is clarified
    # taxon_labels = koza_transform.get_map("taxon-labels")
    # in_taxon_label = taxon_labels[in_taxon]["label"] if in_taxon in taxon_labels else "Schizosaccharomyces pombe"
    in_taxon_label = "Schizosaccharomyces pombe"

    gene = Gene(
        id=row["gene_systematic_id_with_prefix"],
        symbol=row["gene_name"] or row["gene_systematic_id"],
        name=row["gene_name"] or row["gene_systematic_id"],
        full_name=row["gene_name"] or row["gene_systematic_id"],
        # No place in the schema for gene type (SO term) right now
        # type=koza_transform.translation_table.resolve_term(row["product type"].replace(' ', '_')),
        in_taxon=[in_taxon],
        in_taxon_label=in_taxon_label,
        provided_by=["infores:pombase"],
    )

    if row["external_id"]:
        gene.xref = ["UniProtKB:" + row["external_id"]]

    if row["synonyms"]:
        gene.synonym = row["synonyms"].split(",")

    return [gene]
