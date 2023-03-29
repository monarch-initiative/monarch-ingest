from koza.cli_runner import get_koza_app
from monarch_ingest.ingests.bgee.gene_to_expression_utils import process_koza_source


# The source name is used for reading and writing
source_name = "bgee_gene_to_expression"
koza_app = get_koza_app(source_name)
process_koza_source(koza_app)
