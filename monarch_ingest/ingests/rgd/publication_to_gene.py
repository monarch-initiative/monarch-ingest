import uuid

from koza.cli_runner import koza_app

from biolink.pydanticmodel import InformationContentEntityToNamedThingAssociation

source_name = "rgd_publication_to_gene"

row = koza_app.get_row(source_name)

if not row["CURATED_REF_PUBMED_ID"]:
    koza_app.next_row()

gene_id='RGD:' + row["GENE_RGD_ID"]

id_list = row["CURATED_REF_PUBMED_ID"].split(';')
for each_id in id_list:

    publication_id = "PMID:" + each_id

    association = InformationContentEntityToNamedThingAssociation(
        id="uuid:" + str(uuid.uuid1()),
        subject=gene_id,
        predicate="biolink:mentions",
        object=publication_id,
        aggregator_knowledge_source=["infores:monarchinitiative"],
        primary_knowledge_source="infores:rgd"
    )

    koza_app.write(association)
