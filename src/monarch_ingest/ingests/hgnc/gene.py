from koza.cli_utils import get_koza_app

from biolink_model.datamodel.pydanticmodel_v2 import Gene

koza_app = get_koza_app("hgnc_gene")

so_term_map = koza_app.get_map("hgnc-so-terms")

while (row := koza_app.get_row()) is not None:

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

    in_taxon = "NCBITaxon:9606"
    in_taxon_label = "Homo sapiens"

    gene = Gene(
        id=row["hgnc_id"],
        symbol=row["symbol"],
        name=row["symbol"],
        full_name=row["name"],
        type=[so_term_map[row['hgnc_id']]['so_term_id']] if row['hgnc_id'] in so_term_map else None,
        xref=xref_list,
        synonym=synonyms_list,
        in_taxon=[in_taxon],
        in_taxon_label=in_taxon_label,
        provided_by=["infores:hgnc"],
    )
    koza_app.write(gene)
