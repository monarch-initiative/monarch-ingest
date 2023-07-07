import pytest


@pytest.fixture
def gene_information_entities(mock_koza, taxon_label_map_cache, global_table):
    row = {
        'gene_systematic_id': 'SPAC1002.06c',
        'gene_systematic_id_with_prefix': 'POMBASE:SPAC1002.06c',
        'gene_name': 'bqt2',
        'chromosome_id': 'chromosome_1',
        'gene_product': 'bouquet formation protein Bqt2',
        'uniprot_id': 'Q9US52',
        'gene type': 'protein coding gene',
        'synonyms': 'mug18,rec23',
    }

    return mock_koza(
        "pombase_gene",
        iter([row]),
        "./src/monarch_ingest/ingests/pombase/gene.py",
        map_cache=taxon_label_map_cache,
        global_table=global_table,
    )


def test_gene_information_gene(gene_information_entities):
    assert len(gene_information_entities) == 1
    gene = gene_information_entities[0]
    assert gene


def test_gene_information_synonym(gene_information_entities):
    gene = gene_information_entities[0]
    assert gene.synonym
    assert "rec23" in gene.synonym


def test_gene_information_id(gene_information_entities):
    gene = gene_information_entities[0]
    assert gene.id == "POMBASE:SPAC1002.06c"


def test_gene_xref(gene_information_entities):
    gene = gene_information_entities[0]
    assert "UniProtKB:Q9US52" in gene.xref
