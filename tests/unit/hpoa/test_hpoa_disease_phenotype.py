import pytest

from biolink.pydanticmodel import DiseaseToPhenotypicFeatureAssociation


@pytest.fixture
def d2pf_entities(mock_koza, global_table):
    row = iter(
        [
            {
                "DatabaseID": "OMIM:614856",
                "DiseaseName": "Osteogenesis imperfecta, type XIII",
                "Qualifier": "NOT",
                "HPO_ID": "HP:0000343",
                "Reference": "OMIM:614856",
                "Evidence": "TAS",
                "Onset": "HP:0003593",
                "Frequency": "1/1",
                "Sex": "FEMALE",
                "Modifier": "",
                "Aspect": "C",  # assert 'Clinical' test record
                "Biocuration": "HPO:skoehler[2012-11-16]",
            }
        ]
    )
    return mock_koza(
        name="hpoa_disease_phenotype",
        data=row,
        transform_code="./monarch_ingest/ingests/hpoa/disease_phenotype.py",
        global_table=global_table,
        local_table="./monarch_ingest/ingests/hpoa/hpoa-translation.yaml",
    )


def test_disease_to_phenotype_transform(d2pf_entities):
    assert d2pf_entities
    assert len(d2pf_entities) == 1
    association = [
        entity
        for entity in d2pf_entities
        if isinstance(entity, DiseaseToPhenotypicFeatureAssociation)
    ][0]
    assert association.subject == "OMIM:614856"
    assert association.predicate == "biolink:has_phenotype"
    assert association.negated is True
    assert association.object == "HP:0000343"
    assert "OMIM:614856" in association.publications
    assert "ECO:0000304" in association.has_evidence  # from local HPOA translation table
    assert association.sex_qualifier == "PATO:0000383"
    assert association.onset_qualifier == "HP:0003593"
    assert association.frequency_qualifier == "1/1"
    assert association.primary_knowledge_source == "infores:hpoa"
    assert "infores:monarchinitiative" in association.aggregator_knowledge_source
