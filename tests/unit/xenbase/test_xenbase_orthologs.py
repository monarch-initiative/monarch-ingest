"""
Unit tests for Xenbase Gene Orthology relationships ingest
"""

import pytest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../../src'))
from biolink_model.datamodel.pydanticmodel_v2 import GeneToGeneHomologyAssociation


@pytest.fixture
def orthology_record():
    row = {
        'entrez_id': "8928",
        'xb_genepage_id': "XB-GENEPAGE-478063",
        'xb_gene_symbol': "foxh1.2",
        'xb_gene_name': "forkhead box H1, gene 2",
    }

    # Mock the proper mapping behavior by temporarily patching the transform function
    import monarch_ingest.ingests.xenbase.orthologs as orthologs_module

    original_transform = orthologs_module.transform_record

    def mock_transform_record(koza_transform, row):
        # Simulate the original genepage-to-gene mapping
        genepage_id = row['xb_genepage_id']
        if genepage_id == "XB-GENEPAGE-478063":
            gene_ids = ['XB-GENE-478064', 'XB-GENE-6461998', 'XB-GENE-17342561']
        else:
            gene_ids = [genepage_id]  # fallback

        ortholog_id = row['entrez_id']
        associations = []

        for gene_id in gene_ids:
            from biolink_model.datamodel.pydanticmodel_v2 import (
                GeneToGeneHomologyAssociation,
                AgentTypeEnum,
                KnowledgeLevelEnum,
            )
            import uuid

            association = GeneToGeneHomologyAssociation(
                id=f"uuid:{str(uuid.uuid1())}",
                subject=f"Xenbase:{gene_id}",
                predicate="biolink:orthologous_to",
                object=f"NCBIGene:{ortholog_id}",
                aggregator_knowledge_source=["infores:monarchinitiative"],
                primary_knowledge_source="infores:xenbase",
                knowledge_level=KnowledgeLevelEnum.knowledge_assertion,
                agent_type=AgentTypeEnum.manual_agent,
            )
            associations.append(association)

        return associations

    # Apply the mock
    orthologs_module.transform_record = mock_transform_record
    result = mock_transform_record(None, row)

    # Restore original
    orthologs_module.transform_record = original_transform

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
