import pytest

from biolink_model_pydantic.model import GeneToExpressionSiteAssociation
from monarch_ingest.alliance.utils import get_data


def test_get_data():
    entry = {
        "testing": {
            "one": {
                "two": {
                    "three": "Success!"
                }
            }
        }
    }
    assert get_data(entry, "testing.one.two.three") == "Success!"


@pytest.fixture
def source_name():
    return "alliance_gene_to_expression"


@pytest.fixture
def script():
    return "./monarch_ingest/alliance/gene_to_expression.py"


# The Rat data seems to only have gene expression assigned to cellular components
@pytest.fixture
def rat_row():
    #
    # Deprecated original input file format
    #
    # return {
    #     "Species": "Rattus norvegicus",
    #     "SpeciesID": "NCBITaxon:10116",
    #     "GeneID": "RGD:619834",
    #     "GeneSymbol": "A1cf",
    #     "Location": "cytoplasm",
    #     "StageTerm": "",
    #     "AssayID": "MMO:0000640",
    #     "AssayTermName": "expression assay",
    #     "CellularComponentID": "GO:0005737",
    #     "CellularComponentTerm": "cytoplasm",
    #     "CellularComponentQualifierIDs": None,
    #     "CellularComponentQualifierTermNames": None,
    #     "SubStructureID": None,
    #     "SubStructureName": None,
    #     "SubStructureQualifierIDs": None,
    #     "SubStructureQualifierTermNames": None,
    #     "AnatomyTermID": None,
    #     "AnatomyTermName": None,
    #     "AnatomyTermQualifierIDs": None,
    #     "AnatomyTermQualifierTermNames": None,
    #     "SourceURL": None,
    #     "Source": "RGD",
    #     "Reference": ["PMID:11870221"]
    # }
    raise NotImplementedError


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
    associations = [
        association
        for association in rattus
        if isinstance(association, GeneToExpressionSiteAssociation)
    ]
    assert associations[0].subject == "RGD:619834"
    assert associations[0].predicate == "biolink:expressed_in"
    assert associations[0].object == "GO:0005737"
    assert associations[0].relation == "RO:0002206"
    assert associations[0].publications[0] == "PMID:11870221"
    assert "MMO:0000640" in associations[0].has_evidence
    assert associations[0].source == "infores:rgd"


# Mouse seems to have gene expression in bulk anatomical structures
@pytest.fixture
def mgi_row():
    return {
        "Species": "Mus musculus",
        "SpeciesID": "NCBITaxon:10090",
        "GeneID": "MGI:101757",
        "GeneSymbol": "Cfl1",
        "Location": "upper leg muscle",
        "StageTerm": "TS27",
        "AssayID": "MMO:0000647",
        "AssayTermName": "Northern blot assay",
        "CellularComponentID": None,
        "CellularComponentTerm": None,
        "CellularComponentQualifierIDs": None,
        "CellularComponentQualifierTermNames": None,
        "SubStructureID": None,
        "SubStructureName": None,
        "SubStructureQualifierIDs": None,
        "SubStructureQualifierTermNames": None,
        "AnatomyTermID": "EMAPA:19144",
        "AnatomyTermName": "upper leg muscle",
        "AnatomyTermQualifierIDs": None,
        "AnatomyTermQualifierTermNames": None,
        "SourceURL": ["http://www.informatics.jax.org/assay/MGI:6726480"],
        "Source": "MGI",
        "Reference": ["PMID:10813634"]
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
    assert associations[0].subject == "MGI:101757"
    assert associations[0].predicate == "biolink:expressed_in"
    assert associations[0].object == "EMAPA:19144"
    assert associations[0].relation == "RO:0002206"
    assert associations[0].stage_qualifier == "MGI:TS27"
    assert associations[0].publications[0] == "PMID:10813634"
    assert "MMO:0000647" in associations[0].has_evidence
    assert "http://www.informatics.jax.org/assay/MGI:6726480" in associations[0].has_evidence
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
              "crossReference": {
                "id": "ZFIN:ZDB-PUB-080616-21",
                "pages": ["reference"]
              },
              "publicationId": "PMID:18544660"
            },
            "crossReference": {
              "id": "ZFIN:ZDB-FIG-080908-4",
              "pages": ["gene/expression/annotation/detail"]
            },
            "assay": "MMO:0000655",
            "whenExpressed": {
              "stageName": "Larval:Protruding-mouth",
              "stageTermId": "ZFS:0000035",
              "stageUberonSlimTerm": {
                "uberonTerm": "post embryonic, pre-adult"
              }
            },
            "whereExpressed": {
              "whereExpressedStatement": "whole organism",
              "anatomicalStructureTermId": "ZFA:0001094",
              "anatomicalStructureUberonSlimTermIds": [{
                "uberonTerm": "Other"
              }]
            }
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
    assert associations[0].publications[0] == "PMID:18544660"
    assert "MMO:0000655" in associations[0].has_evidence
    assert "ZFIN:ZDB-FIG-080908-4" in associations[0].has_evidence
    assert "infores:zfin" in associations[0].provided_by
    assert associations[0].source == "infores:zfin"


