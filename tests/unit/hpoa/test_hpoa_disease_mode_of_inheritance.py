import pytest

from biolink.pydanticmodel import DiseaseOrPhenotypicFeatureToGeneticInheritanceAssociation


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
        name="hpoa_disease_mode_of_inheritance",
        data=row,
        transform_code="./src/monarch_ingest/ingests/hpoa/disease_mode_of_inheritance.py",
        global_table=global_table,
        local_table="./src/monarch_ingest/ingests/hpoa/hpoa-translation.yaml",
    )


def test_disease_to_mode_of_inheritance_transform(d2moi_entities):
    assert d2moi_entities
    assert len(d2moi_entities) == 1
    association = [
        entity
        for entity in d2moi_entities
        if isinstance(entity, DiseaseOrPhenotypicFeatureToGeneticInheritanceAssociation)
    ][0]
    assert association.subject == "OMIM:300425"

    assert association.predicate == "biolink:has_mode_of_inheritance"

    assert association.object == "HP:0001417"
    assert "OMIM:300425" in association.publications
    assert "ECO:0000501" in association.has_evidence  # from local HPOA translation table
    assert association.primary_knowledge_source == "infores:hpoa"
    assert "infores:monarchinitiative" in association.aggregator_knowledge_source
