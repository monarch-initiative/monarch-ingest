import pytest

from biolink.pydanticmodel import (
    Gene,
    GeneToPhenotypicFeatureAssociation,
    PhenotypicFeature
)


@pytest.fixture
def source_name():
    return "alliance_gene_to_phenotype"


@pytest.fixture
def script():
    return "./monarch_ingest/ingests/alliance/gene_to_phenotype.py"


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
def rat(rat_row, mock_koza, source_name, script, map_cache, global_table):
    # First row is a gene, second is a feature and should get ignored
    rows = iter([rat_row])

    return mock_koza(
        source_name,
        rows,
        script,
        map_cache=map_cache,
        global_table=global_table,
    )


def test_association_publication(rat):
    association = [
        association
        for association in rat
        if isinstance(association, GeneToPhenotypicFeatureAssociation)
    ][0]
    assert association.publications[0] == "PMID:11549339"


@pytest.fixture
def conditions_row(rat_row):
    rat_row["conditionRelations"] = [
        {
            "conditionRelationType": "has_condition",
            "conditions": [
                {
                    "conditionClassId": "ZECO:0000111",
                    "conditionStatement": "chemical:glycogen",
                    "chemicalOntologyId": "CHEBI:28087",
                }
            ],
        }
    ]

    return rat_row


@pytest.fixture
def conditions_entities(
    conditions_row, mock_koza, source_name, script, map_cache, global_table
):
    rows = iter([conditions_row])

    return mock_koza(
        source_name,
        rows,
        script,
        map_cache=map_cache,
        global_table=global_table,
    )


def test_conditions(conditions_entities):
    association = [
        association
        for association in conditions_entities
        if isinstance(association, GeneToPhenotypicFeatureAssociation)
    ][0]
    assert any(["ZECO:0000111" == term.id for term in association.qualifiers])
    assert association.primary_knowledge_source == "infores:rgd"
    assert "infores:monarchinitiative" in association.aggregator_knowledge_source
    assert "infores:alliancegenome" in association.aggregator_knowledge_source


# TODO: can this test be shared across all g2p loads?
@pytest.mark.parametrize(
    "cls", [Gene, PhenotypicFeature, GeneToPhenotypicFeatureAssociation]
)
def confirm_one_of_each_classes(cls, rat):
    class_entities = [entity for entity in rat if isinstance(entity, cls)]
    assert class_entities
    assert len(class_entities) == 1
    assert class_entities[0]
