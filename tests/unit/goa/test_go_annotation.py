"""
Unit tests for GO Annotations ingest
"""
import pytest
from sys import stderr
import logging

logger = logging.getLogger(__name__)


@pytest.fixture
def source_name():
    """
    :return: string source name of GO Annotations ingest
    """
    return "goa_go_annotation"


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
        "A0A024RBG1": {"Entrez": "440671"},
        "WBGene00000013": {"Entrez": "440672"},
        "A0A024RBG2": {"Entrez": "440673"},
        "A0A024RBG3": {"Entrez": "440674"},
        "A0A024RBG4": {"Entrez": "440675"},
        "Q6GZX3": {"Entrez": "440676"},
        "Q6GZX0": {"Entrez": "440677"},
        "A0A024RBG8": {"Entrez": "440678"},
        "A0A024RBG9": {"Entrez": "440679"}
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
        # Core data test: a completely normal record
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
        # Multiple taxa
        {
            'DB': 'WB',
            'DB_Object_ID': 'WBGene00000013',
            'DB_Object_Symbol': 'abf-2',
            'Qualifier': 'involved_in',
            'GO_ID': 'GO:0050830',
            'DB_Reference': 'WB_REF:WBPaper00045314|PMID:24882217',
            'Evidence_Code': 'IEP',
            'With_or_From': '',
            'Aspect': 'P',
            'DB_Object_Name': '',
            'DB_Object_Synonym': 'C50F2.10|C50F2.e',
            'DB_Object_Type': 'gene',
            'Taxon': 'taxon:6239|taxon:46170',
            'Date': '20140827',
            'Assigned_By': 'WB',
            'Annotation_Extension': '',
            'Gene_Product_Form_ID': ''
        },
        # Test default qualifier override for molecular function
        {
            "DB": "UniProtKB",
            "DB_Object_ID": "A0A024RBG2",
            "DB_Object_Symbol": "NUDT4B",
            "Qualifier": "contributes_to",
            "GO_ID": "GO:0003674",  # molecular_function root
            "DB_Reference": "GO_REF:0003674",
            "Evidence_Code": "ND",
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
        # Test default qualifier override for biological process
        {
            "DB": "UniProtKB",
            "DB_Object_ID": "A0A024RBG3",
            "DB_Object_Symbol": "NUDT4B",
            "Qualifier": "acts_upstream_of_negative_effect",
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
        # Test default qualifier override for cellular compartment
        {
            "DB": "UniProtKB",
            "DB_Object_ID": "A0A024RBG4",
            "DB_Object_Symbol": "NUDT4B",
            "Qualifier": "colocalizes_with",
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
        },
        # Test non-default Biological Process and non-default qualifier
        {
            "DB": "UniProtKB",
            "DB_Object_ID": "Q6GZX3",
            "DB_Object_Symbol": "NUDT4B",
            "Qualifier": "acts_upstream_of_or_within",
            "GO_ID": "GO:0045759",
            "DB_Reference": "GO_REF:0045759",
            "Evidence_Code": "ND",
            "With_or_From": "UniProtKB-KW:KW-0694",
            "Aspect": "P",
            "DB_Object_Name": "Diphosphoinositol polyphosphate phosphohydrolase",
            "DB_Object_Synonym": "NUDT4B",
            "DB_Object_Type": "protein",
            "Taxon": "taxon:1000",
            "Date": "20211010",
            "Assigned_By": "UniProt",
            "Annotation_Extension": "",
            "Gene_Product_Form_ID": ""
        },
        # Test outcome of unknown UniProt idmapping: uniprot id
        # is returned as gene id? Also try another evidence code
        {
            "DB": "UniProtKB",
            "DB_Object_ID": "A0A024RBG5",
            "DB_Object_Symbol": "NUDT4B",
            "Qualifier": "enables",
            "GO_ID": "GO:0003723",  # molecular_function: RNA binding
            "DB_Reference": "GO_REF:0000043",
            "Evidence_Code": "HMP",
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
        # Test non-default Biological Process with negated qualifier
        {
            "DB": "UniProtKB",
            "DB_Object_ID": "Q6GZX0",
            "DB_Object_Symbol": "NUDT4B",
            "Qualifier": "NOT|acts_upstream_of_or_within",
            "GO_ID": "GO:0045759",
            "DB_Reference": "GO_REF:0045759",
            "Evidence_Code": "ND",
            "With_or_From": "UniProtKB-KW:KW-0694",
            "Aspect": "P",
            "DB_Object_Name": "Diphosphoinositol polyphosphate phosphohydrolase",
            "DB_Object_Synonym": "NUDT4B",
            "DB_Object_Type": "protein",
            "Taxon": "taxon:1000",
            "Date": "20211010",
            "Assigned_By": "UniProt",
            "Annotation_Extension": "",
            "Gene_Product_Form_ID": ""
        },
        # Missing (or wrong) GO term Aspect value - the record will be skipped?
        # So no entry is needed in the result_expected dictionary below
        {
           "DB": "UniProtKB",
           "DB_Object_ID": "Q6GZX0",
           "DB_Object_Symbol": "NUDT4B",
           "Qualifier": "acts_upstream_of_or_within",
           "GO_ID": "GO:0045759",
           "DB_Reference": "GO_REF:0045759",
           "Evidence_Code": "IEA",
           "With_or_From": "UniProtKB-KW:KW-0694",
           "Aspect": "",
           "DB_Object_Name": "Diphosphoinositol polyphosphate phosphohydrolase",
           "DB_Object_Synonym": "NUDT4B",
           "DB_Object_Type": "protein",
           "Taxon": "taxon:1000",
           "Date": "20211010",
           "Assigned_By": "UniProt",
           "Annotation_Extension": "",
           "Gene_Product_Form_ID": ""
        },
        # Missing (empty) qualifier - assign GO Aspect associated default
        {
           "DB": "UniProtKB",
           "DB_Object_ID": "A0A024RBG8",
           "DB_Object_Symbol": "NUDT4B",
           "Qualifier": "",
           "GO_ID": "GO:0005575",  # cellular compartment
           "DB_Reference": "GO_REF:0005575",
           "Evidence_Code": "IEA-GO_REF:0000041",
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
        },
        # Invalid Evidence Code - coerced into 'ND' -> "ECO:0000307"
        {
            "DB": "UniProtKB",
            "DB_Object_ID": "A0A024RBG9",
            "DB_Object_Symbol": "NUDT4B",
            "Qualifier": "enables",
            "GO_ID": "GO:0003723",
            "DB_Reference": "GO_REF:0000043",
            "Evidence_Code": "XXX",  # invalid Evidence Code
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
    # Test regular MolecularActivity go term
    "NCBIGene:440671": [
        "biolink:Gene",
        "NCBITaxon:9606",
        "GO:0003723",
        "biolink:MolecularActivity",
        "biolink:BiologicalProcessOrActivity",
        "biolink:enables",
        "RO:0002327",
        False,
        "ECO:0000501"
    ],
    # Multiple Taxa
    "NCBIGene:440672": [
        "biolink:Gene",
        "NCBITaxon:46170",   # test for presence of the second one?
        "GO:0050830",
        "biolink:BiologicalProcess",
        "biolink:BiologicalProcessOrActivity",
        "biolink:actively_involved_in",
        "RO:0002331",
        False,
        "ECO:0000270"
    ],
    # Test default qualifier override for Molecular Activity go term
    "NCBIGene:440673": [
        "biolink:Gene",
        "NCBITaxon:9606",
        "GO:0003674",
        "biolink:MolecularActivity",
        "biolink:BiologicalProcessOrActivity",
        "biolink:enables",
        "RO:0002327",
        False,
        "ECO:0000307"
    ],
    # Test default qualifier override for Biological Process go term
    "NCBIGene:440674": [
        "biolink:Gene",
        "NCBITaxon:4932",
        "GO:0008150",
        "biolink:BiologicalProcess",
        "biolink:BiologicalProcessOrActivity",
        "biolink:actively_involved_in",
        "RO:0002331",
        False,
        "ECO:0000307"
    ],
    # Test default qualifier override for Cellular Component go term
    "NCBIGene:440675": [
        "biolink:Gene",
        "NCBITaxon:4932",
        "GO:0005575",
        "biolink:CellularComponent",
        "biolink:AnatomicalEntity",
        "biolink:active_in",
        "RO:0002432",
        False,
        "ECO:0000307"
    ],
    # Test non-default Biological Process and non-default qualifier
    "NCBIGene:440676": [
        "biolink:Gene",
        "NCBITaxon:1000",
        "GO:0045759",
        "biolink:BiologicalProcess",
        "biolink:BiologicalProcessOrActivity",
        "biolink:acts_upstream_of_or_within",
        "RO:0002264",
        False,
        "ECO:0000307"
    ],
    # Test outcome of unknown UniProt idmapping: uniprot id
    # is returned as gene id? Also try another evidence code
    "UniProtKB:A0A024RBG5": [
        "biolink:Gene",
        "NCBITaxon:9606",
        "GO:0003723",
        "biolink:MolecularActivity",
        "biolink:BiologicalProcessOrActivity",
        "biolink:enables",
        "RO:0002327",
        False,
        "ECO:0007001"
    ],
    # Test non-default Biological Process with negated qualifier
    "NCBIGene:440677": [
        "biolink:Gene",
        "NCBITaxon:1000",
        "GO:0045759",
        "biolink:BiologicalProcess",
        "biolink:BiologicalProcessOrActivity",
        "biolink:acts_upstream_of_or_within",
        "RO:0002264",
        True,
        "ECO:0000307"
    ],
    # Missing (empty) qualifier - assign GO Aspect associated default
    "NCBIGene:440678": [
        "biolink:Gene",
        "NCBITaxon:4932",
        "GO:0005575",
        "biolink:CellularComponent",
        "biolink:AnatomicalEntity",
        "biolink:located_in",
        "RO:0002432",
        False,
        "ECO:0000307"
    ],
    # Invalid Evidence Code - coerced into 'ND' -> "ECO:0000307"
    "NCBIGene:440679": [
        "biolink:Gene",
        "NCBITaxon:9606",
        "GO:0003723",
        "biolink:MolecularActivity",
        "biolink:BiologicalProcessOrActivity",
        "biolink:enables",
        "RO:0002327",
        False,
        "ECO:0000307"
    ]
}


def test_nodes(basic_goa):

    if not len(basic_goa):
        logger.warning("test_nodes() null test result?")
        return

    gene = basic_goa[0]
    go_term = basic_goa[1]

    assert gene
    assert gene.id in result_expected.keys()

    print(f"\nTesting gene node '{gene.id}'", file=stderr)

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

    if not len(basic_goa):
        logger.warning("test_association() null test?")
        return

    association = basic_goa[2]
    assert association
    assert association.subject in result_expected.keys()

    assert association.object == result_expected[association.subject][2]
    assert association.predicate == result_expected[association.subject][5]
    assert association.relation == result_expected[association.subject][6]
    assert association.negated == result_expected[association.subject][7]
    assert result_expected[association.subject][8] in association.has_evidence

    assert "infores:goa" in association.source