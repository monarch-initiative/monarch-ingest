import uuid

from biolink_model_pydantic.model import (
    Gene,
    NamedThingToInformationContentEntityAssociation,
    Predicate,
    Publication,
)
from koza.cli_runner import koza_app

source_name = "hgnc_gene_to_publication"

row = koza_app.get_row(source_name)

if not row["pubmed_id"]:
    koza_app.next_row()


gene = Gene(id=row["hgnc_id"])

id_list = row["pubmed_id"].split('|')
for each_id in id_list:
    publication_id = "PMID:"+each_id
    publication = Publication(
        id=publication_id,
        type=koza_app.translation_table.resolve_term("publication"),
    )
    association = NamedThingToInformationContentEntityAssociation(
        id="uuid:" + str(uuid.uuid1()),
        subject=gene.id,
        predicate=Predicate.mentions,
        object=publication.id,
        relation=koza_app.translation_table.resolve_term("mentions"),
    )

    koza_app.write(gene, publication, association)