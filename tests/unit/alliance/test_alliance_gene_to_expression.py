import pytest
from biolink.pydanticmodel import GeneToExpressionSiteAssociation

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
    return "./monarch_ingest/ingests/alliance/gene_to_expression.py"


def aggregator_knowledge_sources(association) -> bool:
    return all(
        [
            ks in ["infores:monarchinitiative", "infores:alliancegenome"]
            for ks in association.aggregator_knowledge_source
        ]
    )


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
    association = [
        association
        for association in rattus
        if isinstance(association, GeneToExpressionSiteAssociation)
    ][0]
    assert association.subject == "RGD:3143"
    assert association.predicate == "biolink:expressed_in"
    assert association.object == "GO:0030141"
    assert not association.stage_qualifier
    assert "PMID:12615975" in association.publications
    assert "MMO:0000640" in association.has_evidence
    assert association.primary_knowledge_source == "infores:rgd"
    assert aggregator_knowledge_sources(association)


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
    association = [
        association
        for association in mouse
        if isinstance(association, GeneToExpressionSiteAssociation)
    ][0]
    assert association.subject == "MGI:99180"
    assert association.predicate == "biolink:expressed_in"
    assert association.object == "EMAPA:16039"
    assert association.stage_qualifier is None
    assert "MGI:1199209" in association.publications
    assert "MMO:0000655" in association.has_evidence
    assert "MGI:1203979" in association.has_evidence
    assert association.primary_knowledge_source == "infores:mgi"
    assert aggregator_knowledge_sources(association)


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
    association = [
        association
        for association in zebrafish
        if isinstance(association, GeneToExpressionSiteAssociation)
    ][0]
    assert association.subject == "ZFIN:ZDB-GENE-031222-3"
    assert association.predicate == "biolink:expressed_in"
    assert association.object == "ZFA:0001094"
    assert association.stage_qualifier == "ZFS:0000035"
    assert "PMID:18544660" in association.publications
    assert "MMO:0000655" in association.has_evidence
    assert "ZFIN:ZDB-FIG-080908-4" in association.has_evidence
    assert association.primary_knowledge_source == "infores:zfin"
    assert aggregator_knowledge_sources(association)


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
    association = [
        association
        for association in drosophila
        if isinstance(association, GeneToExpressionSiteAssociation)
    ][0]
    assert association.subject == "FB:FBgn0010339"
    assert association.predicate == "biolink:expressed_in"
    assert association.object == "FBbt:00003007"
    assert association.stage_qualifier == "FBdv:00005369"
    assert "FB:FBrf0231198" in association.publications
    assert "MMO:0000534" in association.has_evidence
    assert association.primary_knowledge_source == "infores:flybase"
    assert aggregator_knowledge_sources(association)


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
    association = [
        association
        for association in worm
        if isinstance(association, GeneToExpressionSiteAssociation)
    ][0]
    assert association.subject == "WB:WBGene00001386"
    assert association.predicate == "biolink:expressed_in"
    assert association.object == "WBbt:0000100"
    assert association.stage_qualifier == "WBls:0000057"
    assert association.publications[0] == "PMID:1782857"
    assert "MMO:0000670" in association.has_evidence
    assert "WB:Expr1" in association.has_evidence
    assert association.primary_knowledge_source == "infores:wormbase"
    assert aggregator_knowledge_sources(association)


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
    assert len(yeast) > 0
    association = [
        association
        for association in yeast
        if isinstance(association, GeneToExpressionSiteAssociation)
    ][0]
    assert association.subject == "SGD:S000002429"
    assert association.predicate == "biolink:expressed_in"
    assert association.object == "GO:1990316"
    assert not association.stage_qualifier
    assert association.publications[0] == "PMID:26753620"
    assert "MMO:0000642" in association.has_evidence
    assert association.primary_knowledge_source == "infores:sgd"
    assert aggregator_knowledge_sources(association)
