import logging

from koza.converter.biolink_converter import gpi2gene
from koza.cli_runner import koza_app

LOG = logging.getLogger(__name__)

source_name = "gene-information"
row = koza_app.get_row(source_name)
row["DB_Object_ID"] = "Xenbase:" + row["DB_Object_ID"]

gene = gpi2gene(row)

koza_app.write(gene)
