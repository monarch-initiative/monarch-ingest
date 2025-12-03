"""
Unit tests for ZFIN Gene to Phenotype ingest
"""

import pytest
from biolink_model.datamodel.pydanticmodel_v2 import GeneToPhenotypicFeatureAssociation
from koza import KozaTransform
from koza.io.writer.passthrough_writer import PassthroughWriter

from monarch_ingest.ingests.zfin.gene_to_phenotype import transform_record


@pytest.fixture
def eqe2zp_mapping():
    """
    Mock eqe2zp mapping for testing.
    Keys are EQE concatenations, values are dicts with 'iri' field.
    """
    return {
        "0-0-ZFA:0000042-PATO:0000638-0-0-0": {"iri": "ZP:0004225"},
        "BSPO:0000112-BFO:0000050-ZFA:0000042-PATO:0000638-0-0-0": {"iri": "ZP:0011243"},
        "BSPO:0000000-BFO:0000050-ZFA:0000823-PATO:0000642-BSPO:0000007-BFO:0000050-ZFA:0000823": {"iri": "ZP:0000157"},
    }


@pytest.fixture
def basic_row():
    return {
        "ID": "341492416",
        "Gene Symbol": "pax2a",
        "Gene ID": "ZDB-GENE-990415-8",
        "Affected Structure or Process 1 subterm ID": "",
        "Affected Structure or Process 1 subterm Name": "",
        "Post-composed Relationship ID": "",
        "Post-composed Relationship Name": "",
        "Affected Structure or Process 1 superterm ID": "ZFA:0000042",
        "Affected Structure or Process 1 superterm Name": "midbrain hindbrain boundary",
        "Phenotype Keyword ID": "PATO:0000638",
        "Phenotype Keyword Name": "apoptotic",
        "Phenotype Tag": "abnormal",
        "Affected Structure or Process 2 subterm ID": "",
        "Affected Structure or Process 2 subterm name": "",
        "Post-composed Relationship (rel) ID": "",
        "Post-composed Relationship (rel) Name": "",
        "Affected Structure or Process 2 superterm ID": "",
        "Affected Structure or Process 2 superterm name": "",
        "Fish ID": "ZDB-FISH-150901-29679",
        "Fish Display Name": "pax2a<sup>th44/th44</sup>",
        "Start Stage ID": "ZDB-STAGE-010723-13",
        "End Stage ID": "ZDB-STAGE-010723-13",
        "Fish Environment ID": "ZDB-GENOX-041102-1385",
        "Publication ID": "ZDB-PUB-970210-19",
        "Figure ID": "ZDB-FIG-120307-8",
    }


@pytest.fixture
def basic_g2p(basic_row, eqe2zp_mapping):
    koza_transform = KozaTransform(
        mappings={"eqe2zp": eqe2zp_mapping},
        writer=PassthroughWriter(),
        extra_fields={}
    )
    return transform_record(koza_transform, basic_row)


def test_association(basic_g2p):
    assert len(basic_g2p) > 0
    association = basic_g2p[0]
    assert association
    assert isinstance(association, GeneToPhenotypicFeatureAssociation)
    assert association.subject == "ZFIN:ZDB-GENE-990415-8"
    assert association.object == "ZP:0004225"
    assert association.publications
    assert association.publications[0] == "ZFIN:ZDB-PUB-970210-19"
    assert association.primary_knowledge_source == "infores:zfin"
    assert "infores:monarchinitiative" in association.aggregator_knowledge_source


@pytest.fixture
def postcomposed_row(basic_row):
    basic_row["Affected Structure or Process 1 subterm ID"] = "BSPO:0000112"
    basic_row["Post-composed Relationship ID"] = "BFO:0000050"
    basic_row["Affected Structure or Process 1 superterm ID"] = "ZFA:0000042"
    return basic_row


@pytest.fixture
def postcomposed(postcomposed_row, eqe2zp_mapping):
    koza_transform = KozaTransform(
        mappings={"eqe2zp": eqe2zp_mapping},
        writer=PassthroughWriter(),
        extra_fields={}
    )
    return transform_record(koza_transform, postcomposed_row)


def test_postcomposed(postcomposed):
    assert len(postcomposed) > 0
    association = postcomposed[0]
    assert association.object == "ZP:0011243"


@pytest.fixture
def double_postcomposed_row(basic_row):
    basic_row["Affected Structure or Process 1 subterm ID"] = "BSPO:0000000"
    basic_row["Post-composed Relationship ID"] = "BFO:0000050"
    basic_row["Affected Structure or Process 1 superterm ID"] = "ZFA:0000823"
    basic_row["Phenotype Keyword ID"] = "PATO:0000642"
    basic_row["Affected Structure or Process 2 subterm ID"] = "BSPO:0000007"
    basic_row["Post-composed Relationship (rel) ID"] = "BFO:0000050"
    basic_row["Affected Structure or Process 2 superterm ID"] = "ZFA:0000823"
    return basic_row


@pytest.fixture
def double_postcomposed(double_postcomposed_row, eqe2zp_mapping):
    koza_transform = KozaTransform(
        mappings={"eqe2zp": eqe2zp_mapping},
        writer=PassthroughWriter(),
        extra_fields={}
    )
    return transform_record(koza_transform, double_postcomposed_row)


def test_double_postcomposed(double_postcomposed):
    assert len(double_postcomposed) > 0
    association = double_postcomposed[0]
    assert association.object == "ZP:0000157"


@pytest.mark.parametrize("tag", ["normal", "exacerbated", "ameliorated"])
def test_excluded_tags(basic_row, eqe2zp_mapping, tag):
    basic_row["Phenotype Tag"] = tag
    koza_transform = KozaTransform(
        mappings={"eqe2zp": eqe2zp_mapping},
        writer=PassthroughWriter(),
        extra_fields={}
    )
    entities = transform_record(koza_transform, basic_row)
    assert len(entities) == 0


@pytest.mark.parametrize("tag", ["abnormal"])
def test_included_tags(basic_row, eqe2zp_mapping, tag):
    basic_row["Phenotype Tag"] = tag
    koza_transform = KozaTransform(
        mappings={"eqe2zp": eqe2zp_mapping},
        writer=PassthroughWriter(),
        extra_fields={}
    )
    entities = transform_record(koza_transform, basic_row)
    assert len(entities) == 1
