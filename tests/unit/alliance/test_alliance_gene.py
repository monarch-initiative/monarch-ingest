import pytest
from koza.utils.testing_utils import mock_koza  # noqa: F401


@pytest.fixture
def source_name():
    return "alliance_gene"


@pytest.fixture
def script():
    return "./src/monarch_ingest/ingests/alliance/gene.py"


@pytest.fixture
def pax2a_row():
    return {
        "symbol": "pax2a",
        "name": "paired box 2a",
        "soTermId": "SO:0001217",
        "basicGeneticEntity": {
            "synonyms": [
                "no isthmus",
                "pax2.1",
                "pax-b",
                "cb378",
                "pax[zf-b]",
                "pax2a1",
                "noi",
                "Pax-2",
                "Pax2.1",
                "paxb",
            ],
            "secondaryIds": ["ZFIN:ZDB-LOCUS-990215-377"],
            "primaryId": "ZFIN:ZDB-GENE-990415-8",
            "crossReferences": [
                {"id": "UniProtKB:Q90268", "pages": []},
                {"id": "NCBI_Gene:30425", "pages": []},
                {"id": "UniProtKB:F1QKT4", "pages": []},
                {"id": "UniProtKB:A0A0R4IAI2", "pages": []},
                {"id": "ENSEMBL:ENSDARG00000028148", "pages": []},
                {"id": "UniProtKB:F1R5S6", "pages": []},
                {"id": "UniProtKB:F1Q6N9", "pages": []},
                {"id": "UniProtKB:F1R6E2", "pages": []},
                {"id": "PANTHER:PTHR24329", "pages": []},
                {
                    "id": "ZFIN:ZDB-GENE-990415-8",
                    "pages": [
                        "gene",
                        "gene/expression",
                        "gene/wild_type_expression",
                        "gene/expression_images",
                        "gene/references",
                    ],
                },
                {"id": "UniProtKB:F1QEK2", "pages": []},
                {"id": "UniProtKB:F1QHP2", "pages": []},
                {"id": "UniProtKB:B8JJS3", "pages": []},
                {"id": "UniProtKB:B8JJS4", "pages": []},
            ],
            "genomeLocations": [
                {
                    "assembly": "GRCz11",
                    "chromosome": "13",
                    "startPosition": 29770837,
                    "endPosition": 29803764,
                }
            ],
            "taxonId": "NCBITaxon:7955",
        },
    }


@pytest.fixture
def no_synonym_row():
    return {
        "symbol": "evx2",
        "name": "even-skipped homeobox 2",
        "soTermId": "SO:0001217",
        "basicGeneticEntity": {
            "secondaryIds": ["ZFIN:ZDB-EST-990707-74"],
            "primaryId": "ZFIN:ZDB-GENE-980526-215",
            "crossReferences": [
                {"id": "UniProtKB:Q6PFR9", "pages": []},
                {"id": "NCBI_Gene:30479", "pages": []},
                {"id": "PANTHER:PTHR24329", "pages": []},
                {"id": "UniProtKB:Q98863", "pages": []},
                {
                    "id": "ZFIN:ZDB-GENE-980526-215",
                    "pages": [
                        "gene",
                        "gene/expression",
                        "gene/wild_type_expression",
                        "gene/expression_images",
                        "gene/references",
                    ],
                },
                {"id": "ENSEMBL:ENSDARG00000059255", "pages": []},
            ],
            "genomeLocations": [
                {
                    "assembly": "GRCz11",
                    "chromosome": "9",
                    "startPosition": 2002701,
                    "endPosition": 2007106,
                }
            ],
            "taxonId": "NCBITaxon:7955",
        },
    }


@pytest.fixture
def no_name_row():
    return {
        "basicGeneticEntity": {
            "crossReferences": [
                {"id": "ENSEMBL:WBGene00000646"},
                {"id": "NCBI_Gene:186749"},
                {"id": "UniProtKB:O61209"},
                {
                    "id": "WB:WBGene00000646",
                    "pages": [
                        "gene",
                        "gene/expression",
                        "gene/references",
                        "gene/expression_images",
                    ],
                },
                {"id": "WB:H17B01.2", "pages": ["gene/spell"]},
            ],
            "genomeLocations": [
                {
                    "assembly": "WBcel235",
                    "chromosome": "II",
                    "endPosition": 1472260,
                    "startPosition": 1470565,
                    "strand": "+",
                }
            ],
            "primaryId": "WB:WBGene00000646",
            "synonyms": ["CELE_H17B01.2", "col-70"],
            "taxonId": "NCBITaxon:6239",
        },
        "geneSynopsis": "Is affected by several genes including daf-2; glp-1; and rrf-3 based on microarray; tiling array; proteomic; and RNA-seq studies. Is affected by twenty-two chemicals including Mercuric Chloride; rotenone; and Tunicamycin based on microarray and RNA-seq studies.",
        "soTermId": "SO:0001217",
        "symbol": "H17B01.2",
    }


@pytest.fixture
def pax2a(mock_koza, source_name, pax2a_row, taxon_label_map_cache, script, global_table):
    return mock_koza(
        source_name,
        pax2a_row,
        script,
        map_cache=taxon_label_map_cache,
        global_table=global_table,
    )


@pytest.fixture
def no_synonym_gene(mock_koza, source_name, no_synonym_row, taxon_label_map_cache, script, global_table):
    return mock_koza(
        source_name,
        no_synonym_row,
        script,
        map_cache=taxon_label_map_cache,
        global_table=global_table,
    )


@pytest.fixture
def no_name_gene(mock_koza, source_name, no_name_row, taxon_label_map_cache, script, global_table):
    return mock_koza(
        source_name,
        no_name_row,
        script,
        map_cache=taxon_label_map_cache,
        global_table=global_table,
    )


def test_gene_information_gene(pax2a):
    assert len(pax2a) == 1
    gene = pax2a[0]
    assert gene


def test_gene_taxon(pax2a):
    gene = pax2a[0]
    assert "NCBITaxon:7955" in gene.in_taxon
    assert gene.in_taxon_label == "Danio rerio"


def test_gene_information_synonym(pax2a):
    gene = pax2a[0]
    assert gene.synonym
    assert "no isthmus" in gene.synonym


def test_gene_information_id(pax2a):
    gene = pax2a[0]
    assert gene.id == "ZFIN:ZDB-GENE-990415-8"


def test_gene_information_no_synonyms(no_synonym_gene):
    gene = no_synonym_gene[0]
    assert gene.synonym is None or len(gene.synonym) == 0


def test_gene_information_no_name_gene_uses_symbol(no_name_gene):
    gene = no_name_gene[0]
    assert gene
    assert gene.name == gene.symbol
