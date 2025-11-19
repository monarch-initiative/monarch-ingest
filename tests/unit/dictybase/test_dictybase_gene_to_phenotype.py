from typing import Dict, List

import pytest
from biolink_model.datamodel.pydanticmodel_v2 import GeneToPhenotypicFeatureAssociation
from koza import KozaTransform
from koza.io.writer.passthrough_writer import PassthroughWriter

from monarch_ingest.ingests.dictybase.gene_to_phenotype import transform_record
from monarch_ingest.ingests.dictybase.utils import parse_phenotypes


@pytest.fixture
def phenotype_mapping_cache() -> Dict:
    """
    :return: Mock phenotype name to ID mappings for Dictybase.
    """
    return {
        "decreased slug migration": {"id": "DDPHENO:0000225"},
        "aberrant spore morphology": {"id": "DDPHENO:0000163"},
        "delayed aggregation": {"id": "DDPHENO:0000156"},
        "increased cell-substrate adhesion": {"id": "DDPHENO:0000213"},
        "decreased cell motility": {"id": "DDPHENO:0000148"},
    }


@pytest.mark.parametrize(
    "query",
    [
        (
            {
                # empty 'Phenotypes' field
                "Phenotypes": None
            },
            None,
        ),
        (
            {
                # Unrecognized phenotype
                "Phenotypes": "this is not a phenotype"
            },
            None,
        ),
        (
            {
                # Single known phenotype mappings (with flanking blank space?)
                "Phenotypes": " decreased slug migration "
            },
            "DDPHENO:0000225",
        ),
        (
            {
                # Multiple known phenotype mappings
                "Phenotypes": " decreased slug migration | aberrant spore morphology "
            },
            "DDPHENO:0000163",
        ),
    ],
)
def test_parse_phenotypes(query, phenotype_mapping_cache):
    koza_transform = KozaTransform(
        mappings={"dictybase_phenotype_names_to_ids": phenotype_mapping_cache},
        writer=PassthroughWriter(),
        extra_fields={}
    )
    phenotypes: List[str] = parse_phenotypes(query[0], koza_transform)
    if query[1]:  # If we expect a phenotype ID
        assert query[1] in phenotypes
    else:  # If we expect None (empty list)
        assert not phenotypes


@pytest.fixture
def test_row_1():
    """
    :return: Test Dictybase Gene to Phenotype data row.
    """
    return {
        "Systematic_Name": "DBS0235594",
        "Strain_Descriptor": "CHE10",
        "Associated gene(s)": "cbpC",
        "DDB_G_ID": "DDB_G0283613",
        "Phenotypes": " decreased slug migration | aberrant spore morphology ",
    }


@pytest.fixture
def basic_dictybase_1(test_row_1, phenotype_mapping_cache):
    """
    Mock Koza run for Dictybase Gene to Phenotype ingest using KozaTransform.
    """
    koza_transform = KozaTransform(
        mappings={"dictybase_phenotype_names_to_ids": phenotype_mapping_cache},
        writer=PassthroughWriter(),
        extra_fields={}
    )
    return transform_record(koza_transform, test_row_1)


@pytest.mark.parametrize("cls", [GeneToPhenotypicFeatureAssociation])
def test_confirm_one_of_each_classes(cls, basic_dictybase_1):
    class_entities = [entity for entity in basic_dictybase_1 if isinstance(entity, cls)]
    assert class_entities
    assert len(class_entities) == 2
    assert class_entities[0]


def test_dictybase_g2p_association_ncbi_gene(basic_dictybase_1):
    associations = [
        association for association in basic_dictybase_1 if isinstance(association, GeneToPhenotypicFeatureAssociation)
    ]
    assert len(associations) == 2

    for association in associations:
        assert association
        assert association.subject == "dictyBase:DDB_G0283613"
        assert association.object in ["DDPHENO:0000225", "DDPHENO:0000163"]
        assert association.predicate == "biolink:has_phenotype"
        assert association.primary_knowledge_source == "infores:dictybase"
        assert "infores:monarchinitiative" in association.aggregator_knowledge_source


@pytest.fixture
def test_row_2():
    """
    :return: another Test Dictybase Gene to Phenotype data row.
    """
    return {
        "Systematic Name": "DBS0351079",
        "Strain Descriptor": "DDB_G0274679-",
        "Associated gene(s)": "DDB_G0274679",
        "DDB_G_ID": "DDB_G0283613",
        "Phenotypes": "delayed aggregation | increased cell-substrate adhesion | decreased cell motility",
    }


@pytest.fixture
def basic_dictybase_2(test_row_2, phenotype_mapping_cache):
    """
    Mock Koza run for Dictybase Gene to Phenotype ingest using KozaTransform.
    """
    koza_transform = KozaTransform(
        mappings={"dictybase_phenotype_names_to_ids": phenotype_mapping_cache},
        writer=PassthroughWriter(),
        extra_fields={}
    )
    return transform_record(koza_transform, test_row_2)


def test_dictybase_g2p_association_dictybase_gene(basic_dictybase_2):
    associations = [
        association for association in basic_dictybase_2 if isinstance(association, GeneToPhenotypicFeatureAssociation)
    ]
    assert len(associations) == 3

    for association in associations:
        assert association
        assert association.subject == "dictyBase:DDB_G0283613"
        assert association.object in ["DDPHENO:0000156", "DDPHENO:0000213", "DDPHENO:0000148"]
        assert association.predicate == "biolink:has_phenotype"
        assert association.primary_knowledge_source == "infores:dictybase"
        assert "infores:monarchinitiative" in association.aggregator_knowledge_source


@pytest.fixture
def real_data_row():
    """Real example from all-mutants-ddb_g.txt file"""
    return {
        "Systematic_Name": "DBS0235412",
        "Strain_Descriptor": "1C7",
        "Associated gene(s)": "gp130",
        "DDB_G_ID": "DDB_G0279921",
        "Phenotypes": "decreased cell-substrate adhesion | delayed development | increased growth rate",
    }


@pytest.fixture
def real_data_mapping():
    """Real phenotype mappings from ddpheno.tsv"""
    return {
        "decreased cell-substrate adhesion": {"id": "DDPHENO:0000393"},
        "delayed development": {"id": "DDPHENO:0000162"},
        "increased growth rate": {"id": "DDPHENO:0000171"},
    }


@pytest.fixture
def real_data_associations(real_data_row, real_data_mapping):
    koza_transform = KozaTransform(
        mappings={"dictybase_phenotype_names_to_ids": real_data_mapping},
        writer=PassthroughWriter(),
        extra_fields={}
    )
    return transform_record(koza_transform, real_data_row)


def test_real_data_from_file(real_data_associations):
    """Test with actual data from all-mutants-ddb_g.txt"""
    associations = [
        association for association in real_data_associations
        if isinstance(association, GeneToPhenotypicFeatureAssociation)
    ]
    assert len(associations) == 3

    for association in associations:
        assert association.subject == "dictyBase:DDB_G0279921"
        assert association.object in ["DDPHENO:0000393", "DDPHENO:0000162", "DDPHENO:0000171"]
        assert association.predicate == "biolink:has_phenotype"
