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
def map_cache():
    """
    :return: Multi-level mock map_cache Uniprot to Entrez GeneID dictionary (realistic looking but synthetic data)
    """
    uniprot_2_gene = {
        "A0A024RBG1": {"Entrez": "440672"},
        "A0A024RBG2": {"Entrez": "440673"},
        "A0A024RBG3": {"Entrez": "440674"}
    }
    return {"uniprot_2_gene": uniprot_2_gene}


@pytest.fixture(scope="package")
def local_table():
    """
    :return: string path to Evidence Code to ECO term mappings file
    """
    return "monarch_ingest/goa/gaf-eco-mapping.yaml"


@pytest.fixture
def test_rows():
    """
    :return: List of test GO Annotation data rows (realistic looking but synthetic data).
    """
    return [
        {
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
        },
        {
            "DB": "UniProtKB",
            "DB_Object_ID": "A0A024RBG2",
            "DB_Object_Symbol": "NUDT4B",
            "Qualifier": "enables",
            "GO_ID": "GO:0008150",  # biological_process
            "DB_Reference": "GO_REF:0008150",
            "Evidence_Code": "ND",
            "With_or_From": "UniProtKB-KW:KW-0694",
            "Aspect": "P",
            "DB_Object_Name": "Diphosphoinositol polyphosphate phosphohydrolase",
            "DB_Object_Synonym": "NUDT4B",
            "DB_Object_Type": "protein",
            "Taxon": "taxon:4932",
            "Date": "20211010",
            "Assigned_By": "UniProt",
            "Annotation_Extension": "",
            "Gene_Product_Form_ID": ""
        },
        {
            "DB": "UniProtKB",
            "DB_Object_ID": "A0A024RBG3",
            "DB_Object_Symbol": "NUDT4B",
            "Qualifier": "enables",
            "GO_ID": "GO:0005575",  # cellular compartment
            "DB_Reference": "GO_REF:0005575",
            "Evidence_Code": "ND",
            "With_or_From": "UniProtKB-KW:KW-0694",
            "Aspect": "C",
            "DB_Object_Name": "Diphosphoinositol polyphosphate phosphohydrolase",
            "DB_Object_Synonym": "NUDT4B",
            "DB_Object_Type": "protein",
            "Taxon": "taxon:4932",
            "Date": "20211010",
            "Assigned_By": "UniProt",
            "Annotation_Extension": "",
            "Gene_Product_Form_ID": ""
        }
    ]


@pytest.fixture
def basic_goa(mock_koza, source_name, test_rows, script, global_table, local_table, map_cache):
    """
    Mock Koza run for GO annotation ingest.

    :param mock_koza:
    :param source_name:
    :param test_rows:
    :param script:
    :param global_table:
    :param local_table:
    :param map_cache:
    
    :return: mock_koza application
    """
    return mock_koza(
        name=source_name,
        data=iter(test_rows),
        transform_code=script,
        global_table=global_table,
        local_table=local_table,
        map_cache=map_cache
    )


result_expected = {
    "NCBIGene:440672": [
        "biolink:Gene",
        "NCBITaxon:9606",
        "GO:0003723",
        "biolink:MolecularActivity",
        "biolink:BiologicalProcessOrActivity",
        "biolink:enables",
        "RO:0002327"
    ],
    "NCBIGene:440673": [
        "biolink:Gene",
        "NCBITaxon:4932",
        "GO:0008150",
        "biolink:BiologicalProcess",
        "biolink:BiologicalProcessOrActivity",
        "biolink:actively_involved_in",
        "RO:0002331"
    ],
    "NCBIGene:440674": [
        "biolink:Gene",
        "NCBITaxon:4932",
        "GO:0005575",
        "biolink:CellularComponent",
        "biolink:AnatomicalEntity",
        "biolink:active_in",
        "RO:0002432"
    ]
}


def test_nodes(basic_goa):
    
    gene = basic_goa[0]
    go_term = basic_goa[1]
    
    assert gene
    assert gene.id in result_expected.keys()

    # 'category' is multivalued (an array)
    assert result_expected[gene.id][0] in gene.category
    # Pydantic or equivalent bug: doesn't emit this intermediary category... yet?
    # assert "biolink:BiologicalEntity" in gene.category
    assert "biolink:NamedThing" in gene.category
    
    # 'in_taxon' is multivalued (an array)
    assert result_expected[gene.id][1] in gene.in_taxon

    assert "infores:uniprot" in gene.source
    
    assert go_term
    assert go_term.id == result_expected[gene.id][2]
    
    # 'category' should be multivalued (an array)
    # TODO: some of the intermediate concrete classes here in between
    #       NamedThing and MolecularActivity appear to be missing?
    assert result_expected[gene.id][3] in go_term.category
    assert result_expected[gene.id][4] in go_term.category
    # This ancestral category appears to be missing? Pydantic model error?
    # assert "biolink:BiologicalEntity" in go_term.category
    assert "biolink:NamedThing" in go_term.category

    assert "infores:go" in go_term.source


def test_association(basic_goa):
    association = basic_goa[2]
    assert association
    assert association.subject in result_expected.keys()
    
    assert association.object == result_expected[association.subject][2]
    assert association.predicate == result_expected[association.subject][5]
    assert association.relation == result_expected[association.subject][6]

    assert "infores:goa" in association.source
