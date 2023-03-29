import pytest


@pytest.fixture
def source_name():
    return "sgd_publication_to_gene"


@pytest.fixture
def script():
    return "./src/monarch_ingest/ingests/sgd/publication_to_gene.py"


@pytest.fixture
def basic_row():
    return {
        "gene name": "YHR030C",
        "PubMed ID": "9770551",
    }


@pytest.fixture
def basic_g2p(mock_koza, source_name, basic_row, script, global_table):
    return mock_koza(
        source_name,
        iter([basic_row]),
        script,
        global_table=global_table,
    )


def test_association(basic_g2p):
    association = basic_g2p[0]
    assert association
    assert association.subject == "SGD:YHR030C"
    assert association.object == "PMID:9770551"
    assert association.primary_knowledge_source == "infores:sgd"
    assert "infores:monarchinitiative" in association.aggregator_knowledge_source
