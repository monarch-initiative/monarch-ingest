"""
Unit tests for Panther Gene Orthology relationships ingest
"""
import pytest


@pytest.fixture
def source_name():
    """
    :return: string source name of Panther Gene Orthology relationships ingest
    """
    return "panther_ref_genome_orthologs"


@pytest.fixture
def script():
    """
    :return: string path to Panther Gene Orthology relationships ingest script
    """
    return "./monarch_ingest/panther/ref_genome_orthologs.py"


@pytest.fixture
def map_cache():
    """
    :return: Multi-level mock map_cache Uniprot to Entrez GeneID dictionary (realistic looking but synthetic data)
    """
    uniprot_2_gene = {
        "Q15528": {"Entrez": "6837"},
        "Q62276": {"Entrez": "20933"},
    }
    return {"uniprot_2_gene": uniprot_2_gene}


@pytest.fixture
def test_rows():
    """
    :return: List of test GO Annotation data rows (realistic looking but synthetic data).
    """
    return [
        {
            "Gene": "HUMAN|HGNC=11477|UniProtKB=Q15528",                # species1|DB=id1|protdb=pdbid1
            "Ortholog": "MOUSE|MGI=MGI=98446|UniProtKB=Q62276",         # species2|DB=id2|protdb=pdbid2
            "Type of ortholog": "LDO",                                  # [LDO, O, P, X ,LDX]  see: localtt
            "Common ancestor for the orthologs": "Euarchontoglires",    # unused
            "Panther Ortholog ID": "PTHR12434"                          # panther_id
        },
        # Most of these other test rows don't generate any results
        # in the unit tests, but will generated logger messages?
        {
            # missing protein spec?
            "Gene": "HUMAN|HGNC=11477|",
            "Ortholog": "MOUSE|MGI=MGI=98446|UniProtKB=Q62276",
            "Type of ortholog": "LDO",
            "Common ancestor for the orthologs": "Euarchontoglires",
            "Panther Ortholog ID": "PTHR12434"
        },
        {
            # Unmappable protein ID?
            "Gene": "HUMAN|HGNC=11477|UniProtKB=A123B3",
            "Ortholog": "MOUSE|MGI=MGI=98446|UniProtKB=Q62276",
            "Type of ortholog": "LDO",
            "Common ancestor for the orthologs": "Euarchontoglires",
            "Panther Ortholog ID": "PTHR12434"
        },
        {
            # Non-target species ("AARDvark, lol")
            "Gene": "HUMAN|HGNC=11477|UniProtKB=Q15528",
            "Ortholog": "AARDV|AVD=98446|UniProtKB=Q62276",
            "Type of ortholog": "LDO",
            "Common ancestor for the orthologs": "Euarchontoglires",
            "Panther Ortholog ID": "PTHR12434"
        },
        {   # Empty gene (or ortholog) spec entry
            "Gene": "",
            "Ortholog": "MOUSE|MGI=MGI=98446|UniProtKB=Q62276",
            "Type of ortholog": "LDO",
            "Common ancestor for the orthologs": "Euarchontoglires",
            "Panther Ortholog ID": "PTHR12434"
        },
        {   # Ill formed Gene spec string
            "Gene": "HUMAN|HGNC=11477&UniProtKB=Q15528",  # species1|DB=id1|protdb=pdbid1
            "Ortholog": "MOUSE|MGI=MGI=98446|UniProtKB=Q62276",  # species2|DB=id2|protdb=pdbid2
            "Type of ortholog": "LDO",  # [LDO, O, P, X ,LDX]  see: localtt
            "Common ancestor for the orthologs": "Euarchontoglires",  # unused
            "Panther Ortholog ID": "PTHR12434"  # panther_id
        }
    ]


@pytest.fixture
def basic_pl(mock_koza, source_name, test_rows, script, global_table, map_cache):
    """
    Mock Koza run for Panther gene orthology data ingest.

    :param mock_koza:
    :param source_name:
    :param test_rows: a method returning a List of test data dictionary records
    :param script:
    :param global_table:
    :param map_cache:
    :return:
    """
    return mock_koza(
        name=source_name,
        data=iter(test_rows),
        transform_code=script,
        map_cache=map_cache,
        global_table=global_table
    )


result_expected = {
    # Test complete Panther record
    "NCBIGene:6837": [
        "NCBITaxon:9606",
        "NCBIGene:20933",
        "NCBITaxon:10090",
        "biolink:orthologous_to",
        "RO:HOM0000017"
    ]
}


def test_genes(basic_pl):

    gene = basic_pl[0]

    assert gene
    assert gene.id in result_expected.keys()

    # 'category' is multivalued (an array)
    assert "biolink:Gene" in gene.category
    # This ancestral category appears to be missing? Pydantic model error?
    # assert "biolink:BiologicalEntity" in gene.category
    assert "biolink:NamedThing" in gene.category

    # 'in_taxon' is multivalued (an array)
    assert result_expected[gene.id][0] in gene.in_taxon

    assert "infores:entrez" in gene.source

    ortholog = basic_pl[1]

    assert ortholog
    assert ortholog.id == result_expected[gene.id][1]

    # 'category' is multivalued (an array)
    assert "biolink:Gene" in ortholog.category
    # This ancestral category appears to be missing? Pydantic model error?
    # assert "biolink:BiologicalEntity" in ortholog.category
    assert "biolink:NamedThing" in ortholog.category

    # 'in_taxon' is multivalued (an array)
    assert result_expected[gene.id][2] in ortholog.in_taxon

    assert "infores:entrez" in ortholog.source


def test_association(basic_pl):
    association = basic_pl[2]
    assert association
    assert association.subject in result_expected.keys()
    assert association.object == result_expected[association.subject][1]
    assert association.predicate == result_expected[association.subject][3]
    assert association.relation == result_expected[association.subject][4]

    assert "infores:panther" in association.source
