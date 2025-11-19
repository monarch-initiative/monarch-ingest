import pytest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../../src'))
from biolink_model.datamodel.pydanticmodel_v2 import Gene, GeneToPhenotypicFeatureAssociation, PhenotypicFeature
from monarch_ingest.ingests.xenbase.gene_to_phenotype import transform_record


@pytest.fixture
def entities():
    row = {
        "SUBJECT": "Xenbase:XB-GENE-1000632",
        "SUBJECT_LABEL": "dctn2",
        "SUBJECT_TAXON": "NCBITaxon:8364",
        "SUBJECT_TAXON_LABEL": "Xla",
        "OBJECT": "XPO:0102358",
        "OBJECT_LABEL": "abnormal tail morphology",
        "RELATION": "RO_0002200",
        "RELATION_LABEL": "has_phenotype",
        "EVIDENCE": "",
        "EVIDENCE_LABEL": "",
        "SOURCE": "PMID:17112317",
        "IS_DEFINED_BY": "",
        "QUALIFIER": "",
    }
    return transform_record(None, row)


def test_gene2_phenotype_transform(entities):
    assert entities
    assert len(entities) == 3  # gene, phenotype, association
    association = [entity for entity in entities if isinstance(entity, GeneToPhenotypicFeatureAssociation)][0]
    assert association.primary_knowledge_source == "infores:xenbase"
    assert "infores:monarchinitiative" in association.aggregator_knowledge_source


# TODO: can this test be shared across all g2p loads?
@pytest.mark.parametrize("cls", [Gene, PhenotypicFeature, GeneToPhenotypicFeatureAssociation])
def confirm_one_of_each_classes(cls, entities):
    class_entities = [entity for entity in entities if isinstance(entity, cls)]
    assert class_entities
    assert len(class_entities) == 1
    assert class_entities[0]


def test_gene2_phenotype_transform_publications(entities):
    association = [entity for entity in entities if isinstance(entity, GeneToPhenotypicFeatureAssociation)][0]
    assert association.publications[0] == "PMID:17112317"
    assert association.primary_knowledge_source == "infores:xenbase"
    assert "infores:monarchinitiative" in association.aggregator_knowledge_source
