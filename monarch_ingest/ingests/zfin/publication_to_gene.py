import logging
import uuid

from koza.cli_runner import koza_app

from biolink.pydantic.model import (
    Gene,
    InformationContentEntityToNamedThingAssociation,
    Publication,
)

LOG = logging.getLogger(__name__)

source_name = "zfin_publication_to_gene"

row = koza_app.get_row(source_name)

gene = Gene(id="ZFIN:" + row["Gene ID"], source="infores:zfin")
publication = Publication(
    id="ZFIN:" + row["Publication ID"],
    type=koza_app.translation_table.resolve_term("publication"),
    source="infores:zfin",
)
# relation = koza_app.translation_table.resolve_term("mentions")
association = InformationContentEntityToNamedThingAssociation(
    id="uuid:" + str(uuid.uuid1()),
    subject=publication.id,
    predicate="biolink:mentions",
    object=gene.id,
    aggregating_knowledge_source=["infores:monarchinitiative"],
    primary_knowledge_source="infores:zfin"
)

koza_app.write(association)
