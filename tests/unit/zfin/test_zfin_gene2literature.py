import pytest
from biolink_model_pydantic.model import (
    Gene,
    NamedThingToInformationContentEntityAssociation,
    Publication,
)
from koza.cli_runner import get_translation_table


@pytest.fixture
def basic_row():
    return {
        "Gene Symbol": "si:dkey-84j12.1",
        "Gene ID": "ZDB-GENE-060526-342",
        "Publication ID": "ZDB-PUB-140801-12",
        "Publication Type": "Journal",
        "PubMed ID": "25078621",
    }


@pytest.fixture
def basic_entities(mock_koza, basic_row):
    return mock_koza(
        "gene-to-publication",
        iter([basic_row]),
        "./monarch_ingest/zfin/gene2publication.py",
        translation_table=get_translation_table("monarch_ingest/translation_table.yaml", None),
    )


def test_gene(basic_entities):
    gene = [entity for entity in basic_entities if isinstance(entity, Gene)][0]
    assert gene.id == "ZFIN:ZDB-GENE-060526-342"


def test_pub(basic_entities):
    pub = [entity for entity in basic_entities if isinstance(entity, Publication)][0]
    assert pub.id == "ZFIN:ZDB-PUB-140801-12"


def test_association(basic_entities):
    association = [
        entity
        for entity in basic_entities
        if isinstance(entity, NamedThingToInformationContentEntityAssociation)
    ][0]
    assert association.subject == "ZFIN:ZDB-GENE-060526-342"
    assert association.object == "ZFIN:ZDB-PUB-140801-12"
