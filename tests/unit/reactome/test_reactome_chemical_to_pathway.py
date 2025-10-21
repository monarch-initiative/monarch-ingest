import pytest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../../src'))
from monarch_ingest.ingests.reactome.chemical_to_pathway import transform_record


@pytest.fixture
def basic_row():
    return {"component": "10033", "pathway_id": "R-RNO-6806664", "go_ecode": "IEA", "species_nam": "Rattus norvegicus"}


@pytest.fixture
def basic_g2p(basic_row):
    return transform_record(None, basic_row)


def test_association(basic_g2p):
    assert len(basic_g2p) == 1
    association = basic_g2p[0]
    assert association
    assert association.subject == "CHEBI:10033"
    assert association.predicate == "biolink:participates_in"
    assert association.object == "Reactome:R-RNO-6806664"
    assert "ECO:0000501" in association.has_evidence
    assert association.primary_knowledge_source == "infores:reactome"
    assert "infores:monarchinitiative" in association.aggregator_knowledge_source
