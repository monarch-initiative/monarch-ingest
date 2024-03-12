"""
Unit tests for GO Annotations ingest
"""

from typing import Tuple

import pytest
from biolink_model.datamodel.pydanticmodel_v2 import Association
from loguru import logger

from monarch_ingest.ingests.go.annotation_utils import parse_identifiers


@pytest.mark.parametrize(
    "query",
    [
        (
            {
                "DB": "AspGD",
                "DB_Object_ID": "ASPL0000057967",
                "DB_Object_Symbol": "catB",
                "Qualifier": "acts_upstream_of_or_within",
                "GO_ID": "GO:0019521",  # D-gluconate metabolic process
                "DB_Reference": "AspGD_REF:ASPL0000080002|PMID:18405346",
                "Evidence_Code": "RCA",
                "With_or_From": "",
                "Aspect": "P",
                "DB_Object_Name": "",
                "DB_Object_Synonym": "AN9339|ANID_09339|ANIA_09339",
                "DB_Object_Type": "gene_product",
                "Taxon": "taxon:227321",
                "Date": "20090403",
                "Assigned_By": "AspGD",
                "Annotation_Extension": "",
                "Gene_Product_Form_ID": "",
            },
            "AspGD:AN9339",
            "NCBITaxon:227321",
        )
    ],
)
def test_parse_identifiers(query: Tuple):
    gene_id, ncbitaxa = parse_identifiers(query[0])
    assert gene_id == query[1]
    assert query[2] in ncbitaxa


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
    return "./src/monarch_ingest/ingests/go/annotation.py"


@pytest.fixture(scope="package")
def local_table():
    """
    :return: string path to Evidence Code to ECO term mappings file
    """
    return "src/monarch_ingest/ingests/go/gaf-eco-mapping.yaml"


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
            "Gene_Product_Form_ID": "",
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
            'Gene_Product_Form_ID': '',
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
            "Gene_Product_Form_ID": "",
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
            "Gene_Product_Form_ID": "",
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
            "Gene_Product_Form_ID": "",
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
            "Gene_Product_Form_ID": "",
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
            "Gene_Product_Form_ID": "",
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
            "Gene_Product_Form_ID": "",
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
            "Gene_Product_Form_ID": "",
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
            "Gene_Product_Form_ID": "",
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
            "Gene_Product_Form_ID": "",
        },
    ]


@pytest.fixture
def basic_go(mock_koza, source_name, test_rows, script, global_table, local_table):
    """
    Mock Koza run for GO annotation ingest.

    :param mock_koza:
    :param source_name:
    :param test_rows:
    :param script:
    :param global_table:
    :param local_table:

    :return: mock_koza application
    """
    return mock_koza(
        name=source_name,
        data=iter(test_rows),
        transform_code=script,
        global_table=global_table,
        local_table=local_table,
        map_cache=None,
    )


