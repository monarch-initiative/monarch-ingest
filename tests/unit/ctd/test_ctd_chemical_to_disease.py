import pytest
from biolink_model.datamodel.pydanticmodel_v2 import ChemicalToDiseaseOrPhenotypicFeatureAssociation
from koza.io.writer.writer import KozaWriter
from koza.runner import KozaRunner, KozaTransformHooks
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../../src'))
from monarch_ingest.ingests.ctd.chemical_to_disease import transform_record
from monarch_ingest.constants import BIOLINK_TREATS_OR_APPLIED_OR_STUDIED_TO_TREAT


class MockWriter(KozaWriter):
    def __init__(self):
        self.items = []

    def write(self, entities):
        self.items += entities

    def finalize(self):
        pass


@pytest.fixture
def no_direct_evidence():
    row = {
        "ChemicalName": "10074-G5",
        "ChemicalID": "C534883",
        "CasRN": "",
        "DiseaseName": "Adenocarcinoma",
        "DiseaseID": "MESH:D000230",
        "DirectEvidence": "",
        "InferenceGeneSymbol": "MYC",
        "InferenceScore": "4.08",
        "OmimIDs": "",
        "PubMedIDs": "26432044",
    }

    writer = MockWriter()
    runner = KozaRunner(data=iter([row]), writer=writer, hooks=KozaTransformHooks(transform_record=[transform_record]))
    runner.run()
    return writer.items


@pytest.fixture
def marker_mechanism():
    row = {
        "ChemicalName": "10,10-bis(4-pyridinylmethyl)-9(10H)-anthracenone",
        "ChemicalID": "C112297",
        "CasRN": "",
        "DiseaseName": "Hyperkinesis",
        "DiseaseID": "MESH:D006948",
        "DirectEvidence": "marker/mechanism",
        "InferenceGeneSymbol": "",
        "InferenceScore": "",
        "OmimIDs": "",
        "PubMedIDs": "19098162",
    }

    writer = MockWriter()
    runner = KozaRunner(data=iter([row]), writer=writer, hooks=KozaTransformHooks(transform_record=[transform_record]))
    runner.run()
    return writer.items


@pytest.fixture
def therapeutic():
    row = {
        "ChemicalName": "10,11-dihydro-10-hydroxycarbamazepine",
        "ChemicalID": "C039775",
        "CasRN": "",
        "DiseaseName": "Epilepsy",
        "DiseaseID": "MESH:D004827",
        "DirectEvidence": "therapeutic",
        "InferenceGeneSymbol": "",
        "InferenceScore": "",
        "OmimIDs": "",
        "PubMedIDs": "17516704|123",
    }

    writer = MockWriter()
    runner = KozaRunner(data=iter([row]), writer=writer, hooks=KozaTransformHooks(transform_record=[transform_record]))
    runner.run()
    return writer.items


def test_no_direct_evidence(no_direct_evidence):
    entities = no_direct_evidence
    assert len(entities) == 0


def test_marker_mechanism_entities(marker_mechanism):
    entities = marker_mechanism
    assert len(entities) == 0


def test_therapeutic_entities(therapeutic):
    entities = therapeutic
    assert entities
    assert len(entities) == 1
    association = [e for e in entities if isinstance(e, ChemicalToDiseaseOrPhenotypicFeatureAssociation)][0]
    assert association
    assert association.predicate == BIOLINK_TREATS_OR_APPLIED_OR_STUDIED_TO_TREAT
    assert "PMID:17516704" in association.publications
    assert "PMID:123" in association.publications
    assert association.primary_knowledge_source == "infores:ctd"
    assert "infores:monarchinitiative" in association.aggregator_knowledge_source
