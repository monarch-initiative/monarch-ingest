import logging
import uuid

from koza.cli_runner import koza_app

from model.biolink import (
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
association = InformationContentEntityToNamedThingAssociation(
    id="uuid:" + str(uuid.uuid1()),
    subject=publication.id,
    predicate="biolink:mentions",
    object=gene.id,
    relation=koza_app.translation_table.resolve_term("mentions"),
    source="infores:zfin",
)

koza_app.write(association)
