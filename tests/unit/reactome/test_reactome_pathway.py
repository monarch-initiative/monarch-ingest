"""
Unit tests for Reactome pathway ingest
"""

import pytest
from biolink_model.datamodel.pydanticmodel_v2 import Pathway
from koza import KozaTransform
from koza.io.writer.passthrough_writer import PassthroughWriter

from monarch_ingest.ingests.reactome.pathway import transform_record


@pytest.fixture
def basic_row():
    return {"ID": "R-BTA-73843", "Name": "5-Phosphoribose 1-diphosphate biosynthesis", "species": "Bos taurus"}


@pytest.fixture
def basic_pathway(basic_row):
    koza_transform = KozaTransform(
        mappings={},
        writer=PassthroughWriter(),
        extra_fields={}
    )
    return transform_record(koza_transform, basic_row)


def test_pathway_id(basic_pathway):
    pathway = basic_pathway[0]
    assert isinstance(pathway, Pathway)
    assert pathway.id == "Reactome:R-BTA-73843"
    assert "infores:reactome" in pathway.provided_by
