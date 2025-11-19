from typing import List

import pytest
from biolink_model.datamodel.pydanticmodel_v2 import Gene
from koza.io.writer.writer import KozaWriter
from koza.runner import KozaRunner, KozaTransformHooks
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../../src'))
from monarch_ingest.ingests.dictybase.gene import transform_record


class MockWriter(KozaWriter):
    def __init__(self):
        self.items = []

    def write(self, entities):
        self.items += entities

    def finalize(self):
        pass


@pytest.fixture
def basic_dictybase_1():
    """
    Test Dictybase Gene ingest with mock data.
    """
    row = {"GENE ID": "DDB_G0269222", "Gene Name": "gefB", "Synonyms": "RasGEFB, RasGEF"}

    writer = MockWriter()
    runner = KozaRunner(data=iter([row]), writer=writer, hooks=KozaTransformHooks(transform_record=[transform_record]))
    runner.run()
    return writer.items


def test_dictybase_ncbi_mapped_gene_ingest(basic_dictybase_1):
    entity: List[Gene] = [entity for entity in basic_dictybase_1 if isinstance(entity, Gene)]
    assert len(entity) == 1

    assert entity[0]
    assert entity[0].id == "dictyBase:DDB_G0269222"
    assert entity[0].symbol == "gefB"
    assert entity[0].name == "gefB"
    assert "RasGEFB" in entity[0].synonym
    assert "RasGEF" in entity[0].synonym
    assert "NCBITaxon:44689" in entity[0].in_taxon
    assert "infores:dictybase" in entity[0].provided_by
