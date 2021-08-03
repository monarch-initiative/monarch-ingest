import pytest
from biolink_model_pydantic.model import (
    Gene,
    GeneToPhenotypicFeatureAssociation,
    PhenotypicFeature,
)
from koza.koza_runner import get_translation_table


@pytest.fixture
def tt():
    return get_translation_table("./mingestibles/translation_table.yaml", None)


@pytest.fixture
def source_name():
    return "gene-to-phenotype"


@pytest.fixture
def script():
    return "./mingestibles/alliance/gene2phenotype.py"


@pytest.fixture
def map_cache():
    return {"alliance-gene": {"RGD:61958": {"gene_id": "RGD:61958"}}}


@pytest.fixture
def rat_row():
    return {
        "dateAssigned": "2006-10-25T18:06:17.000-05:00",
        "evidence": {
            "crossReference": {"id": "RGD:1357201", "pages": ["reference"]},
            "publicationId": "PMID:11549339",
        },
        "objectId": "RGD:61958",
        "phenotypeStatement": "cardiac hypertrophy",
        "phenotypeTermIdentifiers": [{"termId": "MP:0001625", "termOrder": 1}],
    }


@pytest.fixture
def rat(rat_row, mock_koza, source_name, script, map_cache, tt):
    # First row is a gene, second is a feature and should get ignored
    rows = iter([rat_row])

    return mock_koza(
        source_name,
        rows,
        script,
        map_cache=map_cache,
        translation_table=tt,
    )


# TODO: can this test be shared across all g2p loads?
@pytest.mark.parametrize(
    "cls", [Gene, PhenotypicFeature, GeneToPhenotypicFeatureAssociation]
)
def confirm_one_of_each_classes(cls, rat):
    class_entities = [entity for entity in rat if isinstance(entity, cls)]
    assert class_entities
    assert len(class_entities) == 1
    assert class_entities[0]


def test_association_publication(rat):
    associations = [
        association
        for association in rat
        if isinstance(association, GeneToPhenotypicFeatureAssociation)
    ]
    assert associations[0].publications[0] == "PMID:11549339"
