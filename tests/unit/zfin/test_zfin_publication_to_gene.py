import pytest

from biolink.model import InformationContentEntityToNamedThingAssociation


@pytest.fixture
def basic_row():
    return {
        "Gene Symbol": "si:dkey-84j12.1",
        "Gene ID": "ZDB-GENE-060526-342",
        "Publication ID": "ZDB-PUB-140801-12",
        "Publication Type": "Journal",
        "PubMed ID": "25078621",
    }


@pytest.fixture
def basic_entities(mock_koza, basic_row, global_table):
    return mock_koza(
        "zfin_publication_to_gene",
        iter([basic_row]),
        "./monarch_ingest/ingests/zfin/publication_to_gene.py",
        global_table=global_table,
    )


# def test_gene(basic_entities):
#     gene = [entity for entity in basic_entities if isinstance(entity, Gene)][0]
#     assert gene.id == "ZFIN:ZDB-GENE-060526-342"


# def test_pub(basic_entities):
#     pub = [entity for entity in basic_entities if isinstance(entity, Publication)][0]
#     assert pub.id == "ZFIN:ZDB-PUB-140801-12"


def test_association(basic_entities):
    association = [
        entity
        for entity in basic_entities
        if isinstance(entity, InformationContentEntityToNamedThingAssociation)
    ]
    print(association)
    assert association[0].subject == "ZFIN:ZDB-PUB-140801-12"
    assert association[0].object == "ZFIN:ZDB-GENE-060526-342"
