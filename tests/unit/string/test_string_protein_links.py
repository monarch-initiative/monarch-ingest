import pytest
from koza.koza_runner import get_translation_table


@pytest.fixture
def tt():
    return get_translation_table("monarch_ingest/translation_table.yaml", None)

# This name must match the ingest name in the transform code
@pytest.fixture
def source_name():
    return "something-to-somethingelse"

# This is the location of the transform code
@pytest.fixture
def script():
    return "./monarch_ingest/somethingbase/something2somethingelse.py"


# If the ingest requires a map, it can be created here with just the entries that are required
@pytest.fixture
def map_cache():
    eqe2zp = {
        "0-0-ZFA:0000042-PATO:0000638-0-0-0": {"iri": "ZP:0004225"},
        "BSPO:0000112-BFO:0000050-ZFA:0000042-PATO:0000638-0-0-0": {
            "iri": "ZP:0011243"
        },
        "BSPO:0000000-BFO:0000050-ZFA:0000823-PATO:0000642-BSPO:0000007-BFO:0000050-ZFA:0000823": {
            "iri": "ZP:0000157"
        },
    }
    return {"eqe2zp": eqe2zp}


# Create a fixture for a full row, it should be relatively representative of the rows ingested, and can
# be modified for testing edge cases
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


# This is the outward facing fixture that can be used by individual tests, it will return
# a list of biolink instances
@pytest.fixture
def basic_g2p(mock_koza, source_name, basic_row, script, map_cache, tt):
    return mock_koza(
        source_name,
        iter([basic_row]),
        script,
        map_cache=map_cache,
        translation_table=tt,
    )

# A simple end-to-end test is to confirm that the IDs are set on
def test_gene(basic_g2p):
    gene = basic_g2p[0]
    assert gene
    assert gene.id == "ZFIN:ZDB-GENE-990415-8"


def test_phenotypic_feature(basic_g2p):
    phenotypic_feature = basic_g2p[1]
    assert phenotypic_feature
    assert phenotypic_feature.id == "ZP:0004225"


def test_association(basic_g2p):
    association = basic_g2p[2]
    assert association
    assert association.subject == "ZFIN:ZDB-GENE-990415-8"
    assert association.object == "ZP:0004225"
    assert association.publications
    assert association.publications[0] == "ZFIN:ZDB-PUB-970210-19"


# A that fixture creates entities from a modified row is quick way to test all of
# the paths through the code
@pytest.fixture
def postcomposed(mock_koza, source_name, basic_row, script, map_cache, tt):

    basic_row["Affected Structure or Process 1 subterm ID"] = "BSPO:0000112"
    basic_row["Post-composed Relationship ID"] = "BFO:0000050"
    basic_row["Affected Structure or Process 1 superterm ID"] = "ZFA:0000042"

    return mock_koza(
        source_name,
        iter([basic_row]),
        script,
        map_cache=map_cache,
        translation_table=tt,
    )


def test_postcomposed(postcomposed):
    phenotypic_feature = postcomposed[1]
    assert phenotypic_feature.id == "ZP:0011243"


# To parameterize multiple scenarios, the test can depend directly on the row fixture,
# the entities can be generated within the test and the then the state can be checked
# at the end.
@pytest.mark.parametrize("tag", ["normal", "exacerbated", "ameliorated"])
def test_excluded_tags(mock_koza, source_name, basic_row, script, map_cache, tt, tag):
    basic_row["Phenotype Tag"] = tag
    entities = mock_koza(
        source_name,
        iter([basic_row]),
        script,
        map_cache=map_cache,
        translation_table=tt,
    )
    assert len(entities) == 0

