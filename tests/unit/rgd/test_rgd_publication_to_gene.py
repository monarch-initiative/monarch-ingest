import pytest


# This name must match the ingest name in the transform code
@pytest.fixture
def source_name():
    return "rgd_publication_to_gene"


# This is the location of the transform code
@pytest.fixture
def script():
    return "./monarch_ingest/rgd/publication_to_gene.py"


# Create a fixture for a full row, it should be relatively representative of the rows ingested, and can
# be modified for testing edge cases
@pytest.fixture
def basic_row():
    return {
        "GENE_RGD_ID": "2533",
        "CURATED_REF_PUBMED_ID": "8106108",
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
    assert gene.id == "RGD:2533"


def test_publication(basic_g2p):
    publication = basic_g2p[1]
    assert publication
    assert publication.id == "PMID:8106108"


def test_association(basic_g2p):
    association = basic_g2p[2]
    assert association
    assert association.subject == "RGD:2533"
    assert association.object == "PMID:8106108"


def test_association_duplicates(basic_g2p):
    association = basic_g2p[2]
    assert association
    assert association.subject == "RGD:2533"
    assert association.object == "PMID:8106108"
