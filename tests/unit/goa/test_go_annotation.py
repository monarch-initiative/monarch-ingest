import pytest
from biolink_model_pydantic.model import PairwiseGeneToGeneInteraction


@pytest.fixture
def source_name():
    return "go_annotation"


@pytest.fixture
def script():
    return "./monarch_ingest/goa/go_annotation.py"


@pytest.fixture
def map_cache():
    # """
    # :return: Multi-level mock map_cache GO Annotation to entrez dictionary.
    # """
    # entrez_2_goa = {
    #     "10090.ENSMUSP00000000001": {"entrez": "14679"},
    #     "10090.ENSMUSP00000020316": {"entrez": "56480"},
    #     "9606.ENSP00000349467": {'entrez': '801|805|808'},
    #     "9606.ENSP00000000233": {'entrez': '123|381'}
    # }
    # return {"entrez_2_goa": entrez_2_goa}
    raise NotImplemented


@pytest.fixture
def basic_row():
    # """
    # :return: Test GO Annotation protein links data row.
    # """
    # return {
    #     "protein1": "10090.ENSMUSP00000000001",
    #     "protein2": "10090.ENSMUSP00000020316",
    #     "neighborhood": "0",
    #     "fusion": "0",
    #     "cooccurence": "0",
    #     "coexpression": "116",
    #     "experimental": "90",
    #     "database": "0",
    #     "textmining": "67",
    #     "combined_score": "183",
    # }
    raise NotImplemented


@pytest.fixture
def basic_goa(mock_koza, source_name, basic_row, script, global_table, map_cache):
    return mock_koza(
        name=source_name,
        data=iter([basic_row]),
        transform_code=script,
        map_cache=map_cache,
        global_table=global_table,
    )


def test_genes(basic_goa):
    gene_a = basic_goa[0]
    assert gene_a
    assert gene_a.id == "NCBIGene:14679"

    # 'category' is multivalued (an array)
    assert "biolink:Gene" in gene_a.category
    assert "biolink:NamedThing" in gene_a.category

    # 'in_taxon' is multivalued (an array)
    assert "NCBITaxon:10090" in gene_a.in_taxon

    assert gene_a.source == "entrez"

    gene_b = basic_goa[1]
    assert gene_b
    assert gene_b.id == "NCBIGene:56480"

    # 'category' is multivalued (an array)
    assert "biolink:Gene" in gene_b.category
    assert "biolink:NamedThing" in gene_b.category

    # 'in_taxon' is multivalued (an array)
    assert "NCBITaxon:10090" in gene_b.in_taxon

    assert gene_b.source == "entrez"


def test_association(basic_goa):
    association = basic_goa[2]
    assert association
    assert association.subject == "NCBIGene:14679"
    assert association.object == "NCBIGene:56480"
    # assert association.predicate == "biolink:interacts_with"
    # assert association.relation == "RO:0002434"

    assert "infores:goa" in association.source
    raise NotImplemented

@pytest.fixture
def multigene_row():
    # return {
    #     'protein1': '9606.ENSP00000000233',
    #     'protein2': '9606.ENSP00000349467',
    #     'neighborhood': '0',
    #     'fusion': '0',
    #     'cooccurence': '332',
    #     'coexpression': '62',
    #     'experimental': '77',
    #     'database': '0',
    #     'textmining': '101',
    #     'combined_score': 410,
    # }
    raise NotImplemented


@pytest.fixture
def multigene_entities(mock_koza, source_name, multigene_row, script, global_table, map_cache):
    # return mock_koza(
    #     name=source_name,
    #     data=iter([multigene_row]),
    #     transform_code=script,
    #     map_cache=map_cache,
    #     global_table=global_table,
    # )
    raise NotImplemented


def test_multigene_associations(multigene_entities):
    # associations = [
    #     association for association in multigene_entities 
    #     if isinstance(association, PairwiseGeneToGeneInteraction)
    # ]
    # assert len(associations) == 6
    raise NotImplemented
