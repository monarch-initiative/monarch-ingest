import uuid
from koza.cli_runner import get_koza_app
from biolink.pydanticmodel import GeneToExpressionSiteAssociation

# The source name is used for reading and writing
source_name = "bgee_gene_to_expression"

koza_app = get_koza_app(source_name)

# create your entities
while (row := koza_app.get_row()) is not None:
    association = GeneToExpressionSiteAssociation(
        id="uuid:" + str(uuid.uuid1()),
        subject="ENSEMBL:" + row['Gene ID'],
        predicate='biolink:expressed_in',
        object=row['Anatomical entity ID'],
        aggregator_knowledge_source=["infores:monarchinitiative", "infores:bgee"])

    koza_app.write(association)
