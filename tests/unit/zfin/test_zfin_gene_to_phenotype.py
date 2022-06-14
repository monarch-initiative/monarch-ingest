import pytest


@pytest.fixture
def source_name():
    return "zfin_gene_to_phenotype"


@pytest.fixture
def script():
    return "./monarch_ingest/ingests/zfin/gene_to_phenotype.py"


@pytest.fixture
def map_cache():
    eqe2zp = {
        "0-0-ZFA:0000042-PATO:0000638-0-0-0": {"iri": "ZP:0004225"},
        "BSPO:0000112-BFO:0000050-ZFA:0000042-PATO:0000638-0-0-0": {"iri": "ZP:0011243"},
        "BSPO:0000000-BFO:0000050-ZFA:0000823-PATO:0000642-BSPO:0000007-BFO:0000050-ZFA:0000823": {
            "iri": "ZP:0000157"
        },
    }
    return {"eqe2zp": eqe2zp}


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
def basic_g2p(mock_koza, source_name, basic_row, script, map_cache, global_table):
    return mock_koza(
        source_name,
        iter([basic_row]),
        script,
        map_cache=map_cache,
        global_table=global_table,
    )


# def test_gene(basic_g2p):
#     gene = basic_g2p[0]
#     assert gene
#     assert gene.id == "ZFIN:ZDB-GENE-990415-8"


# def test_phenotypic_feature(basic_g2p):
#     phenotypic_feature = basic_g2p[1]
#     assert phenotypic_feature
#     assert phenotypic_feature.id == "ZP:0004225"


def test_association(basic_g2p):
    association = basic_g2p[0]
    assert association
    assert association.subject == "ZFIN:ZDB-GENE-990415-8"
    assert association.object == "ZP:0004225"
    assert association.publications
    assert association.publications[0] == "ZFIN:ZDB-PUB-970210-19"
    assert association.primary_knowledge_source == "infores:zfin"
    assert "infores:monarchinitiative" in association.aggregator_knowledge_source

# @pytest.fixture
# def postcomposed(mock_koza, source_name, basic_row, script, map_cache, global_table):

#     basic_row["Affected Structure or Process 1 subterm ID"] = "BSPO:0000112"
#     basic_row["Post-composed Relationship ID"] = "BFO:0000050"
#     basic_row["Affected Structure or Process 1 superterm ID"] = "ZFA:0000042"

#     return mock_koza(
#         source_name,
#         iter([basic_row]),
#         script,
#         map_cache=map_cache,
#         global_table=global_table,
#     )


# def test_postcomposed(postcomposed):
#     phenotypic_feature = postcomposed[1]
#     assert phenotypic_feature.id == "ZP:0011243"


# @pytest.fixture
# def double_postcomposed(
#     mock_koza, source_name, basic_row, script, map_cache, global_table
# ):

#     basic_row["Affected Structure or Process 1 subterm ID"] = "BSPO:0000000"
#     basic_row["Post-composed Relationship ID"] = "BFO:0000050"
#     basic_row["Affected Structure or Process 1 superterm ID"] = "ZFA:0000823"
#     basic_row["Phenotype Keyword ID"] = "PATO:0000642"
#     basic_row["Affected Structure or Process 2 subterm ID"] = "BSPO:0000007"
#     basic_row["Post-composed Relationship (rel) ID"] = "BFO:0000050"
#     basic_row["Affected Structure or Process 2 superterm ID"] = "ZFA:0000823"

#     return mock_koza(
#         source_name,
#         iter([basic_row]),
#         script,
#         map_cache=map_cache,
#         global_table=global_table,
#     )


# def test_double_postcomposed(double_postcomposed):
#     phenotypic_feature = double_postcomposed[1]
#     assert phenotypic_feature.id == "ZP:0000157"


@pytest.mark.parametrize("tag", ["normal", "exacerbated", "ameliorated"])
def test_excluded_tags(
    mock_koza, source_name, basic_row, script, map_cache, tag, global_table
):
    basic_row["Phenotype Tag"] = tag
    entities = mock_koza(
        source_name,
        iter([basic_row]),
        script,
        map_cache=map_cache,
        global_table=global_table,
    )
    assert len(entities) == 0


@pytest.mark.parametrize("tag", ["abnormal"])
def test_included_tags(
    mock_koza, source_name, basic_row, script, map_cache, tag, global_table
):
    basic_row["Phenotype Tag"] = tag
    entities = mock_koza(
        source_name,
        iter([basic_row]),
        script,
        map_cache=map_cache,
        global_table=global_table,
    )
    assert len(entities) == 1
