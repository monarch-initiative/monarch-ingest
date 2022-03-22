import pytest
from biolink_model_pydantic.model import (
    Gene,
    GeneToexpressionFeatureAssociation,
    expressionFeature,
)


@pytest.fixture
def source_name():
    return "alliance_gene_to_expression"


@pytest.fixture
def script():
    return "./monarch_ingest/alliance/gene_to_expression.py"


@pytest.fixture
def map_cache():
    raise NotImplementedError
    # return {"alliance-gene": {"RGD:61958": {"gene_id": "RGD:61958"}}}


@pytest.fixture
def rat_row():
    raise NotImplementedError
    # return {
    #     "dateAssigned": "2006-10-25T18:06:17.000-05:00",
    #     "evidence": {
    #         "crossReference": {"id": "RGD:1357201", "pages": ["reference"]},
    #         "publicationId": "PMID:11549339",
    #     },
    #     "objectId": "RGD:61958",
    #     "expressionStatement": "cardiac hypertrophy",
    #     "expressionTermIdentifiers": [{"termId": "MP:0001625", "termOrder": 1}],
    # }


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


def test_gene_id(rat):
    genes = [gene for gene in rat if isinstance(gene, Gene)]
    assert genes[0].id == "RGD:61958"


def test_expression_feature_id(rat):
    expressions = [
        expression for expression in rat if isinstance(expression, expressionFeature)
    ]
    assert expressions[0].id == "MP:0001625"


def test_association_publication(rat):
    associations = [
        association
        for association in rat
        if isinstance(association, GeneToexpressionFeatureAssociation)
    ]
    assert associations[0].publications[0] == "PMID:11549339"


@pytest.fixture
def expression_row(rat_row):
    rat_row["conditionRelations"] = [
        {
            "conditionRelationType": "has_condition",
            "expression": [
                {
                    "conditionClassId": "ZECO:0000111",
                    "expressiontatement": "chemical:glycogen",
                    "chemicalOntologyId": "CHEBI:28087",
                }
            ],
        }
    ]

    return rat_row


@pytest.fixture
def expression_entities(
    expression_row, mock_koza, source_name, script, map_cache, global_table
):
    rows = iter([expression_row])

    return mock_koza(
        source_name,
        rows,
        script,
        map_cache=map_cache,
        global_table=global_table,
    )


def test_expression(expression_entities):
    associations = [
        association
        for association in expression_entities
        if isinstance(association, GeneToexpressionFeatureAssociation)
    ]
    assert "ZECO:0000111" in associations[0].qualifiers


# TODO: can this test be shared across all g2e loads?
@pytest.mark.parametrize(
    "cls", [Gene, expressionFeature, GeneToexpressionFeatureAssociation]
)
def confirm_one_of_each_classes(cls, rat):
    class_entities = [entity for entity in rat if isinstance(entity, cls)]
    assert class_entities
    assert len(class_entities) == 1
    assert class_entities[0]
