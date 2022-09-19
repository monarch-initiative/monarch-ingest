import pytest


# This name must match the ingest name in the transform code
@pytest.fixture
def source_name():
    return "flybase_publication_to_gene"


# This is the location of the transform code
@pytest.fixture
def script():
    return "./monarch_ingest/ingests/flybase/publication_to_gene.py"


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


def test_association(basic_g2p):
    association = basic_g2p[0]
    assert association
    assert association.subject == "FB:FBgn0001098"
    assert association.object == "PMID:10199954"
    assert association.primary_knowledge_source == "infores:flybase"
    assert "infores:monarchinitiative" in association.aggregator_knowledge_source


@pytest.fixture
def basic_g2p_without_pmid(mock_koza, source_name, basic_row, script, global_table):
    basic_row['PubMed_id'] = None
    return mock_koza(
        source_name,
        iter([basic_row]),
        script,
        global_table=global_table,
    )
