import pytest

from biolink.pydanticmodel import DiseaseToPhenotypicFeatureAssociation


@pytest.fixture
def d2pf_entities_1(mock_koza, global_table):
    row = iter(
        [
            {
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
        ]
    )
    return mock_koza(
        name="hpoa_disease_phenotype",
        data=row,
        transform_code="./src/monarch_ingest/ingests/hpoa/disease_phenotype.py",
        global_table=global_table,
        local_table="./src/monarch_ingest/ingests/hpoa/hpoa-translation.yaml",
    )


def test_disease_to_phenotype_transform_1(d2pf_entities_1):
    assert d2pf_entities_1
    assert len(d2pf_entities_1) == 1
    association = [
        entity
        for entity in d2pf_entities_1
        if isinstance(entity, DiseaseToPhenotypicFeatureAssociation)
    ][0]
    assert association.subject == "OMIM:614856"
    assert association.predicate == "biolink:has_phenotype"
    assert association.negated
    assert association.object == "HP:0000343"
    assert "OMIM:614856" in association.publications
    assert "ECO:0000304" in association.has_evidence  # from local HPOA translation table
    assert association.sex_qualifier == "PATO:0000383"
    assert association.onset_qualifier == "HP:0003593"
    assert association.has_percentage is None
    assert association.has_quotient == 1.0  # '1/1' implies Always present, i.e. in 100% of the cases.
    assert association.frequency_qualifier == "HP:0040280"  # '1/1' implies Always present, i.e. in 100% of the cases.
    assert association.primary_knowledge_source == "infores:hpo-annotations"
    assert "infores:monarchinitiative" in association.aggregator_knowledge_source


@pytest.fixture
def d2pf_entities_2(mock_koza, global_table):
    row = iter(
        [
            {
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
        ]
    )
    return mock_koza(
        name="hpoa_disease_phenotype",
        data=row,
        transform_code="./src/monarch_ingest/ingests/hpoa/disease_phenotype.py",
        global_table=global_table,
        local_table="./src/monarch_ingest/ingests/hpoa/hpoa-translation.yaml",
    )


def test_disease_to_phenotype_transform_2(d2pf_entities_2):
    assert d2pf_entities_2
    assert len(d2pf_entities_2) == 1
    association = [
        entity
        for entity in d2pf_entities_2
        if isinstance(entity, DiseaseToPhenotypicFeatureAssociation)
    ][0]
    assert association.subject == "OMIM:117650"
    assert association.predicate == "biolink:has_phenotype"
    assert not association.negated
    assert association.object == "HP:0001249"
    assert "OMIM:117650" in association.publications
    assert "ECO:0000304" in association.has_evidence  # from local HPOA translation table
    assert not association.sex_qualifier
    assert not association.onset_qualifier
    assert association.has_percentage == 50.0  # '50%' implies Present in 30% to 79% of the cases.
    assert association.has_quotient is None
    assert association.frequency_qualifier == "HP:0040282"  # '50%' implies Present in 30% to 79% of the cases.
    assert association.primary_knowledge_source == "infores:hpo-annotations"
    assert "infores:monarchinitiative" in association.aggregator_knowledge_source


@pytest.fixture
def d2pf_entities_3(mock_koza, global_table):
    row = iter(
        [
            {
                "database_id": "OMIM:117650",
                "disease_name": "Cerebrocostomandibular syndrome",
                "qualifier": "",
                "hpo_id": "HP:0001545",
                "reference": "OMIM:117650",
                "evidence": "TAS",
                "onset": "",
                "frequency": "HP:0040283",
                "sex": "",
                "modifier": "",
                "aspect": "P",
                "biocuration": "HPO:skoehler[2017-07-13]",
            }
        ]
    )
    return mock_koza(
        name="hpoa_disease_phenotype",
        data=row,
        transform_code="./src/monarch_ingest/ingests/hpoa/disease_phenotype.py",
        global_table=global_table,
        local_table="./src/monarch_ingest/ingests/hpoa/hpoa-translation.yaml",
    )


def test_disease_to_phenotype_transform_3(d2pf_entities_3):
    assert d2pf_entities_3
    assert len(d2pf_entities_3) == 1
    association = [
        entity
        for entity in d2pf_entities_3
        if isinstance(entity, DiseaseToPhenotypicFeatureAssociation)
    ][0]
    assert association.subject == "OMIM:117650"
    assert association.predicate == "biolink:has_phenotype"
    assert not association.negated
    assert association.object == "HP:0001545"
    assert "OMIM:117650" in association.publications
    assert "ECO:0000304" in association.has_evidence  # from local HPOA translation table
    assert not association.sex_qualifier
    assert not association.onset_qualifier
    assert association.has_percentage is None
    assert association.has_quotient is None
    assert association.frequency_qualifier == "HP:0040283"  # "HP:0040283" implies Present in 5% to 29% of the cases.
    assert association.primary_knowledge_source == "infores:hpo-annotations"
    assert "infores:monarchinitiative" in association.aggregator_knowledge_source
