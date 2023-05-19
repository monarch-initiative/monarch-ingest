import pytest


@pytest.fixture
def source_name():
    return "reactome_gene_to_pathway"


@pytest.fixture
def script():
    return "./src/monarch_ingest/ingests/reactome/gene_to_pathway.py"


@pytest.fixture(scope="package")
def local_table():
    """
    :return: string path to Reactome annotation term mappings file
    """
    return "src/monarch_ingest/ingests/reactome/reactome_id_mapping.yaml"


@pytest.fixture
def basic_row():
    return {
        "component": "8627890",
        "pathway_id": "R-DDI-73762",
        "go_ecode": "IEA",
        "species_nam": "Dictyostelium discoideum",
    }


@pytest.fixture
def basic_g2p(mock_koza, source_name, basic_row, script, global_table, local_table):
    return mock_koza(source_name, iter([basic_row]), script, global_table=global_table, local_table=local_table)


def test_association(basic_g2p):
    assert len(basic_g2p) == 1
    association = basic_g2p[0]
    assert association
    assert association.subject == "NCBIGene:8627890"
    assert association.predicate == "biolink:participates_in"
    assert association.object == "REACT:R-DDI-73762"
    assert "ECO:0000501" in association.has_evidence
    assert association.primary_knowledge_source == "infores:reactome"
    assert "infores:monarchinitiative" in association.aggregator_knowledge_source
