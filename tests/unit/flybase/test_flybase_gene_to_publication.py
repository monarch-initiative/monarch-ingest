import pytest


# This name must match the ingest name in the transform code
@pytest.fixture
def source_name():
    return "flybase_gene_to_publication"


# This is the location of the transform code
@pytest.fixture
def script():
    return "./monarch_ingest/flybase/gene_to_publication.py"


# Create a fixture for a full row, it should be relatively representative of the rows ingested, and can
# be modified for testing edge cases
@pytest.fixture
def basic_row():
    return {
        "entity_id": "FBgn0001098",
        "entity_name": "Gdh",
        "FlyBase_publication_id": "FBrf0108260",
        "PubMed_id": "10199954",
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
    assert gene.id == "FB:FBgn0001098"


def test_publication(basic_g2p):
    publication = basic_g2p[1]
    assert publication
    assert publication.id == "PMID:10199954"


def test_association(basic_g2p):
    association = basic_g2p[2]
    assert association
    assert association.subject == "FB:FBgn0001098"
    assert association.object == "PMID:10199954"


@pytest.fixture
def basic_g2p_without_pmid(mock_koza, source_name, basic_row, script, global_table):
    basic_row['PubMed_id'] = None
    return mock_koza(
        source_name,
        iter([basic_row]),
        script,
        global_table=global_table,
    )


def test_publication_withoutpmid(basic_g2p_without_pmid):
    publication = basic_g2p_without_pmid[1]
    assert publication
    assert publication.id == "FB:FBrf0108260"
