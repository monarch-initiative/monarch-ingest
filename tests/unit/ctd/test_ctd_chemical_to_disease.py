import pytest

from biolink_model_pydantic.model import ChemicalToDiseaseOrPhenotypicFeatureAssociation


@pytest.fixture
def source_name():
    return "ctd_chemical_to_disease"


@pytest.fixture
def script():
    return "./monarch_ingest/ingests/ctd/chemical_to_disease.py"


@pytest.fixture
def no_direct_evidence(mock_koza, source_name, script, global_table):
    row = {
        'ChemicalName': '10074-G5',
        'ChemicalID': 'C534883',
        'CasRN': '',
        'DiseaseName': 'Adenocarcinoma',
        'DiseaseID': 'MESH:D000230',
        'DirectEvidence': '',
        'InferenceGeneSymbol': 'MYC',
        'InferenceScore': '4.08',
        'OmimIDs': '',
        'PubMedIDs': '26432044',
    }
    return mock_koza(
        name=source_name,
        data=iter([row]),
        transform_code=script,
        global_table=global_table,
    )


@pytest.fixture
def marker_mechanism(mock_koza, source_name, script, global_table):
    row = {
        'ChemicalName': '10,10-bis(4-pyridinylmethyl)-9(10H)-anthracenone',
        'ChemicalID': 'C112297',
        'CasRN': '',
        'DiseaseName': 'Hyperkinesis',
        'DiseaseID': 'MESH:D006948',
        'DirectEvidence': 'marker/mechanism',
        'InferenceGeneSymbol': '',
        'InferenceScore': '',
        'OmimIDs': '',
        'PubMedIDs': '19098162',
    }
    return mock_koza(
        name=source_name,
        data=iter([row]),
        transform_code=script,
        global_table=global_table,
    )


@pytest.fixture
def therapeutic(mock_koza, source_name, script, global_table):
    row = {
        'ChemicalName': '10,11-dihydro-10-hydroxycarbamazepine',
        'ChemicalID': 'C039775',
        'CasRN': '',
        'DiseaseName': 'Epilepsy',
        'DiseaseID': 'MESH:D004827',
        'DirectEvidence': 'therapeutic',
        'InferenceGeneSymbol': '',
        'InferenceScore': '',
        'OmimIDs': '',
        'PubMedIDs': '17516704|123',
    }
    return mock_koza(
        name=source_name,
        data=iter([row]),
        transform_code=script,
        global_table=global_table,
    )


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
    association = [
        e
        for e in entities
        if isinstance(e, ChemicalToDiseaseOrPhenotypicFeatureAssociation)
    ][0]
    assert association
    assert association.predicate == "biolink:treats"
    assert 'PMID:17516704' in association.publications
    assert 'PMID:123' in association.publications
    assert association.primary_knowledge_source == "infores:ctd"
    assert "infores:monarchinitiative" in association.aggregator_knowledge_source

