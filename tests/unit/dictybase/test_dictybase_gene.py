from typing import List

import pytest
from biolink.pydanticmodel import Gene


@pytest.fixture
def source_name():
    """
    :return: string source name of Dictybase Gene ingest
    """
    return "dictybase_gene"


@pytest.fixture
def script():
    """
    :return: string path to Dictybase Gene ngest script
    """
    return "./src/monarch_ingest/ingests/dictybase/gene.py"


@pytest.fixture
def test_row_1():
    """
    :return: Test Dictybase Gene input data row.
    """
    return {'GENE ID': 'DDB_G0269222', 'Gene Name': 'gefB', 'Synonyms': 'RasGEFB, RasGEF'}


@pytest.fixture
def basic_dictybase_1(mock_koza, source_name, script, test_row_1, global_table):
    """
    Mock Koza run for Dictybase Gene ingest.

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
    )


def test_dictybase_ncbi_mapped_gene_ingest(basic_dictybase_1):
    entity: List[Gene] = [entity for entity in basic_dictybase_1 if isinstance(entity, Gene)]
    assert len(entity) == 1

    assert entity[0]
    assert entity[0].id == "dictyBase:DDB_G0269222"
    assert entity[0].symbol == "gefB"
    assert entity[0].name == "gefB"
    assert 'RasGEFB' in entity[0].synonym
    assert 'RasGEF' in entity[0].synonym
    assert "NCBITaxon:44689" in entity[0].in_taxon
    assert "infores:dictybase" in entity[0].provided_by
