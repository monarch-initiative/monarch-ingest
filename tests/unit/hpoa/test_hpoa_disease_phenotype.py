import pytest

from biolink_model_pydantic.model import DiseaseToPhenotypicFeatureAssociation


@pytest.fixture
def entities(mock_koza, global_table):
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


def test_gene_2_phenotype_transform(entities):
    assert entities
    assert len(entities) == 1
    associations = [
        entity
        for entity in entities
        if isinstance(entity, DiseaseToPhenotypicFeatureAssociation)
    ]
    assert len(associations) == 1
    assert associations[0].subject == "OMIM:614856"
    assert associations[0].predicate == "biolink:has_phenotype"
    assert associations[0].negated is True
    assert associations[0].object == "HP:0000343"
    assert "OMIM:614856" in associations[0].publications
    assert "ECO:0000304" in associations[0].has_evidence  # from local HPOA translation table
    assert associations[0].sex_qualifier == "PATO:0000383"
    assert associations[0].onset_qualifier == "HP:0003593"
    assert associations[0].frequency_qualifier == "1/1"


# Commenting out publication node generation in edge ingests, at least temporarily
# def test_disease_phenotype_transform_publications(entities):
#     associations = [
#         entity
#         for entity in entities
#         if isinstance(entity, DiseaseToPhenotypicFeatureAssociation)
#     ]
#     assert associations[0].publications[0] == "OMIM:614856"
