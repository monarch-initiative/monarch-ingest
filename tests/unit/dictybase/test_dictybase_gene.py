from typing import Dict
import pytest

from monarch_ingest.ingests.dictybase.utils import parse_gene_id


@pytest.fixture
def map_cache() -> Dict:
    """
    :return: Multi-level mock map_cache of Dictybase Gene  Names to Identifiers.
    """
    return {
        "DDB_G0267364_RTE": {"Gene ID": "DDB_G0267364"},
        "argE": {"Gene ID": "DDB_G0267380"},
        "DDB_G0269812": {"Gene ID": "DDB_G0269812"}
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
            "dictyBase:DDB_G0267380"
        ),
        (
            {
                # gene id like (Retro Transposable Element?)
                "Associated gene(s)": "DDB_G0267364_RTE"
            },
            "dictyBase:DDB_G0267364"
        ),
        (
            {
                # regular gene locus
                "Associated gene(s)": "DDB_G0269812"
            },
            "dictyBase:DDB_G0269812"
        ),
    ]
)
def test_parse_gene_id(query, map_cache):
    gene_id: str = parse_gene_id(query[0], map_cache)
    assert gene_id == query[1]
