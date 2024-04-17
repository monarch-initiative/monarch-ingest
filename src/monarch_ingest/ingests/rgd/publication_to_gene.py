import uuid

from koza.cli_runner import get_koza_app

from biolink_model.datamodel.pydanticmodel_v2 import InformationContentEntityToNamedThingAssociation, AgentTypeEnum, \
    KnowledgeLevelEnum

koza_app = get_koza_app("rgd_publication_to_gene")

while (row := koza_app.get_row()) is not None:

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
            primary_knowledge_source="infores:rgd",
            knowledge_level=KnowledgeLevelEnum.knowledge_assertion,
            agent_type=AgentTypeEnum.manual_agent
        )

        koza_app.write(association)