result_expected = {
    # Test regular MolecularActivity go term
    "UniProtKB:A0A024RBG1": [
        "biolink:Gene",
        "NCBITaxon:9606",
        "GO:0003723",
        "biolink:MolecularActivity",
        "biolink:BiologicalProcessOrActivity",
        "biolink:enables",
        "RO:0002327",
        False,
        "ECO:0000501",
    ],
    # Multiple Taxa
    "WB:WBGene00000013": [
        "biolink:Gene",
        "NCBITaxon:46170",  # test for presence of the second one?
        "GO:0050830",
        "biolink:BiologicalProcess",
        "biolink:BiologicalProcessOrActivity",
        "biolink:actively_involved_in",
        "RO:0002331",
        False,
        "ECO:0000270",
    ],
    # Test default qualifier override for Molecular Activity go term
    "UniProtKB:A0A024RBG2": [
        "biolink:Gene",
        "NCBITaxon:9606",
        "GO:0003674",
        "biolink:MolecularActivity",
        "biolink:BiologicalProcessOrActivity",
        "biolink:enables",
        "RO:0002327",
        False,
        "ECO:0000307",
    ],
    # Test default qualifier override for Biological Process go term
    "UniProtKB:A0A024RBG3": [
        "biolink:Gene",
        "NCBITaxon:4932",
        "GO:0008150",
        "biolink:BiologicalProcess",
        "biolink:BiologicalProcessOrActivity",
        "biolink:actively_involved_in",
        "RO:0002331",
        False,
        "ECO:0000307",
    ],
    # Test default qualifier override for Cellular Component go term
    "UniProtKB:A0A024RBG4": [
        "biolink:Gene",
        "NCBITaxon:4932",
        "GO:0005575",
        "biolink:CellularComponent",
        "biolink:AnatomicalEntity",
        "biolink:active_in",
        "RO:0002432",
        False,
        "ECO:0000307",
    ],
    # Test non-default Biological Process and non-default qualifier
    "UniProtKB:Q6GZX3": [
        "biolink:Gene",
        "NCBITaxon:1000",
        "GO:0045759",
        "biolink:BiologicalProcess",
        "biolink:BiologicalProcessOrActivity",
        "biolink:acts_upstream_of_or_within",
        "RO:0002264",
        False,
        "ECO:0000307",
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
        "ECO:0007001",
    ],
    # Test non-default Biological Process with negated qualifier
    "UniProtKB:Q6GZX0": [
        "biolink:Gene",
        "NCBITaxon:1000",
        "GO:0045759",
        "biolink:BiologicalProcess",
        "biolink:BiologicalProcessOrActivity",
        "biolink:acts_upstream_of_or_within",
        "RO:0002264",
        True,
        "ECO:0000307",
    ],
    # Missing (empty) qualifier - assign GO Aspect associated default
    "UniProtKB:A0A024RBG8": [
        "biolink:Gene",
        "NCBITaxon:4932",
        "GO:0005575",
        "biolink:CellularComponent",
        "biolink:AnatomicalEntity",
        "biolink:located_in",
        "RO:0002432",
        False,
        "ECO:0000307",
    ],
    # Invalid Evidence Code - coerced into 'ND' -> "ECO:0000307"
    "UniProtKB:A0A024RBG9": [
        "biolink:Gene",
        "NCBITaxon:9606",
        "GO:0003723",
        "biolink:MolecularActivity",
        "biolink:BiologicalProcessOrActivity",
        "biolink:enables",
        "RO:0002327",
        False,
        "ECO:0000307",
    ],
}


def test_association(basic_go):
    if not len(basic_go):
        logger.warning("test_association() null test?")
        return

    association = basic_go[2]
    assert association
    assert association.subject in result_expected.keys()

    assert association.object == result_expected[association.subject][2]
    assert association.predicate == result_expected[association.subject][5]
    assert association.negated == result_expected[association.subject][7]
    assert result_expected[association.subject][8] in association.has_evidence

    assert association.primary_knowledge_source == "infores:uniprot"
    assert "infores:monarchinitiative" in association.aggregator_knowledge_source


@pytest.fixture
def mgi_entities(mock_koza, source_name, script, global_table, local_table):
    row = {
        'DB': 'MGI',
        'DB_Object_ID': 'MGI:1918911',
        'DB_Object_Symbol': '0610005C13Rik',
        'Qualifier': 'enables',
        'GO_ID': 'GO:0003674',
        'DB_Reference': 'MGI:MGI:2156816|GO_REF:0000015',
        'Evidence_Code': 'ND',
        'With_or_From': '',
        'Aspect': 'F',
        'DB_Object_Name': 'RIKEN cDNA 0610005C13 gene',
        'DB_Object_Synonym': '',
        'DB_Object_Type': 'gene',
        'Taxon': 'taxon:10090',
        'Date': '20200917',
        'Assigned_By': 'MGI',
        'Annotation_Extension': '',
        'Gene_Product_Form_ID': '',
    }

    return mock_koza(
        name=source_name,
        data=iter([row]),
        transform_code=script,
        global_table=global_table,
        local_table=local_table,
        map_cache=None,
    )


def test_mgi_curie(mgi_entities):
    association = [association for association in mgi_entities if isinstance(association, Association)][0]
    assert association
    assert association.subject == "MGI:1918911"
    assert association.primary_knowledge_source == "infores:mgi"
    assert "infores:monarchinitiative" in association.aggregator_knowledge_source
