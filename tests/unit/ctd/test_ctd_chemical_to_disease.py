import pytest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../../src'))
from monarch_ingest.ingests.ctd.chemical_to_disease import transform_record
from monarch_ingest.constants import BIOLINK_TREATS_OR_APPLIED_OR_STUDIED_TO_TREAT


@pytest.fixture
def no_direct_evidence_row():
    return {
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


@pytest.fixture
def marker_mechanism_row():
    return {
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


@pytest.fixture
def therapeutic_row():
    return {
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


def test_no_direct_evidence(no_direct_evidence_row):
    entities = transform_record(None, no_direct_evidence_row)
    assert len(entities) == 0


def test_marker_mechanism_entities(marker_mechanism_row):
    entities = transform_record(None, marker_mechanism_row)
    assert len(entities) == 0


def test_therapeutic_entities(therapeutic_row):
    entities = transform_record(None, therapeutic_row)
    assert entities
    assert len(entities) == 1
    association = entities[0]
    assert association
    assert association.predicate == BIOLINK_TREATS_OR_APPLIED_OR_STUDIED_TO_TREAT
    assert "PMID:17516704" in association.publications
    assert "PMID:123" in association.publications
    assert association.primary_knowledge_source == "infores:ctd"
    assert "infores:monarchinitiative" in association.aggregator_knowledge_source