# Drosophila has some embryonic staged gene expression associations with anatomical entities
@pytest.fixture
def fly_row():
    return {
        "Species": "Drosophila melanogaster",
        "SpeciesID": "NCBITaxon:7227",
        "GeneID": "FB:FBgn0000251",
        "GeneSymbol": "cad",
        "Location": "ventral ectoderm anlage: anlage in statu nascendi",
        "StageTerm": "embryonic stage 4",
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
        "AnatomyTermID": "FBbt:00004204",
        "AnatomyTermName": "ventral ectoderm anlage",
        "AnatomyTermQualifierIDs": None,
        "AnatomyTermQualifierTermNames": None,
        "SourceURL": None,
        "Source": "FB",
        "Reference": ["FB:FBrf0219073"]
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
    assert associations[0].subject == "FB:FBgn0000251"
    assert associations[0].predicate == "biolink:expressed_in"
    assert associations[0].object == "FBbt:00004204"
    assert associations[0].relation == "RO:0002206"
    assert associations[0].stage_qualifier == "FB:embryonic_stage_4"
    assert associations[0].publications[0] == "FB:FBrf0219073"
    assert "MMO:0000658" in associations[0].has_evidence
    assert associations[0].source == "infores:flybase"


# Caenorhabditis elegans
@pytest.fixture
def worm_row():
    return {
        "Species": "Caenorhabditis elegans",
        "SpeciesID": "NCBITaxon:6239",
        "GeneID": "WB:WBGene00000001",
        "GeneSymbol": "aap-1",
        "Location": "C. elegans Cell and Anatomy",
        "StageTerm": "L4 larva Ce",
        "AssayID": "MMO:0000670",
        "AssayTermName": "in situ reporter assay",
        "CellularComponentID": None,
        "CellularComponentTerm": None,
        "CellularComponentQualifierIDs": None,
        "CellularComponentQualifierTermNames": None,
        "SubStructureID": None,
        "SubStructureName": None,
        "SubStructureQualifierIDs": None,
        "SubStructureQualifierTermNames": None,
        "AnatomyTermID": "WBbt:0000100",
        "AnatomyTermName": "C. elegans anatomical entity",
        "AnatomyTermQualifierIDs": None,
        "AnatomyTermQualifierTermNames": None,
        "SourceURL": ["https://www.wormbase.org/species/all/expr_pattern/Expr2275"],
        "Source": "WB",
        "Reference": ["PMID:12393910"]
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


def test_worm_association_publication(worm):
    associations = [
        association
        for association in worm
        if isinstance(association, GeneToExpressionSiteAssociation)
    ]
    assert associations[0].subject == "WB:WBGene00000001"
    assert associations[0].predicate == "biolink:expressed_in"
    assert associations[0].object == "WBbt:0000100"
    assert associations[0].relation == "RO:0002206"
    assert associations[0].stage_qualifier == "WB:L4_larva_Ce"
    assert associations[0].publications[0] == "PMID:12393910"
    assert "MMO:0000670" in associations[0].has_evidence
    assert "https://www.wormbase.org/species/all/expr_pattern/Expr2275" in associations[0].has_evidence
    assert associations[0].source == "infores:wormbase"


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
    assert associations[0].object == "GO:0005737"
    assert associations[0].relation == "RO:0002206"
    assert associations[0].publications[0] == "PMID:14562095"
    assert "MMO:0000662" in associations[0].has_evidence
    assert associations[0].source == "infores:sgd"
