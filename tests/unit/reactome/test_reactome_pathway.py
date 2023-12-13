import pytest


@pytest.fixture
def source_name():
    return "reactome_pathway"


@pytest.fixture
def script():
    return "./src/monarch_ingest/ingests/reactome/pathway.py"


@pytest.fixture(scope="package")
def local_table():
    """
    :return: string path to Reactome annotation term mappings file
    """
    return "src/monarch_ingest/ingests/reactome/reactome_id_mapping.yaml"


@pytest.fixture
def basic_row():
    return {"ID": "R-BTA-73843", "Name": "5-Phosphoribose 1-diphosphate biosynthesis", "species": "Bos taurus"}


@pytest.fixture
def basic_g2p(mock_koza, source_name, basic_row, script, global_table, local_table):
    return mock_koza(source_name, iter([basic_row]), script, global_table=global_table, local_table=local_table)


def test_pathway_id(basic_g2p):
    pathway = basic_g2p[0]
    assert pathway.id == "Reactome:R-BTA-73843"
    assert "infores:reactome" in pathway.provided_by
