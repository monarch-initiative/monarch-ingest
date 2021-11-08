import pytest


@pytest.fixture
def source_name():
    return "hgnc_gene_to_publication"


@pytest.fixture
def script():
    return "./monarch_ingest/hgnc/gene2publication.py"


@pytest.fixture
def basic_row():
    return {
        "hgnc_id": "HGNC:24086",
        "pubmed_id": "11072063",
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
    assert gene.id == "HGNC:24086"


def test_publication(basic_g2p):
    publication = basic_g2p[1]
    assert publication
    assert publication.id == "PMID:11072063"


def test_association(basic_g2p):
    association = basic_g2p[2]
    assert association
    assert association.subject == "HGNC:24086"
    assert association.object == "PMID:11072063"


