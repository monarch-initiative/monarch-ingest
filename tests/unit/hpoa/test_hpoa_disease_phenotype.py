import pytest
from biolink_model.datamodel.pydanticmodel_v2 import DiseaseToPhenotypicFeatureAssociation
from koza.utils.testing_utils import mock_koza  # noqa: F401


@pytest.fixture
def d2pf_entities_1(mock_koza, global_table):
    row = {
        "database_id": "OMIM:614856",
        "disease_name": "Osteogenesis imperfecta, type XIII",
        "qualifier": "NOT",
        "hpo_id": "HP:0000343",
        "reference": "OMIM:614856",
        "evidence": "TAS",
        "onset": "HP:0003593",
        "frequency": "1/1",
        "sex": "FEMALE",
        "modifier": "",
        "aspect": "C",  # assert 'Clinical' test record
        "biocuration": "HPO:skoehler[2012-11-16]",
    }
    return mock_koza(
        name="hpoa_disease_to_phenotype",
        data=row,
        transform_code="./src/monarch_ingest/ingests/hpoa/disease_to_phenotype.py",
        global_table=global_table,
        local_table="./src/monarch_ingest/ingests/hpoa/hpoa-translation.yaml",
    )


def test_disease_to_phenotype_transform_1(d2pf_entities_1):
    assert d2pf_entities_1
    assert len(d2pf_entities_1) == 1
    association = [entity for entity in d2pf_entities_1 if isinstance(entity, DiseaseToPhenotypicFeatureAssociation)][0]
    assert association.subject == "OMIM:614856"
    assert association.predicate == "biolink:has_phenotype"
    assert association.negated
    assert association.object == "HP:0000343"
    assert len(association.publications) == 0
    assert "ECO:0000304" in association.has_evidence  # from local HPOA translation table
    assert association.sex_qualifier == "PATO:0000383"
    assert association.onset_qualifier == "HP:0003593"
    assert association.has_count == 1
    assert association.has_total == 1
    assert association.has_quotient == 1.0  # '1/1' implies Always present, i.e. in 100% of the cases.
    assert association.has_percentage == 100.0
    assert association.frequency_qualifier is None  # No implied frequency qualifier based on the '1/1' ratio.
    assert association.primary_knowledge_source == "infores:omim"
    assert association.aggregator_knowledge_source == ["infores:monarchinitiative","infores:hpo-annotations"]


@pytest.fixture
def d2pf_entities_2(mock_koza, global_table):
    row = {
        "database_id": "OMIM:117650",
        "disease_name": "Cerebrocostomandibular syndrome",
        "qualifier": "",
        "hpo_id": "HP:0001249",
        "reference": "OMIM:117650",
        "evidence": "TAS",
        "onset": "",
        "frequency": "50%",
        "sex": "",
        "modifier": "",
        "aspect": "P",
        "biocuration": "HPO:probinson[2009-02-17]",
    }
    return mock_koza(
        name="hpoa_disease_to_phenotype",
        data=row,
        transform_code="./src/monarch_ingest/ingests/hpoa/disease_to_phenotype.py",
        global_table=global_table,
        local_table="./src/monarch_ingest/ingests/hpoa/hpoa-translation.yaml",
    )


def test_disease_to_phenotype_transform_2(d2pf_entities_2):
    assert d2pf_entities_2
    assert len(d2pf_entities_2) == 1
    association = [entity for entity in d2pf_entities_2 if isinstance(entity, DiseaseToPhenotypicFeatureAssociation)][0]
    assert association.subject == "OMIM:117650"
    assert association.predicate == "biolink:has_phenotype"
    assert not association.negated
    assert association.object == "HP:0001249"
    assert len(association.publications) == 0
    assert "ECO:0000304" in association.has_evidence  # from local HPOA translation table
    assert not association.sex_qualifier
    assert not association.onset_qualifier
    assert association.has_percentage == 50.0  # '50%' implies Present in 30% to 79% of the cases.
    assert association.has_quotient == 0.5
    assert association.frequency_qualifier is None  # No implied frequency qualifier based on the '50%' ratio.
    assert association.primary_knowledge_source == "infores:omim"
    assert association.aggregator_knowledge_source == ["infores:monarchinitiative","infores:hpo-annotations"]


@pytest.fixture
def d2pf_entities_3(mock_koza, global_table):
    row = {
        "database_id": "OMIM:117650",
        "disease_name": "Cerebrocostomandibular syndrome",
        "qualifier": "",
        "hpo_id": "HP:0001545",
        "reference": "OMIM:117650;PMID:12345",
        "evidence": "TAS",
        "onset": "",
        "frequency": "HP:0040283",
        "sex": "",
        "modifier": "",
        "aspect": "P",
        "biocuration": "HPO:skoehler[2017-07-13]",
    }
    return mock_koza(
        name="hpoa_disease_to_phenotype",
        data=row,
        transform_code="./src/monarch_ingest/ingests/hpoa/disease_to_phenotype.py",
        global_table=global_table,
        local_table="./src/monarch_ingest/ingests/hpoa/hpoa-translation.yaml",
    )


