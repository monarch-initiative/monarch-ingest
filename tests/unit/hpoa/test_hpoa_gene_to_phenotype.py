import pytest
from biolink_model.datamodel.pydanticmodel_v2 import GeneToPhenotypicFeatureAssociation
from koza.utils.testing_utils import mock_koza  # noqa: F401


@pytest.fixture
def source_name():
    """
    :return: string source name of HPOA Gene to Phenotype ingest
    """
    return "hpoa_gene_to_phenotype"


@pytest.fixture
def script():
    """
    :return: string path to HPOA Gene to Phenotype ingest script
    """
    return "./src/monarch_ingest/ingests/hpoa/gene_to_phenotype.py"


@pytest.fixture
def test_row():
    """
    :return: Test HPOA Gene to Phenotype data row.
    """
    return {
        "ncbi_gene_id": "8192",
        "gene_symbol": "CLPP",
        "hpo_id": "HP:0000252",
        "hpo_name": "Microcephaly",
    }


@pytest.fixture
def basic_hpoa(mock_koza, source_name, script, test_row):
    """
    Mock Koza run for HPOA Gene to Phenotype ingest.

    :param mock_koza:
    :param source_name:
    :param test_row:
    :param script:

    :return: mock_koza application
    """
    return mock_koza(name=source_name, data=test_row, transform_code=script)


@pytest.mark.parametrize("cls", [GeneToPhenotypicFeatureAssociation])
def test_confirm_one_of_each_classes(cls, basic_hpoa):
    class_entities = [entity for entity in basic_hpoa if isinstance(entity, cls)]
    assert class_entities
    assert len(class_entities) == 1
    assert class_entities[0]


def test_hpoa_g2p_association(basic_hpoa):
    assert basic_hpoa
    assert len(basic_hpoa) == 1
    association = [entity for entity in basic_hpoa if isinstance(entity, GeneToPhenotypicFeatureAssociation)][0]
    assert len(basic_hpoa) == 1
    assert basic_hpoa[0]
    assert basic_hpoa[0].subject == "NCBIGene:8192"
    assert basic_hpoa[0].object == "HP:0000252"
    assert basic_hpoa[0].predicate == "biolink:has_phenotype"
    assert association.primary_knowledge_source == "infores:hpo-annotations"
    assert "infores:monarchinitiative" in association.aggregator_knowledge_source
