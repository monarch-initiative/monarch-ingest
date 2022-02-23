import pytest
from biolink_model_pydantic.model import (
    Gene,
    NamedThingToInformationContentEntityAssociation,
    Publication,
)

pubmed_ids = (
    "11217851|12466851|18163442|21267068|19213785|27357688|27914912|21873635|31504408"
)
markers = "Cbe1|Smrp1"


@pytest.fixture
def source_name():
    return "mgi_gene_to_publication"


@pytest.fixture
def script():
    return "./monarch_ingest/mgi/gene_to_publication.py"


@pytest.fixture
def basic_row():
    return {
        "MGI Marker Accession ID": "MGI:1920971",
        "Marker Symbol": "1110017D15Rik",
        "Marker Name": "RIKEN cDNA 1110017D15 gene",
        "Marker Synonyms": markers,
        "PubMed IDs": pubmed_ids,
    }


@pytest.fixture
def basic_entities(mock_koza, source_name, basic_row, script, global_table):
    return mock_koza(
        source_name,
        iter([basic_row]),
        script,
        global_table=global_table,
    )


def test_gene(basic_entities):
    print("basic_entities: ", basic_entities)
    gene = [entity for entity in basic_entities if isinstance(entity, Gene)][0]
    assert gene.id == "MGI:1920971"


def test_pub(basic_entities):
    pub = [entity for entity in basic_entities if isinstance(entity, Publication)][0]
    assert str(pub.id)[5:] in pubmed_ids


def test_association(basic_entities):
    association = [
        entity
        for entity in basic_entities
        if isinstance(entity, NamedThingToInformationContentEntityAssociation)
    ][0]
    assert association.subject == "MGI:1920971"
    assert association.object == "PMID:31504408"
