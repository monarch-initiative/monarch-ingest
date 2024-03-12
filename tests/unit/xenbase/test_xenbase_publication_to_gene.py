import pytest
from biolink_model.datamodel.pydanticmodel_v2 import Gene, InformationContentEntityToNamedThingAssociation, Publication
from koza.cli_runner import get_translation_table
from loguru import logger


@pytest.fixture
def gene_literature_entities(mock_koza, global_table):
    row = iter(
        [
            {
                "xb_article": "XB-ART-1",
                "pmid": "16938438",
                "gene_pages": "XB-GENEPAGE-487723 nog,XB-GENEPAGE-490377 msx1,XB-GENEPAGE-481828 bmp2,XB-GENEPAGE-483057 bmp4,XB-GENEPAGE-480982 fgf8,XB-GENEPAGE-6045068 hspa1l,XB-GENEPAGE-485625 hsp70",
            }
        ]
    )
    map_cache = {
        "genepage-2-gene": {
            "XB-GENEPAGE-487723": {
                "tropicalis_id": "XB-GENE-487724",
                "laevis_l_id": "XB-GENE-864891",
                "laevis_s_id": "XB-GENE-17332089",
            },
            "XB-GENEPAGE-490377": {
                "tropicalis_id": "XB-GENE-490378",
                "laevis_l_id": "XB-GENE-490382",
                "laevis_s_id": "XB-GENE-6253888",
            },
            "XB-GENEPAGE-481828": {
                "tropicalis_id": "XB-GENE-481829",
                "laevis_l_id": "XB-GENE-6252323",
                "laevis_s_id": "XB-GENE-481833",
            },
            "XB-GENEPAGE-483057": {
                "tropicalis_id": "XB-GENE-483058",
                "laevis_l_id": "XB-GENE-483062",
                "laevis_s_id": "XB-GENE-6254046",
            },
            "XB-GENEPAGE-480982": {
                "tropicalis_id": "XB-GENE-480983",
                "laevis_l_id": "XB-GENE-865429",
                "laevis_s_id": "XB-GENE-17330198",
            },
            "XB-GENEPAGE-6045068": {
                "tropicalis_id": "XB-GENE-6045069",
                "laevis_l_id": "XB-GENE-17342842",
                "laevis_s_id": "XB-GENE-6254949",
            },
            "XB-GENEPAGE-485625": {
                "tropicalis_id": "XB-GENE-485626",
                "laevis_l_id": "XB-GENE-485630",
                "laevis_s_id": "XB-GENE-17340402",
            },
        }
    }
    get_translation_table("src/monarch_ingest/translation_table.yaml", None, logger),

    return mock_koza(
        name="xenbase_publication_to_gene",
        data=row,
        transform_code="./src/monarch_ingest/ingests/xenbase/publication_to_gene.py",
        map_cache=map_cache,
        global_table=global_table,
    )


def test_gene_literature_entities(gene_literature_entities):
    assert gene_literature_entities


def test_gene_literature_entity_types(gene_literature_entities):
    publications = [entity for entity in gene_literature_entities if isinstance(entity, Publication)]
    [entity for entity in gene_literature_entities if isinstance(entity, Gene)]
    association = [
        entity
        for entity in gene_literature_entities
        if isinstance(entity, InformationContentEntityToNamedThingAssociation)
    ][0]

    # Simple assertion, do any associations exist. Could be more rigorous
    assert association.primary_knowledge_source == "infores:xenbase"
    assert "infores:monarchinitiative" in association.aggregator_knowledge_source
