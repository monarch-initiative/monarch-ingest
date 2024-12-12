"""
Unit tests for Xenbase Gene Orthology relationships ingest
"""

import pytest
from biolink_model.datamodel.pydanticmodel_v2 import GeneToGeneHomologyAssociation
from koza.utils.testing_utils import mock_koza  # noqa: F401


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
    return "./src/monarch_ingest/ingests/xenbase/orthologs.py"


@pytest.fixture
def map_cache():
    return { 
        'genepage-2-gene': {
            'XB-GENEPAGE-478063': { 
                'tropicalis_id':'XB-GENE-478064',
                'laevis_l_id': 'XB-GENE-6461998',
                'laevis_s_id': 'XB-GENE-17342561',
            }
        }
    }

@pytest.fixture
def orthology_record(mock_koza, source_name, script, global_table, map_cache):
    row = {
        'entrez_id': "8928",
        'xb_genepage_id': "XB-GENEPAGE-478063",
        'xb_gene_symbol': "foxh1.2",
        'xb_gene_name': "forkhead box H1, gene 2",
    }
    return mock_koza(
        name=source_name,
        data=row,
        transform_code=script,
        map_cache=map_cache,
        global_table=global_table,
    )

@pytest.mark.parametrize("index, expected_subject", 
                         [(0, "Xenbase:XB-GENE-478064"), 
                          (1, "Xenbase:XB-GENE-6461998"),
                          (2, "Xenbase:XB-GENE-17342561")])
def test_orthology_records(orthology_record, index: int, expected_subject: str):
    assert orthology_record
    association = [
        association for association in orthology_record if isinstance(association, GeneToGeneHomologyAssociation)
    ][index]
    assert association.subject == expected_subject
    assert association.predicate == "biolink:orthologous_to"
    assert association.object == "NCBIGene:8928"

    assert association.primary_knowledge_source == "infores:xenbase"
    assert "infores:monarchinitiative" in association.aggregator_knowledge_source
