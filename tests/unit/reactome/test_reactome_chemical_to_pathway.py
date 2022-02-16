import pytest


@pytest.fixture
def source_name():
    return "reactome_chemical_to_pathway"


@pytest.fixture
def script():
    return "./monarch_ingest/reactome/chemical_to_pathway.py"


@pytest.fixture
def basic_row():
    return {
        "component": "10033",
        "pathway_id": "R-RNO-6806664",
    }


@pytest.fixture
def basic_g2p(mock_koza, source_name, basic_row, script, global_table):
    return mock_koza(
        source_name,
        iter([basic_row]),
        script,
        global_table=global_table,
    )


def test_chemical(basic_g2p):
    chemical = basic_g2p[0]
    assert chemical
    assert chemical.id == "CHEBI:10033"


def test_pathway(basic_g2p):
    pathway = basic_g2p[1]
    assert pathway
    assert pathway.id == "REACT:R-RNO-6806664"


def test_association(basic_g2p):
    association = basic_g2p[2]
    assert association
    assert association.subject == "CHEBI:10033"
    assert association.object == "REACT:R-RNO-6806664"
