import pytest
from biolink_model_pydantic.model import PairwiseGeneToGeneInteraction


@pytest.fixture
def source_name():
    """
    :return: string source name of GO Annotations ingest
    """
    return "go_annotation"


@pytest.fixture
def script():
    """
    :return: string path to GO Annotations ingest script
    """
    return "./monarch_ingest/goa/go_annotation.py"


@pytest.fixture
def basic_row():
    """
    :return: Test GO Annotation data row.
    """
    return {
        "DB": "UniProtKB",
        "DB_Object_ID": "A0A024RBG1",
        "DB_Object_Symbol": "NUDT4B",
        "Qualifier": "enables",
        "GO_ID": "GO:0003723",  # molecular_function: RNA binding
        "DB_Reference": "GO_REF:0000043",
        "Evidence_Code": "IEA",
        "With_or_From": "UniProtKB-KW:KW-0694",
        "Aspect": "F",
        "DB_Object_Name": "Diphosphoinositol polyphosphate phosphohydrolase",
        "DB_Object_Synonym": "NUDT4B",
        "DB_Object_Type": "protein",
        "Taxon": "taxon:9606",
        "Date": "20211010",
        "Assigned_By": "UniProt",
        "Annotation_Extension": "",
        "Gene_Product_Form_ID": ""
    }


@pytest.fixture
def basic_goa(mock_koza, source_name, basic_row, script):
    """
    Mock Koza run for GO annotation ingest.
    :param mock_koza:
    :param source_name:
    :param basic_row:
    :param script:
    :return:
    """
    return mock_koza(
        name=source_name,
        data=iter([basic_row]),
        transform_code=script
    )


def test_gene(basic_goa):
    
    gene = basic_goa[0]
    
    assert gene
    assert gene.id == "UniProtKB:A0A024RBG1"

    # 'category' is multivalued (an array)
    assert "biolink:Gene" in gene.category
    #
    # Pydantic or equivalent bug: doesn't emit this intermediary category... yet?
    # assert "biolink:BiologicalEntity" in gene.category

    assert "biolink:NamedThing" in gene.category

    # 'in_taxon' is multivalued (an array)
    assert "NCBITaxon:10090" in gene.in_taxon

    assert gene.source == "infores:entrez"


def test_go_term(basic_goa):
    
    go_term = basic_goa[1]
    
    assert go_term
    assert go_term.id == "GO:0003723"

    # 'category' should be multivalued (an array)
    # TODO: are all the intermediate concrete classes here between NamedThing and MolecularActivity?
    # TODO: Are the mixins 'biolink:Occurrent' and 'biolink:OntologyClass' also here?
    # TODO: Should 'biolink:GeneOntologyClass' be lurking somewhere in here too?
    assert "biolink:MolecularActivity" in go_term.category
    assert "biolink:BiologicalProcessOrActivity" in go_term.category
    assert "biolink:BiologicalEntity" in go_term.category
    assert "biolink:NamedThing" in go_term.category

    assert go_term.source == "infores:go"


def test_association(basic_goa):
    association = basic_goa[2]
    assert association
    assert association.subject == "NCBIGene:14679"
    assert association.object == "NCBIGene:56480"
    assert association.predicate == "biolink:related_to"
    assert association.relation == "skos:relatedMatch"

    assert "infores:goa" in association.source
