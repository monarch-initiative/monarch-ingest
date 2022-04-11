import pytest
from biolink_model_pydantic.model import GeneToExpressionSiteAssociation

#
# test of utility function - proven to work, unless modified in the future?
#
# def test_get_data():
#     entry = {
#         "testing": {
#             "one": {
#                 "two": {
#                     "three": "Success!"
#                 }
#             }
#         }
#     }
#     assert get_data(entry, "testing.one.two.three") == "Success!"


@pytest.fixture
def source_name():
    return "alliance_gene_to_expression"


@pytest.fixture
def script():
    return "./monarch_ingest/alliance/gene_to_expression.py"


# The Rat data seems to only have gene expression assigned to cellular components
@pytest.fixture
def rat_row():
    # just a single Alliance schema JSON formatted "data" array entry
    return {
        "assay": "MMO:0000640",
        "dateAssigned": "2006-10-24T10:38:36.000-05:00",
        "evidence": {
            "crossReference": {"id": "RGD:1298991", "pages": ["reference"]},
            "publicationId": "PMID:12615975",
        },
        "geneId": "RGD:3143",
        "whenExpressed": {"stageName": "N/A"},
        "whereExpressed": {
            "cellularComponentTermId": "GO:0030141",
            "whereExpressedStatement": "secretory granule",
        },
    }


@pytest.fixture
def rattus(rat_row, mock_koza, source_name, script, global_table):
    rows = iter([rat_row])
    return mock_koza(
        source_name,
        rows,
        script,
        global_table=global_table,
    )


def test_rattus_association(rattus):
    assert len(rattus) > 0
    associations = [
        association
        for association in rattus
        if isinstance(association, GeneToExpressionSiteAssociation)
    ]
    assert associations[0].subject == "RGD:3143"
    assert associations[0].predicate == "biolink:expressed_in"
    assert associations[0].object == "GO:0030141"
    assert associations[0].relation == "RO:0002206"
    assert not associations[0].stage_qualifier
    assert "PMID:12615975" in associations[0].publications
    assert "MMO:0000640" in associations[0].has_evidence
    assert associations[0].source == "infores:rgd"


# Mouse seems to have gene expression in bulk anatomical structures
@pytest.fixture
def mgi_row():
    # just a single Alliance schema JSON formatted "data" array entry
    return {
        "assay": "MMO:0000655",
        "crossReference": {
            "id": "MGI:1203979",
            "pages": ["gene/expression/annotation/detail"],
        },
        "dateAssigned": "2018-07-18T13:27:43-04:00",
        "evidence": {
            "crossReference": {"id": "MGI:1199209", "pages": ["reference"]},
            "publicationId": "MGI:1199209",
        },
        "geneId": "MGI:99180",
        "whenExpressed": {
            "stageName": "TS23",
            "stageUberonSlimTerm": {"uberonTerm": "post embryonic, pre-adult"},
        },
        "whereExpressed": {
            "anatomicalStructureTermId": "EMAPA:16039",
            "anatomicalStructureUberonSlimTermIds": [{"uberonTerm": "Other"}],
            "whereExpressedStatement": "embryo",
        },
    }


@pytest.fixture
def mouse(mgi_row, mock_koza, source_name, script, global_table):
    rows = iter([mgi_row])
    return mock_koza(
        source_name,
        rows,
        script,
        global_table=global_table,
    )


def test_mouse_association(mouse):
    associations = [
        association
        for association in mouse
        if isinstance(association, GeneToExpressionSiteAssociation)
    ]
    assert associations[0].subject == "MGI:99180"
    assert associations[0].predicate == "biolink:expressed_in"
    assert associations[0].object == "EMAPA:16039"
    assert associations[0].relation == "RO:0002206"
    assert associations[0].stage_qualifier is None
    assert "MGI:1199209" in associations[0].publications
    assert "MMO:0000655" in associations[0].has_evidence
    assert "MGI:1203979" in associations[0].has_evidence
    assert associations[0].source == "infores:mgi"


# Zebrafish has rich gene expression associations with
# tissue level and above anatomical entities
@pytest.fixture
def zfin_row():
    # just a single Alliance schema JSON formatted "data" array entry
    return {
        "dateAssigned": "2022-01-21T07:09:02-08:00",
        "geneId": "ZFIN:ZDB-GENE-031222-3",
        "evidence": {
            "crossReference": {"id": "ZFIN:ZDB-PUB-080616-21", "pages": ["reference"]},
            "publicationId": "PMID:18544660",
        },
        "crossReference": {
            "id": "ZFIN:ZDB-FIG-080908-4",
            "pages": ["gene/expression/annotation/detail"],
        },
        "assay": "MMO:0000655",
        "whenExpressed": {
            "stageName": "Larval:Protruding-mouth",
            "stageTermId": "ZFS:0000035",
            "stageUberonSlimTerm": {"uberonTerm": "post embryonic, pre-adult"},
        },
        "whereExpressed": {
            "whereExpressedStatement": "whole organism",
            "anatomicalStructureTermId": "ZFA:0001094",
            "anatomicalStructureUberonSlimTermIds": [{"uberonTerm": "Other"}],
        },
    }


@pytest.fixture
def zebrafish(zfin_row, mock_koza, source_name, script, global_table):
    rows = iter([zfin_row])
    return mock_koza(
        source_name,
        rows,
        script,
        global_table=global_table,
    )


