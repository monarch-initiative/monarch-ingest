from typing import Dict, List
import pytest

from biolink.pydanticmodel import Gene
from monarch_ingest.ingests.dictybase.utils import parse_gene_id


@pytest.fixture
def map_cache() -> Dict:
    """
    :return: Multi-level mock map_cache of test Dictybase Gene Names to Identifiers.
    """
    dictybase_gene_names_to_ids = {
        "cbpC": {"GENE ID": "DDB_G0283613"},
        "DDB_G0267364_RTE": {"GENE ID": "DDB_G0267364"},
        "argE": {"GENE ID": "DDB_G0267380"},
        "DDB_G0269812": {"GENE ID": "DDB_G0269812"}
    }
    return {
        "dictybase_gene_names_to_ids": dictybase_gene_names_to_ids
    }


@pytest.mark.parametrize(
    "query",
    [
        (
            {
                # empty gene field
                "Associated gene(s)": None
            },
            None
        ),
        (
            {
                # Multiple gene mappings - ignored
                "Associated gene(s)": "zplC-1 | zplC-2"
            },
            None
        ),
        (
            {
                # Multiple gene mappings - ignored
                "Associated gene(s)": "unknown_gene_name"
            },
            None
        ),
        (
            {
                # gene symbol
                "Associated gene(s)": "argE"
            },
            ("dictyBase:DDB_G0267380", "argE")
        ),
        (
            {
                # gene id like (Retro Transposable Element?)
                "Associated gene(s)": "DDB_G0267364_RTE"
            },
            ("dictyBase:DDB_G0267364", "DDB_G0267364_RTE")
        ),
        (
            {
                # regular gene locus
                "Associated gene(s)": "DDB_G0269812"
            },
            ("dictyBase:DDB_G0269812", "DDB_G0269812")
        ),
    ]
)
def test_parse_gene_id(query, map_cache):
    gene = parse_gene_id(query[0], map_cache["dictybase_gene_names_to_ids"])
    assert gene == query[1]


@pytest.fixture
def source_name():
    """
    :return: string source name of Dictybase Gene to Phenotype ingest
    """
    return "dictybase_gene"


@pytest.fixture
def script():
    """
    :return: string path to Dictybase Gene ngest script
    """
    return "./monarch_ingest/ingests/dictybase/gene.py"


@pytest.fixture
def test_row():
    """
    :return: Test Dictybase Gene input data row.
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
    Mock Koza run for Dictybase Gene ingest.

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
    "cls", [Gene]
)
def confirm_one_of_each_classes(cls, basic_dictybase):
    class_entities = [entity for entity in basic_dictybase if isinstance(entity, cls)]
    assert class_entities
    assert len(class_entities) == 1
    assert class_entities[0]


def test_dictybase_gene_ingest(basic_dictybase):
    entity: List[Gene] = [
        entity
        for entity in basic_dictybase
        if isinstance(entity, Gene)
    ]
    assert len(entity) == 1

    assert entity[0]
    assert entity[0].id == "dictyBase:DDB_G0283613"
    assert entity[0].symbol == "cbpC"
    assert entity[0].name == "cbpC"
    assert "NCBITaxon:44689" in entity[0].in_taxon
    assert "infores:dictybase" in entity[0].source
