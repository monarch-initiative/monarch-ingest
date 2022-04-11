import pytest


@pytest.fixture
def source_name():
    return "ncbi_gene"


@pytest.fixture
def script():
    return "./monarch_ingest/ncbi-gene/gene.py"


@pytest.fixture
def pax2a_row():
    return {
        "GeneID": "373854",
        "Symbol": "TENM2",
        "description": "teneurin transmembrane protein 2",
        "tax_id": "9031"
    }


@pytest.fixture
def pax2a(mock_koza, source_name, pax2a_row, script, global_table):
    row = iter([pax2a_row])
    return mock_koza(
        source_name,
        row,
        script,
        global_table=global_table,
    )


def test_gene_information_gene(pax2a):
    assert len(pax2a) == 1
    gene = pax2a[0]
    assert gene


def test_gene_information_id(pax2a):
    gene = pax2a[0]
    assert gene.id == "NCBIGene:373854"


def test_gene_information_symbol(pax2a):
    gene = pax2a[0]
    assert gene.symbol == "TENM2"


def test_gene_information_description(pax2a):
    gene = pax2a[0]
    assert gene.description == "teneurin transmembrane protein 2"