def test_zebrafish_association(zebrafish):
    assert len(zebrafish) > 0
    associations = [
        association
        for association in zebrafish
        if isinstance(association, GeneToExpressionSiteAssociation)
    ]
    assert associations[0].subject == "ZFIN:ZDB-GENE-031222-3"
    assert associations[0].predicate == "biolink:expressed_in"
    assert associations[0].object == "ZFA:0001094"
    assert associations[0].relation == "RO:0002206"
    assert associations[0].stage_qualifier == "ZFS:0000035"
    assert "PMID:18544660" in associations[0].publications
    assert "MMO:0000655" in associations[0].has_evidence
    assert "ZFIN:ZDB-FIG-080908-4" in associations[0].has_evidence
    assert associations[0].source == "infores:zfin"


# Drosophila has some embryonic staged gene expression associations with anatomical entities
@pytest.fixture
def fly_row():
    return {
        "assay": "MMO:0000534",
        "dateAssigned": "2022-01-12T10:12:11-05:00",
        "evidence": {"publicationId": "FB:FBrf0231198"},
        "geneId": "FB:FBgn0010339",
        "whenExpressed": {
            "stageName": "adult stage",
            "stageTermId": "FBdv:00005369",
            "stageUberonSlimTerm": {"uberonTerm": "UBERON:0000113"},
        },
        "whereExpressed": {
            "anatomicalStructureTermId": "FBbt:00003007",
            "anatomicalStructureUberonSlimTermIds": [{"uberonTerm": "Other"}],
            "cellularComponentTermId": "GO:0016020",
            "whereExpressedStatement": "membrane in adult head",
        },
    }


@pytest.fixture
def drosophila(fly_row, mock_koza, source_name, script, global_table):
    rows = iter([fly_row])
    return mock_koza(
        source_name,
        rows,
        script,
        global_table=global_table,
    )


def test_drosophila_association(drosophila):
    associations = [
        association
        for association in drosophila
        if isinstance(association, GeneToExpressionSiteAssociation)
    ]
    assert associations[0].subject == "FB:FBgn0010339"
    assert associations[0].predicate == "biolink:expressed_in"
    assert associations[0].object == "FBbt:00003007"
    assert associations[0].relation == "RO:0002206"
    assert associations[0].stage_qualifier == "FBdv:00005369"
    assert "FB:FBrf0231198" in associations[0].publications
    assert "MMO:0000534" in associations[0].has_evidence
    assert associations[0].source == "infores:flybase"


# Caenorhabditis elegans
@pytest.fixture
def worm_row():
    return {
        "assay": "MMO:0000670",
        "crossReference": {
            "id": "WB:Expr1",
            "pages": ["gene/expression/annotation/detail"],
        },
        "dateAssigned": "2021-11-10T00:12:21+00:00",
        "evidence": {
            "crossReference": {"id": "WB:WBPaper00001469", "pages": ["reference"]},
            "publicationId": "PMID:1782857",
        },
        "geneId": "WB:WBGene00001386",
        "whenExpressed": {
            "stageName": "adult hermaphrodite Ce",
            "stageTermId": "WBls:0000057",
            "stageUberonSlimTerm": {"uberonTerm": "UBERON:0000113"},
        },
        "whereExpressed": {
            "anatomicalStructureTermId": "WBbt:0000100",
            "anatomicalStructureUberonSlimTermIds": [{"uberonTerm": "Other"}],
            "whereExpressedStatement": "C. elegans Cell and Anatomy",
        },
    }


@pytest.fixture
def worm(worm_row, mock_koza, source_name, script, global_table):
    rows = iter([worm_row])
    return mock_koza(
        source_name,
        rows,
        script,
        global_table=global_table,
    )


def test_worm_association(worm):
    associations = [
        association
        for association in worm
        if isinstance(association, GeneToExpressionSiteAssociation)
    ]
    assert associations[0].subject == "WB:WBGene00001386"
    assert associations[0].predicate == "biolink:expressed_in"
    assert associations[0].object == "WBbt:0000100"
    assert associations[0].relation == "RO:0002206"
    assert associations[0].stage_qualifier == "WBls:0000057"
    assert associations[0].publications[0] == "PMID:1782857"
    assert "MMO:0000670" in associations[0].has_evidence
    assert "WB:Expr1" in associations[0].has_evidence
    assert associations[0].source == "infores:wormbase"


# Saccharomyces cerevisiae has rich gene expression associations
# with subcellular (Gene Ontology tagged) CellularComponent entities
@pytest.fixture
def sgd_row():
    return {
        "assay": "MMO:0000642",
        "dateAssigned": "2018-01-18T00:01:00-00:00",
        "evidence": {
            "crossReference": {"id": "SGD:S000184034", "pages": ["reference"]},
            "publicationId": "PMID:26753620",
        },
        "geneId": "SGD:S000002429",
        "whenExpressed": {"stageName": "N/A"},
        "whereExpressed": {
            "cellularComponentTermId": "GO:1990316",
            "whereExpressedStatement": "Atg1/ULK1 kinase complex",
        },
    }


@pytest.fixture
def yeast(sgd_row, mock_koza, source_name, script, global_table):
    rows = iter([sgd_row])
    return mock_koza(
        source_name,
        rows,
        script,
        global_table=global_table,
    )


def test_yeast_association(yeast):
    associations = [
        association
        for association in yeast
        if isinstance(association, GeneToExpressionSiteAssociation)
    ]
    assert associations[0].subject == "SGD:S000002429"
    assert associations[0].predicate == "biolink:expressed_in"
    assert associations[0].object == "GO:1990316"
    assert associations[0].relation == "RO:0002206"
    assert not associations[0].stage_qualifier
    assert associations[0].publications[0] == "PMID:26753620"
    assert "MMO:0000642" in associations[0].has_evidence
    assert associations[0].source == "infores:sgd"
