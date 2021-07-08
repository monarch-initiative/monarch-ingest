from unittest.mock import patch

import pytest
from biolink_model_pydantic.model import Gene, PhenotypicFeature, GeneToPhenotypicFeatureAssociation
from koza.koza_runner import get_translation_table

@pytest.fixture
def pombase_gene2phenotype_entities(mock_koza):
    row = iter([{
        "Database name": "PomBase",
        "Gene systematic ID": "SPAC24B11.06c",
        "FYPO ID": "FYPO:0004058",
        "Allele description": "",
        "Expression": "",
        "Parental strain": "972 h-",
        "Strain name (background)": "",
        "Genotype description": "",
        "Gene name": "sty1",
        "Allele name": "sty1delta",
        "Allele synonym": "",
        "Allele type": "deletion",
        "Evidence": "cell growth assay evidence",
        "Condition": "",
        "Penetrance": "",
        "Severity": "FYPO_EXT:0000001",
        "Extension": "",
        "Reference": "PMID:19436749",
        "Taxon": "4896",
        "Date": "2014-11-21",
    }])
    tt = get_translation_table("mingestibles/translation_table.yaml", None)

    return mock_koza('gene-to-phenotype', row, './mingestibles/pombase/gene2phenotype.py', translation_table=tt)


@pytest.fixture
def genes(pombase_gene2phenotype_entities):
   return [gene for gene in pombase_gene2phenotype_entities if isinstance(gene, Gene)]


def test_pombase_gene(genes):
    assert len(genes) == 1
    gene = genes[0]
    assert gene


@pytest.fixture
def phenotypes(pombase_gene2phenotype_entities):
    return [phenotype for phenotype in pombase_gene2phenotype_entities if isinstance(phenotype, PhenotypicFeature)]


def test_pombase_phenotype(phenotypes):
    assert phenotypes
    assert len(phenotypes) == 1
    phenotype = phenotypes[0]
    assert phenotype


@pytest.fixture
def associations(pombase_gene2phenotype_entities):
    return [association for association in pombase_gene2phenotype_entities if isinstance(association, GeneToPhenotypicFeatureAssociation)]


def test_pombase_g2p_association(associations):
    assert associations
    assert len(associations) == 1
    association = associations[0]


def test_pombase_g2p_association_publication(associations):
    assert associations[0].publications[0] == 'PMID:19436749'
