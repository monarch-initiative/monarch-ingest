import logging
import uuid

from biolink_model_pydantic.model import (
    Gene,
    InformationContentEntityToNamedThingAssociation,
    Predicate,
    Publication,
)
from koza.cli_runner import koza_app

LOG = logging.getLogger(__name__)

source_name = "zfin_publication_to_gene"

row = koza_app.get_row(source_name)

gene = Gene(id="ZFIN:" + row["Gene ID"], source="infores:zfin")
publication = Publication(
    id="ZFIN:" + row["Publication ID"],
    type=koza_app.translation_table.resolve_term("publication"),
    source="infores:zfin",
)
association = InformationContentEntityToNamedThingAssociation(
    id="uuid:" + str(uuid.uuid1()),
    subject=publication.id,
    predicate=Predicate.mentions,
    object=gene.id,
    relation=koza_app.translation_table.resolve_term("mentions"),
    source="infores:zfin",
)

koza_app.write(association)
