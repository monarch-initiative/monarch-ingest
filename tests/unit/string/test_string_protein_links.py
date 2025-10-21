"""
Unit tests for STRING protein links ingest
"""

import pytest
from biolink_model.datamodel.pydanticmodel_v2 import PairwiseGeneToGeneInteraction
from koza import KozaTransform
from koza.io.writer.passthrough_writer import PassthroughWriter

from monarch_ingest.ingests.string.protein_links import transform_record


@pytest.fixture
def entrez_mapping():
    """
    Mock STRING to entrez mapping for testing.
    """
    return {
        "10090.ENSMUSP00000000001": {"entrez": "14679"},
        "10090.ENSMUSP00000020316": {"entrez": "56480"},
        "9606.ENSP00000349467": {"entrez": "801|805|808"},
        "9606.ENSP00000000233": {"entrez": "123|381"},
    }


@pytest.fixture
def basic_row():
    """
    Test STRING protein links data row.
    """
    return {
        "protein1": "10090.ENSMUSP00000000001",
        "protein2": "10090.ENSMUSP00000020316",
        "neighborhood": "0",
        "fusion": "0",
        "cooccurence": "0",
        "coexpression": "116",
        "experimental": "90",
        "database": "0",
        "textmining": "67",
        "combined_score": "183",
    }


@pytest.fixture
def inverse_duplicate_rows():
    return [
        {
            "protein1": "10090.ENSMUSP00000000001",
            "protein2": "10090.ENSMUSP00000020316",
            "neighborhood": "0",
            "fusion": "0",
            "cooccurence": "0",
            "coexpression": "116",
            "experimental": "90",
            "database": "0",
            "textmining": "67",
            "combined_score": "183",
        },
        {
            "protein1": "10090.ENSMUSP00000020316",
            "protein2": "10090.ENSMUSP00000000001",
            "neighborhood": "0",
            "fusion": "0",
            "cooccurence": "0",
            "coexpression": "116",
            "experimental": "90",
            "database": "0",
            "textmining": "67",
            "combined_score": "183",
        },
    ]


@pytest.fixture
def basic_pl(basic_row, entrez_mapping):
    """
    Mock Koza run for STRING protein links ingest.
    """
    koza_transform = KozaTransform(
        mappings={"entrez_2_string": entrez_mapping},
        writer=PassthroughWriter(),
        extra_fields={}
    )
    return transform_record(koza_transform, basic_row)


@pytest.fixture
def duplicate_row_entities(inverse_duplicate_rows, entrez_mapping):
    """
    Process inverse duplicate rows to test deduplication.
    """
    koza_transform = KozaTransform(
        mappings={"entrez_2_string": entrez_mapping},
        writer=PassthroughWriter(),
        extra_fields={}
    )

    results = []
    for row in inverse_duplicate_rows:
        result = transform_record(koza_transform, row)
        if result:
            results.extend(result)
    return results


INCLUDED_ECO_CODES = ["ECO:0000075", "ECO:0000006", "ECO:0007833"]
EXCLUDED_ECO_CODES = ["ECO:0000044", "ECO:0000124", "ECO:0000080", "ECO:0007636"]


def test_association(basic_pl):
    association = basic_pl[0]
    assert association
    assert isinstance(association, PairwiseGeneToGeneInteraction)
    assert association.subject == "NCBIGene:14679"
    assert association.object == "NCBIGene:56480"
    assert association.predicate == "biolink:interacts_with"
    assert association.primary_knowledge_source == "infores:string"
    assert association.has_evidence
    assert all([eco_code in INCLUDED_ECO_CODES for eco_code in association.has_evidence])
    assert all([eco_code not in EXCLUDED_ECO_CODES for eco_code in association.has_evidence])
    assert "infores:monarchinitiative" in association.aggregator_knowledge_source


@pytest.fixture
def multigene_row():
    return {
        "protein1": "9606.ENSP00000000233",
        "protein2": "9606.ENSP00000349467",
        "neighborhood": "0",
        "fusion": "0",
        "cooccurence": "332",
        "coexpression": "62",
        "experimental": "77",
        "database": "0",
        "textmining": "101",
        "combined_score": 410,
    }


@pytest.fixture
def multigene_entities(multigene_row, entrez_mapping):
    koza_transform = KozaTransform(
        mappings={"entrez_2_string": entrez_mapping},
        writer=PassthroughWriter(),
        extra_fields={}
    )
    return transform_record(koza_transform, multigene_row)


def test_multigene_associations(multigene_entities):
    associations = [
        association for association in multigene_entities if isinstance(association, PairwiseGeneToGeneInteraction)
    ]
    assert len(associations) == 6


def test_duplicates_are_removed(duplicate_row_entities):
    associations = [
        association for association in duplicate_row_entities if isinstance(association, PairwiseGeneToGeneInteraction)
    ]
    assert len(associations) == 1
