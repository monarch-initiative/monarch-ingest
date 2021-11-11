import uuid

from biolink_model_pydantic.model import (
    Gene,
    NamedThingToInformationContentEntityAssociation,
    Predicate,
    Publication,
)
from koza.cli_runner import koza_app

source_name = "rgd_gene_to_publication"

row = koza_app.get_row(source_name)

if not row["CURATED_REF_PUBMED_ID"]:
    koza_app.next_row()

gene = Gene(id='RGD:' + row["GENE_RGD_ID"])

id_list = row["CURATED_REF_PUBMED_ID"].split(';')
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