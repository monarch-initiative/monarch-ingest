import pytest
from biolink_model.datamodel.pydanticmodel_v2 import Gene
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../../src'))
from monarch_ingest.ingests.dictybase.gene import transform_record


@pytest.fixture
def basic_dictybase_1():
    """
    Test Dictybase Gene ingest with mock data.
    """
    row = {"GENE ID": "DDB_G0269222", "Gene Name": "gefB", "Synonyms": "RasGEFB, RasGEF"}
    return transform_record(None, row)


def test_dictybase_ncbi_mapped_gene_ingest(basic_dictybase_1):
    entity = [entity for entity in basic_dictybase_1 if isinstance(entity, Gene)]
    assert len(entity) == 1

    assert entity[0]
    assert entity[0].id == "dictyBase:DDB_G0269222"
    assert entity[0].symbol == "gefB"
    assert entity[0].name == "gefB"
    assert "RasGEFB" in entity[0].synonym
    assert "RasGEF" in entity[0].synonym
    assert "NCBITaxon:44689" in entity[0].in_taxon
    assert "infores:dictybase" in entity[0].provided_by
