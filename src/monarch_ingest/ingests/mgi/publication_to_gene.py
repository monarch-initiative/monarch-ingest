import uuid

from koza.cli_runner import get_koza_app

from biolink_model.datamodel.pydanticmodel_v2 import InformationContentEntityToNamedThingAssociation, AgentTypeEnum, \
    KnowledgeLevelEnum

koza_app = get_koza_app("mgi_publication_to_gene")

while (row := koza_app.get_row()) is not None:

    gene_id=row["MGI Marker Accession ID"]

    relation = koza_app.translation_table.resolve_term("mentions")

    pub_ids = row["PubMed IDs"].split("|")

    for pub_id in pub_ids:

        pmid = "PMID:" + pub_id

        association = InformationContentEntityToNamedThingAssociation(
            id="uuid:" + str(uuid.uuid1()),
            subject=pmid,
            predicate="biolink:mentions",
            object=gene_id,
            aggregator_knowledge_source=["infores:monarchinitiative"],
            primary_knowledge_source="infores:mgi",
            knowledge_level=KnowledgeLevelEnum.knowledge_assertion,
            agent_type=AgentTypeEnum.manual_agent
        )

        koza_app.write(association)
