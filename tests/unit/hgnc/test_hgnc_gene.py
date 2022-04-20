import pytest


@pytest.fixture
def source_name():
    return "hgnc_gene"


@pytest.fixture
def script():
    return "./monarch_ingest/hgnc/gene.py"


@pytest.fixture
def pax2a_row():
    return {
        "hgnc_id": "HGNC:24086",
        "pubmed_id": "11072063",
        "symbol": "A1CF",
        "name": "APOBEC1 complementation factor",
        "ensembl_gene_id": "ENSG00000148584",
        "omim_id": "618199",
        "alias_symbol": "ACF|ASP|ACF64|ACF65|APOBEC1CF",
        "alias_name": "",
        "prev_symbol": "",
        "prev_name": "",
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


def test_gene(pax2a):
    gene = pax2a[0]
    assert gene
    assert gene.id == "HGNC:24086"


def test_gene_information_synonym(pax2a):
    gene = pax2a[0]
    assert gene.synonym
    assert gene.synonym == ['ACF', 'ASP', 'ACF64', 'ACF65', 'APOBEC1CF', '', '', '']


def test_gene_information_xref(pax2a):
    gene = pax2a[0]
    assert gene.xref
    assert gene.xref == ['ENSEMBL:ENSG00000148584', 'OMIM:618199']


# Commenting out publication ingests at least temporarily
# def test_publication(pax2a):
#     publication = pax2a[1]
#     assert publication
#     assert publication.id == "PMID:11072063"
#
#
# def test_association(pax2a):
#     association = pax2a[2]
#     assert association
#     assert association.subject == "HGNC:24086"
#     assert association.object == "PMID:11072063"
