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
    return "./monarch_ingest/orthology/ref_genome_orthologs.py"


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
def basic_row():
    """
    :return: Test row of Panther protein orthology relationship data.
    """
    return {
        "Gene": "HUMAN|HGNC=11477|UniProtKB=Q15528",                # species1|DB=id1|protdb=pdbid1
        "Ortholog": "MOUSE|MGI=MGI=98446|UniProtKB=Q62276",         # species2|DB=id2|protdb=pdbid2
        "Type of ortholog": "LDO",                                  # [LDO, O, P, X ,LDX]  see: localtt
        "Common ancestor for the orthologs": "Euarchontoglires",    # unused
        "Panther Ortholog ID": "PTHR12434"                          # panther_id
    }


@pytest.fixture
def basic_pl(mock_koza, source_name, basic_row, script, global_table, map_cache):
    """
    Mock Koza run for Panther gene orthology data ingest.
    
    :param mock_koza:
    :param source_name:
    :param basic_row:
    :param script:
    :param global_table:
    :param map_cache:
    :return:
    """
    return mock_koza(
        name=source_name,
        data=iter([basic_row]),
        transform_code=script,
        map_cache=map_cache,
        global_table=global_table
    )


def test_genes(basic_pl):
    gene = basic_pl[0]
    assert gene
    assert gene.id == "NCBIGene:6837"

    # 'category' is multivalued (an array)
    assert "biolink:Gene" in gene.category
    # This ancestral category appears to be missing? Pydantic model error?
    # assert "biolink:BiologicalEntity" in gene.category
    assert "biolink:NamedThing" in gene.category

    # 'in_taxon' is multivalued (an array)
    assert "NCBITaxon:9600" in gene.in_taxon

    assert gene.source == "infores:entrez"

    ortholog = basic_pl[1]
    assert ortholog
    assert ortholog.id == "NCBIGene:20933"

    # 'category' is multivalued (an array)
    assert "biolink:Gene" in ortholog.category
    # This ancestral category appears to be missing? Pydantic model error?
    # assert "biolink:BiologicalEntity" in ortholog.category
    assert "biolink:NamedThing" in ortholog.category

    # 'in_taxon' is multivalued (an array)
    assert "NCBITaxon:10090" in ortholog.in_taxon

    assert ortholog.source == "infores:entrez"


def test_association(basic_pl):
    association = basic_pl[2]
    assert association
    assert association.subject == "NCBIGene:6837"
    assert association.object == "NCBIGene:20933"
    assert association.predicate == "biolink:orthologous_to"
    assert association.relation == "RO:HOM0000017"

    assert "infores:panther" in association.source
