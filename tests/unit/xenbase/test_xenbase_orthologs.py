"""
Unit tests for Xenbase Gene Orthology relationships ingest
"""

import pytest
from biolink_model.datamodel.pydanticmodel_v2 import GeneToGeneHomologyAssociation
from koza import KozaTransform
from koza.io.writer.passthrough_writer import PassthroughWriter

from monarch_ingest.ingests.xenbase.orthologs import transform_record


@pytest.fixture
def genepage_to_gene_mapping():
    """Mock genepage-to-gene mapping for testing"""
    return {
        "XB-GENEPAGE-478063": {
            "gene_page_id": "XB-GENEPAGE-478063",
            "tropicalis_id": "XB-GENE-478064",
            "laevis_l_id": "XB-GENE-6461998",
            "laevis_s_id": "XB-GENE-17342561"
        }
    }


@pytest.fixture
def orthology_record(genepage_to_gene_mapping):
    """Test the real transform_record function with KozaTransform"""
    row = {
        'entrez_id': "8928",
        'xb_genepage_id': "XB-GENEPAGE-478063",
        'xb_gene_symbol': "foxh1.2",
        'xb_gene_name': "forkhead box H1, gene 2",
    }

    koza_transform = KozaTransform(
        mappings={"genepage-2-gene": genepage_to_gene_mapping},
        writer=PassthroughWriter(),
        extra_fields={}
    )
    result = transform_record(koza_transform, row)

    return result


@pytest.mark.parametrize(
    "index, expected_subject",
    [(0, "Xenbase:XB-GENE-478064"), (1, "Xenbase:XB-GENE-6461998"), (2, "Xenbase:XB-GENE-17342561")],
)
def test_orthology_records(orthology_record, index: int, expected_subject: str):
    """Test that orthology records are created for each gene mapping"""
    assert orthology_record
    assert len(orthology_record) == 3  # Should have 3 associations

    association = [
        association for association in orthology_record if isinstance(association, GeneToGeneHomologyAssociation)
    ][index]

    assert association.subject == expected_subject
    assert association.predicate == "biolink:orthologous_to"
    assert association.object == "NCBIGene:8928"

    assert association.primary_knowledge_source == "infores:xenbase"
    assert "infores:monarchinitiative" in association.aggregator_knowledge_source
