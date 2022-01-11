import pytest


@pytest.fixture
def source_name():
    return "string_protein_links"


@pytest.fixture
def script():
    return "./monarch_ingest/string/protein_links.py"


@pytest.fixture
def basic_row():
    return {
        "protein1": "10090.ENSMUSP00000000001",
        "protein2": "10090.ENSMUSP00000020316",
        "neighborhood": "0",
        "fusion": "0",
        "cooccurence": "0",
        "coexpression": "116",
        "experimental": "90",
        "database": "0",
        "textmining": "67",
        "combined_score": "183"
    }


@pytest.fixture
def basic_pl(mock_koza, source_name, basic_row, script, global_table):
    return mock_koza(
        source_name,
        iter([basic_row]),
        script,
        global_table=global_table,
    )


def test_proteins(basic_pl):
    protein_a = basic_pl[0]
    assert protein_a
    assert protein_a.id == "ENSEMBL:ENSMUSP00000000001"

    # 'category' is multivalued (an array)
    assert "biolink:Protein" in protein_a.category
    assert "biolink:Polypeptide" in protein_a.category
    assert "biolink:NamedThing" in protein_a.category

    # 'in_taxon' is multivalued (an array)
    assert "NCBITaxon:10090" in protein_a.in_taxon
    
    assert protein_a.source == "ENSEMBL"

    protein_b = basic_pl[1]
    assert protein_b
    assert protein_b.id == "ENSEMBL:ENSMUSP00000020316"

    # 'category' is multivalued (an array)
    assert "biolink:Protein" in protein_b.category
    assert "biolink:Polypeptide" in protein_b.category
    assert "biolink:NamedThing" in protein_b.category

    # 'in_taxon' is multivalued (an array)
    assert "NCBITaxon:10090" in protein_b.in_taxon
    
    assert protein_b.source == "ENSEMBL"


def test_association(basic_pl):
    association = basic_pl[2]
    assert association
    assert association.subject == "ENSEMBL:ENSMUSP00000000001"
    assert association.object == "ENSEMBL:ENSMUSP00000020316"
    assert association.predicate == "biolink:interacts_with"
    assert association.relation == "RO:0002434"
    
    # 'provided_by' is multivalued (an array)
    assert "infores:string" in association.provided_by
