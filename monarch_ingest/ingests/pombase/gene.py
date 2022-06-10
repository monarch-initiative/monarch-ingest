import logging

from koza.cli_runner import koza_app

from monarch_ingest.model.biolink import Gene

LOG = logging.getLogger(__name__)

source_name = "pombase_gene"
row = koza_app.get_row(source_name)

gene = Gene(
    id=row["curie"],
    symbol=row["primary gene name"],
    type=koza_app.translation_table.resolve_term(row["product type"].replace(' ', '_')),
    source="infores:PomBase",
    in_taxon=["NCBITaxon:4896"]
)

if row["UniProtKB accession"]:
    gene.xref = ["UniProtKB:" + row["UniProtKB accession"]]

if row["synonyms"]:
    gene.synonym = row["synonyms"].split(",")

koza_app.write(gene)
