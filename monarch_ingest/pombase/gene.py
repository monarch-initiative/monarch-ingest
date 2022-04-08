import logging

from koza.cli_runner import koza_app

from model.biolink import Gene

LOG = logging.getLogger(__name__)

source_name = "pombase_gene"
row = koza_app.get_row(source_name)

# Given that this file is coming from PomBase, I think the biolink model is wrong about all caps
row["curie"] = row["curie"].replace("PomBase", "POMBASE")

gene = Gene(
    id=row["curie"],
    symbol=row["primary gene name"],
    type=koza_app.translation_table.resolve_term(row["product type"].replace(' ', '_')),
    source="infores:PomBase",
)

if row["UniProtKB accession"]:
    gene.xref = ["UniProtKB:" + row["UniProtKB accession"]]

if row["synonyms"]:
    gene.synonym = row["synonyms"].split(",")

koza_app.write(gene)
