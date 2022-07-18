from typing import Dict, List
import pytest

from biolink.pydanticmodel import GeneToPhenotypicFeatureAssociation
from monarch_ingest.ingests.dictybase.utils import parse_phenotypes


@pytest.fixture
def map_cache() -> Dict:
    """
    :return: Multi-level mock map_cache of test Dictybase Gene & Phenotype, Names to Identifiers.
    """
    dictybase_gene_names_to_ids = {
        "cbpC": {"GENE ID": "DDB_G0283613"},
        "DDB_G0267364_RTE": {"GENE ID": "DDB_G0267364"},
        "argE": {"GENE ID": "DDB_G0267380"},
        "DDB_G0269812": {"GENE ID": "DDB_G0269812"}
    }
    dictybase_phenotype_names_to_ids = {
        "decreased slug migration": {"id": "DDPHENO:0000225"},
        "aberrant spore morphology": {"id": "DDPHENO:0000163"}
    }
    return {
        "dictybase_gene_names_to_ids": dictybase_gene_names_to_ids,
        "dictybase_phenotype_names_to_ids": dictybase_phenotype_names_to_ids
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
    return "./monarch_ingest/ingests/dictybase/gene_to_phenotype.py"


@pytest.fixture
def test_row():
    """
    :return: Test Dictybase Gene to Phenotype data row.
    """
    return {
        "Systematic Name": "DBS0235594",
        "Strain Descriptor": "CHE10",
        "Associated gene(s)": "cbpC",
        "Phenotypes": " decreased slug migration | aberrant spore morphology "
    }


@pytest.fixture
def basic_dictybase(mock_koza, source_name, script, test_row, global_table, map_cache):
    """
    Mock Koza run for Dictybase Gene to Phenotype ingest.

    :param mock_koza:
    :param source_name:
    :param test_row:
    :param script:
    :param global_table:
    :param map_cache:

    :return: mock_koza application
    """
    return mock_koza(
        name=source_name,
        data=iter([test_row]),
        transform_code=script,
        global_table=global_table,
        map_cache=map_cache
    )


@pytest.mark.parametrize(
    "cls", [GeneToPhenotypicFeatureAssociation]
)
def confirm_one_of_each_classes(cls, basic_dictybase):
    class_entities = [entity for entity in basic_dictybase if isinstance(entity, cls)]
    assert class_entities
    assert len(class_entities) == 1
    assert class_entities[0]


def test_dictybase_g2p_association(basic_dictybase):
    associations = [
        association
        for association in basic_dictybase
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