def test_disease_to_phenotype_transform_3(d2pf_entities_3):
    assert d2pf_entities_3
    assert len(d2pf_entities_3) == 1
    association = [entity for entity in d2pf_entities_3 if isinstance(entity, DiseaseToPhenotypicFeatureAssociation)][0]
    assert association.subject == "OMIM:117650"
    assert association.predicate == "biolink:has_phenotype"
    assert not association.negated
    assert association.object == "HP:0001545"
    assert len(association.publications) == 1
    assert "PMID:12345" in association.publications
    assert "ECO:0000304" in association.has_evidence  # from local HPOA translation table
    assert not association.sex_qualifier
    assert not association.onset_qualifier
    assert association.has_count is None
    assert association.has_total is None
    assert association.has_percentage is None
    assert association.has_quotient is None
    assert association.frequency_qualifier == "HP:0040283"  # "HP:0040283" implies Present in 5% to 29% of the cases.
    assert association.primary_knowledge_source == "infores:omim"
    assert association.aggregator_knowledge_source == ["infores:monarchinitiative","infores:hpo-annotations"]



@pytest.fixture
def d2pf_frequency_fraction_entities(mock_koza, global_table, d2pf_entities_1):
    row = {
        "database_id": "OMIM:117650",
        "disease_name": "Cerebrocostomandibular syndrome",
        "qualifier": "",
        "hpo_id": "HP:0001545",
        "reference": "OMIM:117650",
        "evidence": "TAS",
        "onset": "",
        "frequency": "3/20",
        "sex": "",
        "modifier": "",
        "aspect": "P",
        "biocuration": "HPO:skoehler[2017-07-13]",
    }
    return mock_koza(
        name="hpoa_disease_to_phenotype",
        data=row,
        transform_code="./src/monarch_ingest/ingests/hpoa/disease_to_phenotype.py",
        global_table=global_table,
        local_table="./src/monarch_ingest/ingests/hpoa/hpoa-translation.yaml",
    )


def test_disease_to_phenotype_transform_frequency_fraction(d2pf_frequency_fraction_entities):
    assert d2pf_frequency_fraction_entities
    assert len(d2pf_frequency_fraction_entities) == 1
    association = [
        entity
        for entity in d2pf_frequency_fraction_entities
        if isinstance(entity, DiseaseToPhenotypicFeatureAssociation)
    ][0]
    assert association.has_count == 3
    assert association.has_total == 20
    assert association.has_quotient == 0.15
    assert association.has_percentage == 15.0


@pytest.fixture
def count_zero_entities(mock_koza, global_table):
    row = {'database_id': 'OMIM:615654', 'disease_name': 'Deafness, autosomal dominant 58', 'qualifier': '', 'hpo_id': 'HP:0007663', 'reference': 'PMID:32337552', 'evidence': 'PCS', 'onset': '', 'frequency': '0/20', 'sex': '', 'modifier': '', 'aspect': 'P', 'biocuration': 'HPO:probinson[2024-03-15];HPO:probinson[2024-03-15]'}

    return mock_koza(
        name="hpoa_disease_to_phenotype",
        data=[row],
        transform_code="./src/monarch_ingest/ingests/hpoa/disease_to_phenotype.py",
        global_table=global_table,
        local_table="./src/monarch_ingest/ingests/hpoa/hpoa-translation.yaml",
    )


def test_zero_fraction(count_zero_entities):
    entities = count_zero_entities
    assert len(entities) == 1
    association = [entity for entity in entities if isinstance(entity, DiseaseToPhenotypicFeatureAssociation)][0]
    assert association.has_count == 0
    assert association.has_total == 20


@pytest.fixture
def orphanet_entities(mock_koza, global_table):
    row = {'database_id': 'ORPHA:79474', 'disease_name': 'Atypical Werner syndrome', 'qualifier': '', 'hpo_id': 'HP:0000347', 'reference': 'ORPHA:79474', 'evidence': 'TAS', 'onset': '', 'frequency': 'HP:0040281', 'sex': '', 'modifier': '', 'aspect': 'P', 'biocuration': 'ORPHA:orphadata[2024-06-25]'}
    return mock_koza(
        name="hpoa_disease_to_phenotype",
        data=[row],
        transform_code="./src/monarch_ingest/ingests/hpoa/disease_to_phenotype.py",
        global_table=global_table,
        local_table="./src/monarch_ingest/ingests/hpoa/hpoa-translation.yaml",
    )

def test_orphanet_entities(orphanet_entities):
    entities = orphanet_entities
    assert len(entities) == 1
    association = [entity for entity in entities if isinstance(entity, DiseaseToPhenotypicFeatureAssociation)][0]
    assert association.primary_knowledge_source == "infores:orphanet"
