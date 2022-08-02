"""
Unit tests for Xenbase Gene Orthology relationships ingest
"""
import pytest
from biolink.pydanticmodel import GeneToGeneHomologyAssociation


@pytest.fixture
def source_name():
    """
    :return: string source name of Xenbase Gene Orthology relationships ingest
    """
    return "xenbase_orthologs"


@pytest.fixture
def script():
    """
    :return: string path to Xenbase Gene Orthology relationships ingest script
    """
    return "./monarch_ingest/ingests/xenbase/orthologs.py"


@pytest.fixture
def orthology_record(mock_koza, source_name, script, global_table):
    row = {
        'entrez_id': "8928",
        'xb_genepage_id': "XB-GENEPAGE-478063",
        'xb_gene_symbol': "foxh1.2",
        'xb_gene_name': "forkhead box H1, gene 2"
    }
    return mock_koza(
        name=source_name,
        data=iter([row]),
        transform_code=script,
        global_table=global_table,
    )


def test_orthology_record(orthology_record):
    assert orthology_record
    association = [
        association
        for association in orthology_record
        if isinstance(association, GeneToGeneHomologyAssociation)
    ][0]
    assert association.subject == "Xenbase:XB-GENEPAGE-478063"
    assert association.predicate == "biolink:orthologous_to"
    assert association.object == "NCBIGene:8928"

    assert association.primary_knowledge_source == "infores:xenbase"
    assert "infores:monarchinitiative" in association.aggregator_knowledge_source
