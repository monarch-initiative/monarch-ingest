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
        "DDB_G0269812": {"GENE ID": "DDB_G0269812"},
        "DDB_G0284955": {"GENE ID": "DDB_G0284955"}
    }
    dicty_symbols_to_ncbi_genes = {
        "cbpC": {"NCBI GeneID": "8624175"},
        "argE": {"NCBI GeneID": "8615966"},
    }
    return {
        "dictybase_gene_names_to_ids": dictybase_gene_names_to_ids,
        "dicty_symbols_to_ncbi_genes": dicty_symbols_to_ncbi_genes
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
            ("NCBIGene:8615966", "argE")
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
    gene = parse_gene_id(
        query[0],
        map_cache["dictybase_gene_names_to_ids"],
        map_cache["dicty_symbols_to_ncbi_genes"]
    )
    assert gene == query[1]


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
    return "./monarch_ingest/ingests/dictybase/gene.py"


@pytest.fixture
def test_row_1():
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
def basic_dictybase_1(mock_koza, source_name, script, test_row_1, global_table, map_cache):
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
        data=iter([test_row_1]),
        transform_code=script,
        global_table=global_table,
        map_cache=map_cache
    )


def test_dictybase_ncbi_mapped_gene_ingest(basic_dictybase_1):
    entity: List[Gene] = [
        entity
        for entity in basic_dictybase_1
        if isinstance(entity, Gene)
    ]
    assert len(entity) == 1

    assert entity[0]
    assert entity[0].id == "NCBIGene:8624175"
    assert entity[0].symbol == "cbpC"
    assert entity[0].name == "cbpC"
    assert "NCBITaxon:44689" in entity[0].in_taxon
    assert "infores:dictybase" in entity[0].provided_by


@pytest.fixture
def test_row_2():
    """
    :return: Test Dictybase Gene input data row.
    """
    return {
        "Systematic Name": "DBS0351085",
        "Strain Descriptor": "DDB_G0284955-",
        "Associated gene(s)": "DDB_G0284955",
        "Phenotypes": "delayed aggregation | increased cell-substrate adhesion | decreased cell motility"
    }


@pytest.fixture
def basic_dictybase_2(mock_koza, source_name, script, test_row_2, global_table, map_cache):
    """
    Mock Koza run for Dictybase Gene ingest.

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


def test_dictybase_id_only_gene_ingest(basic_dictybase_2):
    entity: List[Gene] = [
        entity
        for entity in basic_dictybase_2
        if isinstance(entity, Gene)
    ]
    assert len(entity) == 1

    assert entity[0]
    assert entity[0].id == "dictyBase:DDB_G0284955"
    assert entity[0].symbol == "DDB_G0284955"
    assert entity[0].name == "DDB_G0284955"
    assert "NCBITaxon:44689" in entity[0].in_taxon
    assert "infores:dictybase" in entity[0].provided_by
