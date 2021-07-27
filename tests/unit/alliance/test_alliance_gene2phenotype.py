import pytest
from biolink_model_pydantic.model import (
    Gene,
    GeneToPhenotypicFeatureAssociation,
    PhenotypicFeature,
)
from koza.koza_runner import get_translation_table


@pytest.fixture
def entities(mock_koza):
    # First row is a gene, second is a feature and should get ignored
    rows = iter(
        [
            {
                "dateAssigned": "2006-10-25T18:06:17.000-05:00",
                "evidence": {
                    "crossReference": {"id": "RGD:1357201", "pages": ["reference"]},
                    "publicationId": "PMID:11549339",
                },
                "objectId": "RGD:61958",
                "phenotypeStatement": "cardiac hypertrophy",
                "phenotypeTermIdentifiers": [{"termId": "MP:0001625", "termOrder": 1}],
            },
            {
                "dateAssigned": "2008-07-23T00:00:00.000-05:00",
                "evidence": {
                    "crossReference": {"id": "RGD:625461", "pages": ["reference"]},
                    "publicationId": "PMID:12195039",
                },
                "objectId": "RGD:2298772",
                "phenotypeStatement": "fuzzy hair",
                "phenotypeTermIdentifiers": [{"termId": "MP:0009930", "termOrder": 1}],
            },
        ]
    )
    map_cache = {"rgd-gene": {"61958": {"DB_Object_Type": "gene"}}}
    tt = get_translation_table("./mingestibles/translation_table.yaml", None)

    return mock_koza(
        "gene-to-phenotype",
        rows,
        "./mingestibles/alliance/gene2phenotype.py",
        map_cache=map_cache,
        translation_table=tt,
    )


# TODO: can this test be shared across all g2p loads?
@pytest.mark.parametrize(
    "cls", [Gene, PhenotypicFeature, GeneToPhenotypicFeatureAssociation]
)
def confirm_one_of_each_classes(cls, entities):
    class_entities = [entity for entity in entities if isinstance(entity, cls)]
    assert class_entities
    assert len(class_entities) == 1
    assert class_entities[0]


def test_association_publication(entities):
    associations = [
        association
        for association in entities
        if isinstance(association, GeneToPhenotypicFeatureAssociation)
    ]
    assert associations[0].publications[0] == "PMID:11549339"
