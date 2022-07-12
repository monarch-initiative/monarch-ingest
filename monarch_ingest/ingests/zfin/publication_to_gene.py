import logging
import uuid

from koza.cli_runner import koza_app

from biolink.pydanticmodel import InformationContentEntityToNamedThingAssociation

LOG = logging.getLogger(__name__)

source_name = "zfin_publication_to_gene"

row = koza_app.get_row(source_name)

gene_id = "ZFIN:" + row["Gene ID"]

publication_id = "ZFIN:" + row["Publication ID"]

association = InformationContentEntityToNamedThingAssociation(
    id="uuid:" + str(uuid.uuid1()),
    subject=publication_id,
    predicate="biolink:mentions",
    object=gene_id,
    aggregator_knowledge_source=["infores:monarchinitiative"],
    primary_knowledge_source="infores:zfin"
)

koza_app.write(association)
