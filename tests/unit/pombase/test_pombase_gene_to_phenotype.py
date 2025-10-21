import pytest
from biolink_model.datamodel.pydanticmodel_v2 import GeneToPhenotypicFeatureAssociation
from koza import KozaTransform
from koza.io.writer.passthrough_writer import PassthroughWriter

from monarch_ingest.ingests.pombase.gene_to_phenotype import transform_record


@pytest.fixture
def pombase_row():
    return {
        "Database name": "PomBase",
        "Gene systematic ID": "SPAC24B11.06c",
        "FYPO ID": "FYPO:0004058",
        "Allele description": "",
        "Expression": "",
        "Parental strain": "972 h-",
        "Strain name (background)": "",
        "Genotype description": "",
        "Gene symbol": "sty1",
        "Allele name": "sty1delta",
        "Allele synonym": "",
        "Allele type": "deletion",
        "Evidence": "cell growth assay evidence",
        "Condition": "",
        "Penetrance": "",
        "Severity": "FYPO_EXT:0000001",
        "Extension": "",
        "Reference": "PMID:19436749",
        "Taxon": "4896",
        "Date": "2014-11-21",
        "Ploidy": "haploid"
    }


@pytest.fixture
def entities(pombase_row):
    koza_transform = KozaTransform(
        mappings={},
        writer=PassthroughWriter(),
        extra_fields={}
    )
    return transform_record(koza_transform, pombase_row)


@pytest.mark.parametrize("cls", [GeneToPhenotypicFeatureAssociation])
def test_confirm_one_of_each_classes(cls, entities):
    class_entities = [entity for entity in entities if isinstance(entity, cls)]
    assert class_entities
    assert len(class_entities) == 1
    assert class_entities[0]


def test_pombase_g2p_association_publication(entities):
    association = [
        association for association in entities if isinstance(association, GeneToPhenotypicFeatureAssociation)
    ][0]
    assert association.subject == "PomBase:SPAC24B11.06c"
    assert association.predicate == "biolink:has_phenotype"
    assert association.object == "FYPO:0004058"
    assert association.publications[0] == "PMID:19436749"
    assert association.primary_knowledge_source == "infores:pombase"
    assert "infores:monarchinitiative" in association.aggregator_knowledge_source


def test_pombase_conditions(pombase_row):
    pombase_row["Condition"] = "glucose,ethanol"
    koza_transform = KozaTransform(
        mappings={},
        writer=PassthroughWriter(),
        extra_fields={}
    )
    entities = transform_record(koza_transform, pombase_row)
    association = [
        association for association in entities if isinstance(association, GeneToPhenotypicFeatureAssociation)
    ][0]
    assert "glucose" in association.qualifiers
    assert "ethanol" in association.qualifiers
