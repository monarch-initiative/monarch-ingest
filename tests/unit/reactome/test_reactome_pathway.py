import pytest


@pytest.fixture
def source_name():
    return "reactome_pathway"


@pytest.fixture
def script():
    return "./monarch_ingest/reactome/pathway.py"


@pytest.fixture
def basic_row():
    return {
        "ID": "R-BTA-73843",
        "Name": "5-Phosphoribose 1-diphosphate biosynthesis",
    }


@pytest.fixture
def basic_g2p(mock_koza, source_name, basic_row, script, global_table):
    return mock_koza(
        source_name,
        iter([basic_row]),
        script,
        global_table=global_table,
    )


def test_pathway_id(basic_g2p):
    pathway = basic_g2p[0]
    assert pathway.id == "REACT:R-BTA-73843"

