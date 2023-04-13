from typing import Dict, List
import pytest

from biolink.pydanticmodel import GeneToPhenotypicFeatureAssociation
from monarch_ingest.ingests.dictybase.utils import parse_phenotypes


@pytest.fixture
def map_cache() -> Dict:
    """
    :return: Multi-level mock map_cache of test Dictybase Gene & Phenotype, Names to Identifiers.
    """

    dictybase_phenotype_names_to_ids = {
        "decreased slug migration": {"id": "DDPHENO:0000225"},
        "aberrant spore morphology": {"id": "DDPHENO:0000163"},
        "delayed aggregation": {"id": "DDPHENO:0000156"},
        "increased cell-substrate adhesion": {"id": "DDPHENO:0000213"},
        "decreased cell motility": {"id": "DDPHENO:0000148"}
    }

    return {
        "dictybase_phenotype_names_to_ids": dictybase_phenotype_names_to_ids,
    }


@pytest.mark.parametrize(
    "query",
    [
        (
            {
                # empty 'Phenotypes' field
                "Phenotypes": None
            },
            None
        ),
        (
            {
                # Unrecognized phenotype
                "Phenotypes": "this is not a phenotype"
            },
            None
        ),
        (
            {
                # Single known phenotype mappings (with flanking blank space?)
                "Phenotypes": " decreased slug migration "
            },
            "DDPHENO:0000225"
        ),
        (
            {
                # Multiple known phenotype mappings
                "Phenotypes": " decreased slug migration | aberrant spore morphology "
            },
            "DDPHENO:0000163"
        )
    ]
)
def test_parse_phenotypes(query, map_cache):
    phenotypes: List[str] = parse_phenotypes(query[0], map_cache["dictybase_phenotype_names_to_ids"])
    assert query[1] in phenotypes if phenotypes else not query[1]  # sample one, unless None expected


@pytest.fixture
def source_name():
    """
    :return: string source name of Dictybase Gene to Phenotype ingest
    """
    return "dictybase_gene_to_phenotype"


@pytest.fixture
def script():
    """
    :return: string path to Dictybase Gene to Phenotype ingest script
    """
    return "./src/monarch_ingest/ingests/dictybase/gene_to_phenotype.py"


@pytest.fixture
def test_row_1():
    """
    :return: Test Dictybase Gene to Phenotype data row.
    """
    return {
        "Systematic_Name": "DBS0235594",
        "Strain_Descriptor": "CHE10",
        "Associated gene(s)": "cbpC",
        "DDB_G_ID": "DDB_G0283613",
        "Phenotypes": " decreased slug migration | aberrant spore morphology "
    }


@pytest.fixture
def basic_dictybase_1(mock_koza, source_name, script, test_row_1, global_table, map_cache):
    """
    Mock Koza run for Dictybase Gene to Phenotype ingest.

    :param mock_koza:
    :param source_name:
    :param test_row_1:
    :param script:
    :param global_table:
    :param map_cache:

    :return: mock_koza application
    """
    return mock_koza(
        name=source_name,
        data=iter([test_row_1]),
        transform_code=script,
        global_table=global_table,
        map_cache=map_cache
    )


@pytest.mark.parametrize(
    "cls", [GeneToPhenotypicFeatureAssociation]
)
def test_confirm_one_of_each_classes(cls, basic_dictybase_1):
    class_entities = [entity for entity in basic_dictybase_1 if isinstance(entity, cls)]
    assert class_entities
    assert len(class_entities) == 2
    assert class_entities[0]


def test_dictybase_g2p_association_ncbi_gene(basic_dictybase_1):
    associations = [
        association
        for association in basic_dictybase_1
        if isinstance(association, GeneToPhenotypicFeatureAssociation)
    ]
    assert len(associations) == 2

    for association in associations:
        assert association
        assert association.subject == "dictyBase:DDB_G0283613"
        assert association.object in ["DDPHENO:0000225", "DDPHENO:0000163"]
        assert association.predicate == "biolink:has_phenotype"
        assert association.primary_knowledge_source == "infores:dictybase"
        assert "infores:monarchinitiative" in association.aggregator_knowledge_source


@pytest.fixture
def test_row_2():
    """
    :return: another Test Dictybase Gene to Phenotype data row.
    """
    return {
        "Systematic Name": "DBS0351079",
        "Strain Descriptor": "DDB_G0274679-",
        "Associated gene(s)": "DDB_G0274679",
        "DDB_G_ID": "DDB_G0283613",
        "Phenotypes": "delayed aggregation | increased cell-substrate adhesion | decreased cell motility"
    }


@pytest.fixture
def basic_dictybase_2(mock_koza, source_name, script, test_row_2, global_table, map_cache):
    """
    Mock Koza run for Dictybase Gene to Phenotype ingest.

    :param mock_koza:
    :param source_name:
    :param test_row_2:
    :param script:
    :param global_table:
    :param map_cache:

    :return: mock_koza application
    """
    return mock_koza(
        name=source_name,
        data=iter([test_row_2]),
        transform_code=script,
        global_table=global_table,
        map_cache=map_cache
    )


def test_dictybase_g2p_association_dictybase_gene(basic_dictybase_2):
    associations = [
        association
        for association in basic_dictybase_2
        if isinstance(association, GeneToPhenotypicFeatureAssociation)
    ]
    assert len(associations) == 3

    for association in associations:
        assert association
        assert association.subject == "dictyBase:DDB_G0283613"
        assert association.object in ["DDPHENO:0000156", "DDPHENO:0000213", "DDPHENO:0000148"]
        assert association.predicate == "biolink:has_phenotype"
        assert association.primary_knowledge_source == "infores:dictybase"
        assert "infores:monarchinitiative" in association.aggregator_knowledge_source
