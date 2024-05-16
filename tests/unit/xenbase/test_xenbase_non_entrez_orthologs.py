"""
Unit tests for Xenbase Gene Orthology relationships ingest
"""

import pytest
from biolink_model.datamodel.pydanticmodel_v2 import GeneToGeneHomologyAssociation
from koza.utils.testing_utils import mock_koza  # noqa: F401


@pytest.fixture
def source_name():
    """
    :return: string source name of Xenbase Gene Orthology relationships ingest
    """
    return "xenbase_non_entrez_orthologs"


@pytest.fixture
def script():
    """
    :return: string path to Xenbase Gene Orthology relationships ingest script
    """
    return "./src/monarch_ingest/ingests/xenbase/non_entrez_orthologs.py"


@pytest.fixture
def ne_orthology_records(mock_koza, source_name, script):
    row = {
        "Xenbase": "XB-GENE-6485390",
        "OMIM": "614812",
        "MGI": "1891834",
        "ZFIN": "ZDB-GENE-070705-255",
    }
    return mock_koza(name=source_name, data=row, transform_code=script)


def test_ne_orthology_records(ne_orthology_records):
    assert ne_orthology_records
    for association in ne_orthology_records:
        assert isinstance(association, GeneToGeneHomologyAssociation)
        assert association.subject == "Xenbase:XB-GENE-6485390"
        assert association.predicate == "biolink:orthologous_to"

        # not sure of ordering of associations,
        # but the association.object should be one of these...
        assert association.object in ["OMIM:614812", "MGI:1891834", "ZFIN:ZDB-GENE-070705-255"]

        assert association.primary_knowledge_source == "infores:xenbase"
        assert "infores:monarchinitiative" in association.aggregator_knowledge_source
