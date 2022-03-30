import pytest
from biolink_model_pydantic.model import (
    Gene,
    GeneToExpressionSiteAssociation,
    AnatomicalEntity,
    CellularComponent,
    LifeStage
)

from monarch_ingest.alliance.utils import get_life_stage


def test_get_life_stage():
    life_stage = get_life_stage(
        db="ZFIN",
        ncbi_taxon_id="NCBITaxon:7955",
        stage_term="Segmentation:10-13 somites",
        source="infores:zfin"
    )
    assert isinstance(life_stage, LifeStage)
    assert life_stage.id == "ZFIN:Segmentation:10-13_somites"
    assert "NCBITaxon:7955" in life_stage.in_taxon


@pytest.fixture
def source_name():
    return "alliance_gene_to_expression"


@pytest.fixture
def script():
    return "./monarch_ingest/alliance/gene_to_expression.py"


# The Rat data seems to only have gene expression assigned to cellular components
@pytest.fixture
def rat_row():
    return {
        "Species": "Rattus norvegicus",
        "SpeciesID": "NCBITaxon:10116",
        "GeneID": "RGD:619834",
        "GeneSymbol": "A1cf",
        "Location": "cytoplasm",
        "StageTerm": "",
        "AssayID": "MMO:0000640",
        "AssayTermName": "expression assay",
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
        "Source": "RGD",
        "Reference": ["PMID:11870221"]
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


def test_rattus_gene(rattus):
    genes = [gene for gene in rattus if isinstance(gene, Gene)]
    assert genes[0].id == "RGD:619834"
    assert genes[0].name == "A1cf"
    assert "NCBITaxon:10116" in genes[0].in_taxon
    assert genes[0].source == "infores:rgd"


def test_rattus_expression_site(rattus):
    entities = [
        entity for entity in rattus if isinstance(entity, CellularComponent)
    ]
    assert entities[0].id == "GO:0005737"
    assert entities[0].name == "cytoplasm"
    assert "NCBITaxon:10116" in entities[0].in_taxon
    assert entities[0].source == "infores:rgd"


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


def test_mouse_gene(mouse):
    genes = [gene for gene in mouse if isinstance(gene, Gene)]
    assert genes[0].id == "MGI:101757"
    assert genes[0].name == "Cfl1"
    assert "NCBITaxon:10090" in genes[0].in_taxon
    assert genes[0].source == "infores:mgi"


def test_mouse_expression_site(mouse):
    entities = [
        entity for entity in mouse if isinstance(entity, AnatomicalEntity)
    ]
    assert entities[0].id == "EMAPA:19144"
    assert entities[0].name == "upper leg muscle"
    assert "NCBITaxon:10090" in entities[0].in_taxon
    assert entities[0].source == "infores:mgi"


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
    assert associations[0].stage_qualifier.id == "MGI:TS27"
    assert associations[0].publications[0] == "PMID:10813634"
    assert "MMO:0000647" in associations[0].has_evidence
    assert "http://www.informatics.jax.org/assay/MGI:6726480" in associations[0].has_evidence
    assert associations[0].source == "infores:mgi"


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
def zebrafish(zfin_row, mock_koza, source_name, script, global_table):
    rows = iter([zfin_row])
    return mock_koza(
        source_name,
        rows,
        script,
        global_table=global_table,
    )


def test_zebrafish_gene(zebrafish):
    genes = [gene for gene in zebrafish if isinstance(gene, Gene)]
    assert genes[0].id == "ZFIN:ZDB-GENE-010226-1"
    assert genes[0].name == "gdnfa"
    assert "NCBITaxon:7955" in genes[0].in_taxon
    assert genes[0].source == "infores:zfin"


def test_zebrafish_expression_site(zebrafish):
    entities = [
        entity for entity in zebrafish if isinstance(entity, AnatomicalEntity)
    ]
    assert entities[0].id == "ZFA:0001206"
    assert entities[0].name == "intermediate mesoderm"
    assert "NCBITaxon:7955" in entities[0].in_taxon
    assert entities[0].source == "infores:zfin"


def test_zebrafish_association(zebrafish):
    associations = [
        association
        for association in zebrafish
        if isinstance(association, GeneToExpressionSiteAssociation)
    ]
    assert associations[0].subject == "ZFIN:ZDB-GENE-010226-1"
    assert associations[0].predicate == "biolink:expressed_in"
    assert associations[0].object == "ZFA:0001206"
    assert associations[0].relation == "RO:0002206"
    assert associations[0].stage_qualifier.id == "ZFIN:Segmentation:10-13_somites"
    assert associations[0].publications[0] == "PMID:11237470"
    assert "MMO:0000658" in associations[0].has_evidence
    assert "https://zfin.org/ZDB-FIG-110701-1" in associations[0].has_evidence
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


def test_drosophila_gene(drosophila):
    genes = [gene for gene in drosophila if isinstance(gene, Gene)]
    assert genes[0].id == "FB:FBgn0000251"
    assert genes[0].name == "cad"
    assert "NCBITaxon:7227" in genes[0].in_taxon
    assert genes[0].source == "infores:flybase"


def test_drosophila_expression_site(drosophila):
    entities = [
        entity for entity in drosophila if isinstance(entity, AnatomicalEntity)
    ]
    assert entities[0].id == "FBbt:00004204"
    assert entities[0].name == "ventral ectoderm anlage"
    assert "NCBITaxon:7227" in entities[0].in_taxon
    assert entities[0].source == "infores:flybase"


def test_drosophila_association_publication(drosophila):
    associations = [
        association
        for association in drosophila
        if isinstance(association, GeneToExpressionSiteAssociation)
    ]
    assert associations[0].subject == "FB:FBgn0000251"
    assert associations[0].predicate == "biolink:expressed_in"
    assert associations[0].object == "FBbt:00004204"
    assert associations[0].relation == "RO:0002206"
    assert associations[0].stage_qualifier.id == "FB:embryonic_stage_4"
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


def test_worm_gene(worm):
    genes = [gene for gene in worm if isinstance(gene, Gene)]
    assert genes[0].id == "WB:WBGene00000001"
    assert genes[0].name == "aap-1"
    assert "NCBITaxon:6239" in genes[0].in_taxon
    assert genes[0].source == "infores:wormbase"


def test_worm_expression_site(worm):
    entities = [
        entity for entity in worm if isinstance(entity, AnatomicalEntity)
    ]
    assert entities[0].id == "WBbt:0000100"
    assert entities[0].name == "C. elegans anatomical entity"
    assert "NCBITaxon:6239" in entities[0].in_taxon
    assert entities[0].source == "infores:wormbase"


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
    assert associations[0].stage_qualifier.id == "WB:L4_larva_Ce"
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


def test_yeast_gene(yeast):
    genes = [gene for gene in yeast if isinstance(gene, Gene)]
    assert genes[0].id == "SGD:S000002429"
    assert genes[0].name == "ATG31"
    assert "NCBITaxon:559292" in genes[0].in_taxon
    assert genes[0].source == "infores:sgd"


def test_yeast_expression_site(yeast):
    entities = [
        entity for entity in yeast if isinstance(entity, CellularComponent)
    ]
    assert entities[0].id == "GO:0005737"
    assert entities[0].name == "cytoplasm"
    assert "NCBITaxon:559292" in entities[0].in_taxon
    assert entities[0].source == "infores:sgd"


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
