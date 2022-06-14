import uuid

from koza.cli_runner import koza_app

from monarch_ingest.model.biolink import (
    Gene,
    InformationContentEntityToNamedThingAssociation,
    Publication,
)

source_name = "rgd_publication_to_gene"

row = koza_app.get_row(source_name)

if not row["CURATED_REF_PUBMED_ID"]:
    koza_app.next_row()

gene = Gene(id='RGD:' + row["GENE_RGD_ID"], source="infores:rgd")

id_list = row["CURATED_REF_PUBMED_ID"].split(';')
for each_id in id_list:
    publication_id = "PMID:" + each_id
    publication = Publication(
        id=publication_id,
        type=koza_app.translation_table.resolve_term("publication"),
        source="infores:rgd",
    )
    # relation = koza_app.translation_table.resolve_term("mentions")
    association = InformationContentEntityToNamedThingAssociation(
        id="uuid:" + str(uuid.uuid1()),
        subject=gene.id,
        predicate="biolink:mentions",
        object=publication.id,
        aggregating_knowledge_source=["infores:monarchinitiative"],
        primary_knowledge_source="infores:rgd"
    )

    koza_app.write(association)
