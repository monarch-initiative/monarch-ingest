import logging
import uuid

from biolink_model_pydantic.model import (
    Gene,
    NamedThingToInformationContentEntityAssociation,
    Predicate,
    Publication,
)
from koza.cli_runner import koza_app

LOG = logging.getLogger(__name__)

source_name = "zfin_gene_to_publication"

row = koza_app.get_row(source_name)


gene = Gene(id="ZFIN:" + row["Gene ID"], source="ZFIN")
publication = Publication(
    id="ZFIN:" + row["Publication ID"],
    type=koza_app.translation_table.resolve_term("publication"),
    source="ZFIN"
)
association = NamedThingToInformationContentEntityAssociation(
    id="uuid:" + str(uuid.uuid1()),
    subject=gene.id,
    predicate=Predicate.mentions,
    object=publication.id,
    relation=koza_app.translation_table.resolve_term("mentions"),
    source="infores:zfin"
)

koza_app.write(gene, publication, association)
