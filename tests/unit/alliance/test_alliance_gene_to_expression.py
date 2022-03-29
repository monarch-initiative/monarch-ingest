import pytest
from biolink_model_pydantic.model import (
    Gene,
    GeneToExpressionSiteAssociation,
    AnatomicalEntity,
    CellularComponent
)


@pytest.fixture
def source_name():
    return "alliance_gene_to_expression"


@pytest.fixture
def script():
    return "./monarch_ingest/alliance/gene_to_expression.py"


@pytest.fixture
def map_cache():
    return {
        "alliance-gene":
            {
                "ZFIN:ZDB-GENE-010226-1": {"gene_id": "ZFIN:ZDB-GENE-010226-1"},
                "SGD:S000002429": {"gene_id": "SGD:S000002429"}
            }
    }


# Zebrafish has rich gene expression associations with
# tissue level and above anatomical entities
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


def test_zebrafish_gene_id(zebrafish):
    genes = [gene for gene in zebrafish if isinstance(gene, Gene)]
    assert genes[0].id == "ZFIN:ZDB-GENE-010226-1"


def test_zebrafish_expression_feature_id(zebrafish):
    expressions = [
        expression for expression in zebrafish if isinstance(expression, AnatomicalEntity)
    ]
    assert expressions[0].id == "MP:0001625"


def test_zebrafish_association_publication(zebrafish):
    associations = [
        association
        for association in zebrafish
        if isinstance(association, GeneToExpressionSiteAssociation)
    ]
    assert associations[0].publications[0] == "PMID:11237470"


# Saccharomyces cerevisiae has rich gene expression associations
# with subcellular (Gene Ontology tagged) CellularComponent entities
@pytest.fixture
def sgd_row():
    return {
        "Species": "Saccharomyces cerevisiae",
        "SpeciesID": "NCBITaxon:559292",
        "GeneID": "SGD:S000002429",
        "GeneSymbol": "ATG31",
        "Location": "cytoplasm",
        "StageTerm": "",
        "AssayID": "MMO:0000662",
        "AssayTermName": "immunofluorescence",
        "CellularComponentID": "GO:0005737",
        "CellularComponentTerm": "cytoplasm",
        "CellularComponentQualifierIDs": None,
        "CellularComponentQualifierTermNames": None,
        "SubStructureID": None,
        "SubStructureName": None,
        "SubStructureQualifierIDs": None,
        "SubStructureQualifierTermNames": None,
        "AnatomyTermID": None,
        "AnatomyTermName": None,
        "AnatomyTermQualifierIDs": None,
        "AnatomyTermQualifierTermNames": None,
        "SourceURL": None,
        "Source": "SGD",
        "Reference": ["PMID:14562095"]
    }


@pytest.fixture
def yeast(sgd_row, mock_koza, source_name, script, map_cache, global_table):
    rows = iter([sgd_row])
    return mock_koza(
        source_name,
        rows,
        script,
        map_cache=map_cache,
        global_table=global_table,
    )


def test_yeast_gene_id(yeast):
    genes = [gene for gene in yeast if isinstance(gene, Gene)]
    assert genes[0].id == "SGD:S000002429"


def test_yeast_expression_feature_id(yeast):
    expressions = [
        expression for expression in yeast if isinstance(expression, CellularComponent)
    ]
    assert expressions[0].id == "MP:0001625"


def test_yeast_association_publication(yeast):
    associations = [
        association
        for association in yeast
        if isinstance(association, GeneToExpressionSiteAssociation)
    ]
    assert associations[0].publications[0] == "PMID:14562095"
