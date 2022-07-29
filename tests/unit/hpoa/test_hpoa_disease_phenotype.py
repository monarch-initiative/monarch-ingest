import pytest

from biolink.pydanticmodel import (
    Disease,
    DiseaseToPhenotypicFeatureAssociation
)


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


@pytest.fixture
def d2moi_entities(mock_koza, global_table):
    row = iter(
        [
            {
                "DatabaseID": "OMIM:300425",
                "DiseaseName": "Autism susceptibility, X-linked 1",
                "Qualifier": "",
                "HPO_ID": "HP:0001417",
                "Reference": "OMIM:300425",
                "Evidence": "IEA",
                "Onset": "",
                "Frequency": "",
                "Sex": "",
                "Modifier": "",
                "Aspect": "I",  # assert 'Inheritance' test record
                "Biocuration": "HPO:iea[2009-02-17]",
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


def test_disease_to_mode_of_inheritance_transform(d2moi_entities):
    assert d2moi_entities
    assert len(d2moi_entities) == 1
    disease: Disease = [
        entity
        for entity in d2moi_entities
        if isinstance(entity, Disease)
    ][0]
    assert disease.id == "OMIM:300425"
    assert "HP:0001417" in disease.has_attribute
    assert "infores:hpoa" in disease.provided_by


# Commenting out publication node generation in edge ingests, at least temporarily
# def test_disease_phenotype_transform_publications(entities):
#     associations = [
#         entity
#         for entity in entities
#         if isinstance(entity, DiseaseToPhenotypicFeatureAssociation)
#     ]
#     assert association.publications[0] == "OMIM:614856"
