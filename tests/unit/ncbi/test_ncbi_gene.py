import pytest


@pytest.fixture
def source_name():
    return "ncbi_gene"


@pytest.fixture
def script():
    return "./src/monarch_ingest/ingests/ncbi/gene.py"


@pytest.fixture
def gene_row():
    return {
        "GeneID": "373854",
        "Symbol": "TENM2",
        "description": "teneurin transmembrane protein 2",
        "tax_id": "9031",
    }


@pytest.fixture
def gene_entities(mock_koza, source_name, gene_row, script, taxon_label_map_cache, global_table):
    row = iter([gene_row])
    return mock_koza(
        source_name,
        row,
        script,
        map_cache=taxon_label_map_cache,
        global_table=global_table,
    )


def test_gene_information_gene(gene_entities):
    assert len(gene_entities) == 1
    gene = gene_entities[0]
    assert gene


def test_gene_information_id(gene_entities):
    gene = gene_entities[0]
    assert gene.id == "NCBIGene:373854"


def test_gene_information_symbol(gene_entities):
    gene = gene_entities[0]
    assert gene.symbol == "TENM2"


def test_gene_information_description(gene_entities):
    gene = gene_entities[0]
    assert gene.description == "teneurin transmembrane protein 2"
