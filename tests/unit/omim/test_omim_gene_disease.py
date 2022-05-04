"""
OMIM Morbid map tests to
"""

import pytest
from biolink_model_pydantic.model import (
    Disease,
    Gene,
    GeneToDiseaseAssociation,
    NucleicAcidEntity,
    Predicate,
)


@pytest.fixture
def map_cache():
    mim2gene = {
        "609300": {
            'Entrez Gene ID (NCBI)': '1586',
            'Ensembl Gene ID (Ensembl)': 'ENSG00000148795',
        },
        "104000": {'Entrez Gene ID (NCBI)': '100034700', 'Ensembl Gene ID (Ensembl)': ''},
        "605572": {'Entrez Gene ID (NCBI)': '65077', 'Ensembl Gene ID (Ensembl)': ''},
    }
    return {"mim2gene": mim2gene}


@pytest.fixture
def gene_association_row():
    return {
        'Phenotype': '17,20-lyase deficiency, isolated, 202110 (3)',
        'Gene Symbols': 'CYP17A1, CYP17, P450C17',
        'MIM Number': '609300',
        'Cyto Location': '10q24.32',
    }


@pytest.fixture
def gene_association_entities(mock_koza, gene_association_row, global_table, map_cache):
    return mock_koza(
        name="omim_gene_to_disease",
        data=iter([gene_association_row]),
        transform_code="./monarch_ingest/ingests/omim/gene_to_disease.py",
        global_table=global_table,
        local_table="./monarch_ingest/ingests/omim/omim-translation.yaml",
        map_cache=map_cache,
    )


def test_gene_association_transform(gene_association_entities):
    entities = gene_association_entities
    assert entities
    assert len(entities) == 3
    genes = [entity for entity in entities if isinstance(entity, Gene)]
    diseases = [entity for entity in entities if isinstance(entity, Disease)]
    associations = [
        entity for entity in entities if isinstance(entity, GeneToDiseaseAssociation)
    ]
    assert len(genes) == 1
    assert len(diseases) == 1
    assert len(associations) == 1


@pytest.mark.parametrize(
    "phenotype",
    [
        '[?Birbeck granule deficiency], 613393 (3)',
        '[AMP deaminase deficiency, erythrocytic], 612874 (3)',
    ],
)
def test_ignore_phenotype_modifiers(
    mock_koza, gene_association_row, global_table, map_cache, phenotype
):
    row = gene_association_row
    row['Phenotype'] = phenotype
    entities = mock_koza(
        name="omim_gene_to_disease",
        data=iter([gene_association_row]),
        transform_code="./monarch_ingest/ingests/omim/gene_to_disease.py",
        global_table=global_table,
        local_table="./monarch_ingest/ingests/omim/omim-translation.yaml",
        map_cache=map_cache,
    )

    # A gene or genomic entity is ok, but no disease or association
    for entity in entities:
        assert isinstance(entity, Disease) is False
        assert isinstance(entity, GeneToDiseaseAssociation) is False


def test_genomic_entity_row(mock_koza, global_table, map_cache):
    row = {
        'Phenotype': 'Abdominal obesity-metabolic syndrome (2)',
        'Gene Symbols': 'AOMS2',
        'MIM Number': '605572',
        'Cyto Location': '17p12',
    }

    entities = mock_koza(
        name="omim_gene_to_disease",
        data=iter([row]),
        transform_code="./monarch_ingest/ingests/omim/gene_to_disease.py",
        global_table=global_table,
        local_table="./monarch_ingest/ingests/omim/omim-translation.yaml",
        map_cache=map_cache,
    )

    assert entities
    assert len(entities) == 3
    genomic_entity = [
        entity for entity in entities if isinstance(entity, NucleicAcidEntity)
    ][0]
    assert genomic_entity
    assert genomic_entity.id == 'NCBIGene:65077'
    disease = [entity for entity in entities if isinstance(entity, Disease)][0]
    assert disease
    assert disease.id == 'OMIM:605572'
    association = [
        entity for entity in entities if isinstance(entity, GeneToDiseaseAssociation)
    ][0]
    assert association
    assert association.predicate == Predicate.gene_associated_with_condition
    assert association.relation == 'RO:0003303'


def test_susceptibility_row(mock_koza, gene_association_row, global_table, map_cache):
    gene_association_row['Phenotype'] = '{' + gene_association_row['Phenotype'] + '}'
    entities = mock_koza(
        name="omim_gene_to_disease",
        data=iter([gene_association_row]),
        transform_code="./monarch_ingest/ingests/omim/gene_to_disease.py",
        global_table=global_table,
        local_table="./monarch_ingest/ingests/omim/omim-translation.yaml",
        map_cache=map_cache,
    )
    assert len(entities) == 3
    association = [
        entity for entity in entities if isinstance(entity, GeneToDiseaseAssociation)
    ][0]
    assert association
    assert association.relation == 'RO:0019501'
