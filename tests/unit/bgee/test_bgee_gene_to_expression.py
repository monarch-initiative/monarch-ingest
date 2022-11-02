import pytest
from biolink.pydanticmodel import GeneToExpressionSiteAssociation

#
# test of utility function - proven to work, unless modified in the future?
#
# def test_get_data():
#     entry = {
#         "testing": {
#             "one": {
#                 "two": {
#                     "three": "Success!"
#                 }
#             }
#         }
#     }
#     assert get_data(entry, "testing.one.two.three") == "Success!"


@pytest.fixture
def source_name():
    return "bgee_gene_to_expression"


@pytest.fixture
def script():
    return "./monarch_ingest/ingests/bgee/gene_to_expression.py"


def aggregator_knowledge_sources(association) -> bool:
    return all(
        [
            ks in ["infores:monarchinitiative", "infores:bgee"]
            for ks in association.aggregator_knowledge_source
        ]
    )


@pytest.fixture
def koza_row_1(mock_koza, source_name, script, global_table):
    rows = iter([{'Gene ID': 'ENSG00000000003',
            'Gene name': 'TSPAN6',
            'Anatomical entity ID': 'CL:0000019',
            'Anatomical entity name': 'sperm',
            'Expression': 'present',
            'Call quality': 'gold quality',
            'FDR': '0.00167287722066534',
            'Expression score': 99.96,
            'Expression rank': 18.5}])
    return mock_koza(
        source_name,
        rows,
        script,
        global_table=global_table,
    )


@pytest.fixture
def koza_skip_row_1(mock_koza, source_name, script, global_table):
    rows = iter([{'Gene ID': 'ENSG00000008988', 'Gene name': 'RPS20', 'Anatomical entity ID': 'UBERON:0007023',
            'Anatomical entity name': 'adult organism', 'Expression': 'present', 'Call quality': 'gold quality',
            'FDR': '0.00167287722066534', 'Expression score': 99.95, 'Expression rank': 24.0}])
    return mock_koza(
        source_name,
        rows,
        script,
        global_table=global_table,
    )


def test_association(koza_row_1):
    assert len(koza_row_1) == 1
    association = koza_row_1[0]
    assert association.subject == "ENSEMBL:ENSG00000000003"
    assert association.predicate == "biolink:expressed_in"
    assert association.object == "CL:0000019"
    assert aggregator_knowledge_sources(association)

