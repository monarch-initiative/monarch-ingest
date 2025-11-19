"""
Unit tests for Xenbase Gene Orthology relationships ingest
"""

import pytest
from biolink_model.datamodel.pydanticmodel_v2 import GeneToGeneHomologyAssociation
from koza import KozaTransform
from koza.io.writer.passthrough_writer import PassthroughWriter

from monarch_ingest.ingests.xenbase.non_entrez_orthologs import transform_record


@pytest.fixture
def xenbase_row():
    return {
        "Xenbase": "XB-GENE-6485390",
        "OMIM": "614812",
        "MGI": "1891834",
        "ZFIN": "ZDB-GENE-070705-255",
    }


@pytest.fixture
def ne_orthology_records(xenbase_row):
    koza_transform = KozaTransform(
        mappings={},
        writer=PassthroughWriter(),
        extra_fields={}
    )
    return transform_record(koza_transform, xenbase_row)


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
