import pytest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../../src'))
from monarch_ingest.ingests.reactome.gene_to_pathway import transform_record


@pytest.fixture
def basic_row():
    return {
        "component": "8627890",
        "pathway_id": "R-DDI-73762",
        "go_ecode": "IEA",
        "species_nam": "Dictyostelium discoideum",
    }


@pytest.fixture
def basic_g2p(basic_row):
    return transform_record(None, basic_row)


def test_association(basic_g2p):
    assert len(basic_g2p) == 1
    association = basic_g2p[0]
    assert association
    assert association.subject == "NCBIGene:8627890"
    assert association.predicate == "biolink:participates_in"
    assert association.object == "Reactome:R-DDI-73762"
    assert "ECO:0000501" in association.has_evidence
    assert association.primary_knowledge_source == "infores:reactome"
    assert "infores:monarchinitiative" in association.aggregator_knowledge_source
