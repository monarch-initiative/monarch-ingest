import pytest

from biolink.pydanticmodel import Disease


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
        transform_code="./monarch_ingest/ingests/hpoa/disease_mode_of_inheritance.py",
        global_table=global_table,
        local_table="./monarch_ingest/ingests/hpoa/hpoa-modes-of-inheritance.yaml",
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
