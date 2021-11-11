import logging

from koza.cli_runner import koza_app
from koza.converter.biolink_converter import gpi2gene

LOG = logging.getLogger(__name__)

source_name = "xenbase_gene_information"
row = koza_app.get_row(source_name)
row["DB_Object_ID"] = "Xenbase:" + row["DB_Object_ID"]

gene = gpi2gene(row)

gene.source = "Xenbase"

koza_app.write(gene)
