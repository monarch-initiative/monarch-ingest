import pytest


# This name must match the ingest name in the transform code
@pytest.fixture
def source_name():
    return "rgd_publication_to_gene"


# This is the location of the transform code
@pytest.fixture
def script():
    return "./src/monarch_ingest/ingests/rgd/publication_to_gene.py"


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


def test_association(basic_g2p):
    association = basic_g2p[0]
    assert association
    assert association.subject == "RGD:2533"
    assert association.object == "PMID:8106108"
    assert association.primary_knowledge_source == "infores:rgd"
    assert "infores:monarchinitiative" in association.aggregator_knowledge_source
