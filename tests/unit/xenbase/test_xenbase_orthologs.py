"""
Unit tests for Xenbase Gene Orthology relationships ingest
"""
import pytest


@pytest.fixture
def source_name():
    """
    :return: string source name of Xenbase Gene Orthology relationships ingest
    """
    return "xenbase_ref_genome_orthologs"


@pytest.fixture
def script():
    """
    :return: string path to Xenbase Gene Orthology relationships ingest script
    """
    return "./monarch_ingest/ingests/xenbase/orthologs.py"


# The results expected is only distinguished by the above
# distinct Ortholog gene ID's, hence, indexed in that manner
result_expected = {
    # Test complete Xenbase records
    # (defective records do not get passed through to the result_expected)
    #
    # "RGD:1564893": [
    #     "HGNC:11477",
    #     "NCBITaxon:9606",
    #     "NCBITaxon:10116",
    #     "biolink:orthologous_to",
    #     "RO:HOM0000017",
    #     "PANTHER.FAMILY:PTHR12434",
    # ],
}


@pytest.fixture
def well_behaved_record(mock_koza, source_name, script, global_table):
    row = {
        #  - "SUBJECT"
        #  - "SUBJECT_LABEL"
        #  - "SUBJECT_TAXON"
        #  - "SUBJECT_TAXON_LABEL"
        #  - "OBJECT"
        #  - "OBJECT_LABEL"
        #  - "RELATION"
        #  - "RELATION_LABEL"
        #  - "EVIDENCE"
        #  - "EVIDENCE_LABEL"
        #  - "SOURCE"
        #  - "IS_DEFINED_BY"
        #  - "QUALIFIER"
    }
    return mock_koza(
        name=source_name,
        data=iter([row]),
        transform_code=script,
        global_table=global_table,
    )


def test_well_behaved_record_1(well_behaved_record):

    association = well_behaved_record[0]

    assert association
    assert association.object in result_expected.keys()

    # The test data mostly has the same human 'gene' subject
    # but is distinguished by the 'object' orthology gene id
    # hence the result_expected dictionary is now indexed thus...
    assert association.subject == result_expected[association.object][0]
    assert association.predicate == result_expected[association.object][3]

    # Evidence is a list
    assert result_expected[association.object][5] in association.has_evidence

    assert association.primary_knowledge_source == "infores:xenbase"
    assert "infores:monarchinitiative" in association.aggregator_knowledge_source
