import pytest
from biolink_model_pydantic.model import (
    Gene,
    GeneToExpressionSiteAssociation,
    AnatomicalEntity,
)


@pytest.fixture
def source_name():
    return "alliance_gene_to_expression"


@pytest.fixture
def script():
    return "./monarch_ingest/alliance/gene_to_expression.py"


@pytest.fixture
def map_cache():
    return {"alliance-gene": {"ZFIN:ZDB-GENE-010226-1": {"gene_id": "ZFIN:ZDB-GENE-010226-1"}}}


@pytest.fixture
def zfin_row():
    return {
        "Species": "Danio rerio",
        "SpeciesID": "NCBITaxon:7955",
        "GeneID": "ZFIN:ZDB-GENE-010226-1",
        "GeneSymbol": "gdnfa",
        "Location": "intermediate mesoderm",
        "StageTerm": "Segmentation:10-13 somites",
        "AssayID": "MMO:0000658",
        "AssayTermName": "ribonucleic acid in situ hybridization assay",
        "CellularComponentID": None,
        "CellularComponentTerm": None,
        "CellularComponentQualifierIDs": None,
        "CellularComponentQualifierTermNames": None,
        "SubStructureID": None,
        "SubStructureName": None,
        "SubStructureQualifierIDs": None,
        "SubStructureQualifierTermNames": None,
        "AnatomyTermID": "ZFA:0001206",
        "AnatomyTermName": "intermediate mesoderm",
        "AnatomyTermQualifierIDs": None,
        "AnatomyTermQualifierTermNames": None,
        "SourceURL": ["https://zfin.org/ZDB-FIG-110701-1"],
        "Source": "ZFIN",
        "Reference": ["PMID:11237470"]
    }


@pytest.fixture
def zebrafish(zfin_row, mock_koza, source_name, script, map_cache, global_table):
    rows = iter([zfin_row])

    return mock_koza(
        source_name,
        rows,
        script,
        map_cache=map_cache,
        global_table=global_table,
    )


def test_gene_id(zebrafish):
    genes = [gene for gene in zebrafish if isinstance(gene, Gene)]
    assert genes[0].id == "ZFIN:ZDB-GENE-010226-1"


def test_expression_feature_id(zebrafish):
    expressions = [
        expression for expression in zebrafish if isinstance(expression, AnatomicalEntity)
    ]
    assert expressions[0].id == "MP:0001625"


def test_association_publication(zebrafish):
    associations = [
        association
        for association in zebrafish
        if isinstance(association, GeneToExpressionSiteAssociation)
    ]
    assert associations[0].publications[0] == "PMID:11237470"


@pytest.fixture
def expression_row(zfin_row):
    zfin_row["conditionRelations"] = [
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

    return zfin_row


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
        if isinstance(association, GeneToExpressionSiteAssociation)
    ]
    assert "ZECO:0000111" in associations[0].qualifiers


# TODO: can this test be shared across all g2e loads?
@pytest.mark.parametrize(
    "cls", [Gene, AnatomicalEntity, GeneToExpressionSiteAssociation]
)
def confirm_one_of_each_classes(cls, zebrafish):
    class_entities = [entity for entity in zebrafish if isinstance(entity, cls)]
    assert class_entities
    assert len(class_entities) == 1
    assert class_entities[0]
