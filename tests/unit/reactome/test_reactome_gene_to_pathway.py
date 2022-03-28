import pytest


@pytest.fixture
def source_name():
    return "reactome_gene_to_pathway"


@pytest.fixture
def script():
    return "./monarch_ingest/reactome/gene_to_pathway.py"


@pytest.fixture
def basic_row():
    return {
        "component": "27890",
        "pathway_id": "R-BTA-8853659",
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
    assert association.subject == "ENSEMBL:27890"
    assert association.object == "REACT:R-BTA-8853659"
