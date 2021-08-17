import pytest
from biolink_model_pydantic.model import (
    Gene,
    GeneToPhenotypicFeatureAssociation,
    PhenotypicFeature,
)
from koza.koza_runner import get_translation_table


@pytest.fixture
def entities(mock_koza):
    row = iter(
        [
            {
                "Database name": "PomBase",
                "Gene systematic ID": "SPAC24B11.06c",
                "FYPO ID": "FYPO:0004058",
                "Allele description": "",
                "Expression": "",
                "Parental strain": "972 h-",
                "Strain name (background)": "",
                "Genotype description": "",
                "Gene name": "sty1",
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
            }
        ]
    )
    tt = get_translation_table("monarch_ingest/translation_table.yaml", None)

    return mock_koza(
        "gene-to-phenotype",
        row,
        "./monarch_ingest/pombase/gene2phenotype.py",
        translation_table=tt,
    )


# TODO: can this test be shared across all g2p loads?
@pytest.mark.parametrize(
    "cls", [Gene, PhenotypicFeature, GeneToPhenotypicFeatureAssociation]
)
def confirm_one_of_each_classes(cls, entities):
    class_entities = [entity for entity in entities if isinstance(entity, cls)]
    assert class_entities
    assert len(class_entities) == 1
    assert class_entities[0]


def test_pombase_g2p_association_publication(entities):
    associations = [
        association
        for association in entities
        if isinstance(association, GeneToPhenotypicFeatureAssociation)
    ]
    assert associations[0].publications[0] == "PMID:19436749"
