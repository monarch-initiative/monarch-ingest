import koza
from biolink_model.datamodel.pydanticmodel_v2 import Gene


@koza.transform_record()
def transform_record(koza_transform, row):
    xref_list = []
    if row['ensembl_gene_id']:
        xref_list.append('ENSEMBL:' + row['ensembl_gene_id'])
    if row['omim_id']:
        if '|' in row['omim_id']:
            for each in row['omim_id'].split('|'):
                xref_list.append('OMIM:' + each)
        else:
            xref_list.append('OMIM:' + row['omim_id'])

    synonyms_list = (
        row["alias_symbol"].split("|")
        + row["alias_name"].split("|")
        + row["prev_symbol"].split("|")
        + row["prev_name"].split("|")
    )

    # Filter out empty strings from synonyms
    synonyms_list = [s for s in synonyms_list if s and s.strip()]

    in_taxon = "NCBITaxon:9606"
    in_taxon_label = "Homo sapiens"

    # Lookup SO term from mapping, handle case where gene is not in mapping
    so_term = None
    try:
        so_term_id = koza_transform.lookup(row["hgnc_id"], 'so_term_id', 'hgnc-so-terms')
        # Koza's lookup may return the key itself if not found, check if it looks like a valid SO term
        if so_term_id and so_term_id.startswith('SO:'):
            so_term = [so_term_id]
    except (KeyError, AttributeError):
        # Gene not in mapping, so_term remains None
        pass

    gene = Gene(
        id=row["hgnc_id"],
        symbol=row["symbol"],
        name=row["symbol"],
        full_name=row["name"],
        type=so_term,
        xref=xref_list if xref_list else None,
        synonym=synonyms_list if synonyms_list else None,
        in_taxon=[in_taxon],
        in_taxon_label=in_taxon_label,
        provided_by=["infores:hgnc"],
    )
    return [gene]
