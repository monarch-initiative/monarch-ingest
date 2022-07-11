import pytest

from biolink.pydanticmodel import GeneToPhenotypicFeatureAssociation


@pytest.fixture
def source_name():
    """
    :return: string source name of HPOA Gene to Phenotype ingest
    """
    return "hpoa_genes_to_phenotype"


@pytest.fixture
def script():
    """
    :return: string path to HPOA Gene to Phenotype ingest script
    """
    return "./monarch_ingest/ingests/hpoa/genes_to_phenotype.py"


@pytest.fixture
def test_row():
    """
    :return: Test HPOA Gene to Phenotype data row.
    """
    return {
        "entrez-gene-id": "8192",
        "entrez-gene-symbol": "CLPP",
        "HPO-Term-ID": "HP:0000252",
        "HPO-Term-Name": "Microcephaly",
        "Frequency-Raw": "-",
        "Frequency-HPO": "HP:0040283",
        "Additional Info from G-D source": "-",
        "G-D source": "mim2gene",
        "disease-ID for link": "OMIM:614129"
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
    return mock_koza(
        name=source_name,
        data=iter([test_row]),
        transform_code=script
    )


@pytest.mark.parametrize(
    "cls", [GeneToPhenotypicFeatureAssociation]
)
def test_confirm_one_of_each_classes(cls, basic_hpoa):
    class_entities = [entity for entity in basic_hpoa if isinstance(entity, cls)]
    assert class_entities
    assert len(class_entities) == 1
    assert class_entities[0]


def test_hpoa_g2p_association(basic_hpoa):
    assert basic_hpoa
    assert len(basic_hpoa) == 1
    association = [
        entity
        for entity in basic_hpoa
        if isinstance(entity, GeneToPhenotypicFeatureAssociation)
    ][0]
    assert len(basic_hpoa) == 1
    assert basic_hpoa[0]
    assert basic_hpoa[0].subject == "NCBIGene:8192"
    assert basic_hpoa[0].object == "HP:0000252"
    assert basic_hpoa[0].predicate == "biolink:has_phenotype"
    assert "OMIM:614129" in basic_hpoa[0].qualifiers  # Disease term
    assert "HP:0040283" in basic_hpoa[0].qualifiers   # Frequency term
    assert "mim2gene" in basic_hpoa[0].has_evidence
    assert "infores:hpoa" in basic_hpoa[0].source
    assert association.primary_knowledge_source == "infores:hpoa"
    assert "infores:monarchinitiative" in association.aggregator_knowledge_source
