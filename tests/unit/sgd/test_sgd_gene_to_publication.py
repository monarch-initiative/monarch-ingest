import pytest


@pytest.fixture
def source_name():
    return "sgd_gene_to_publication"


@pytest.fixture
def script():
    return "./monarch_ingest/sgd/gene_to_publication.py"


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


def test_gene(basic_g2p):
    gene = basic_g2p[0]
    assert gene
    assert gene.id == "SGD:YHR030C"


def test_publication(basic_g2p):
    publication = basic_g2p[1]
    assert publication
    assert publication.id == "PMID:9770551"


def test_association(basic_g2p):
    association = basic_g2p[2]
    assert association
    assert association.subject == "SGD:YHR030C"
    assert association.object == "PMID:9770551"
