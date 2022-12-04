import types
from typing import List, Dict

import pytest
import yaml
import pandas as pd
from koza.app import KozaApp
from koza.io.yaml_loader import UniqueIncludeLoader
# from koza.cli_runner import *
# from koza.io.writer.jsonl_writer import JSONLWriter
# from koza.io.writer.tsv_writer import TSVWriter
from koza.model.source import Source
from koza.model.config.source_config import PrimaryFileConfig, OutputFormat
from monarch_ingest.ingests.bgee.gene_to_expression_utils import get_row_group, filter_group_by_rank, write_group
from pathlib import PosixPath
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

# transform_source(source="monarch_ingest/ingests/bgee/gene_to_expression.yaml", output_dir="tests/unit/bgee/output")
# source_name = "bgee_gene_to_expression"
# koza_app = get_koza_app(source_name)


# class MockKozaApp(KozaApp):
#     def write(self, *entities):
#         if hasattr(self, '_entities'):
#             self._entities.extend(list(entities))
#         else:
#             self._entities = list(entities)


@pytest.fixture
def bgee_mock_koza(koza_row_1, mock_koza, global_table, source_name, script):
    yaml_file = "monarch_ingest/ingests/bgee/gene_to_expression.yaml"
    with open(yaml_file, 'r') as source_fh:
        source_config = PrimaryFileConfig(**yaml.load(source_fh, Loader=UniqueIncludeLoader))

    koza_app = KozaApp(
        source=Source(source_config),
        translation_table=global_table,
        output_dir="tests/unit/bgee/output",
        output_format=OutputFormat('tsv'),
        schema=None)

    koza_app.source.config.files = [PosixPath("tests/unit/bgee/test_bgee.tsv.gz")]
    # koza_app.source.config.transform_code = str(Path(yaml_file).parent / Path(yaml_file).stem) + '.py'

    def _mock_write(self, *entities):
        if hasattr(self, '_entities'):
            self._entities.extend(list(entities))
        else:
            self._entities = list(entities)

    koza_app.write = types.MethodType(_mock_write, koza_app)

    return koza_app


@pytest.fixture
def filter_col() -> str:
    return 'Expression rank'


@pytest.fixture
def smallest_n() -> int:
    return 10


def get_bgee_rows(mock_koza, n_rows) -> List[Dict]:
    rows = []
    for i in range(0, n_rows):
        rows.append(mock_koza.get_row())
    return rows


@pytest.fixture
def filter_group_1(bgee_mock_koza) -> List[Dict]:
    return get_bgee_rows(bgee_mock_koza, 5)

    # return [{'Gene ID': 'ENSSSCG00000000002', 'Gene name': 'GTSE1', 'Anatomical entity ID': 'CL:0000023',
    #   'Anatomical entity name': 'oocyte', 'Expression': 'present', 'Call quality': 'gold quality',
    #   'FDR': 1.763714432449095e-05, 'Expression score': 77.16, 'Expression rank': 5660.0},
    #  {'Gene ID': 'ENSSSCG00000000002', 'Gene name': 'GTSE1', 'Anatomical entity ID': 'CL:0000501',
    #   'Anatomical entity name': 'granulosa cell', 'Expression': 'present', 'Call quality': 'gold quality',
    #   'FDR': 7.42834005002371e-09, 'Expression score': 74.06, 'Expression rank': 6430.0},
    #  {'Gene ID': 'ENSSSCG00000000002', 'Gene name': 'GTSE1', 'Anatomical entity ID': 'UBERON:0000948',
    #   'Anatomical entity name': 'heart', 'Expression': 'present', 'Call quality': 'gold quality',
    #   'FDR': 1.6545205030930632e-10, 'Expression score': 70.64, 'Expression rank': 7270.0},
    #  {'Gene ID': 'ENSSSCG00000000002', 'Gene name': 'GTSE1', 'Anatomical entity ID': 'UBERON:0005417',
    #   'Anatomical entity name': 'forelimb bud', 'Expression': 'present', 'Call quality': 'gold quality',
    #   'FDR': 2.1864126110580799e-10, 'Expression score': 82.83, 'Expression rank': 4260.0},
    #  {'Gene ID': 'ENSSSCG00000000002', 'Gene name': 'GTSE1', 'Anatomical entity ID': 'UBERON:0005418',
    #   'Anatomical entity name': 'hindlimb bud', 'Expression': 'present', 'Call quality': 'gold quality',
    #   'FDR': 1.6421484304688489e-10, 'Expression score': 84.08, 'Expression rank': 3950.0}]


@pytest.fixture
def filter_group_2(bgee_mock_koza) -> List[Dict]:
    _ = get_bgee_rows(bgee_mock_koza, 5)
    return get_bgee_rows(bgee_mock_koza, 22)
    # return [{'Gene ID': 'ENSSSCG00000000003', 'Gene name': 'TTC38', 'Anatomical entity ID': 'CL:0000501',
    #   'Anatomical entity name': 'granulosa cell', 'Expression': 'present', 'Call quality': 'gold quality',
    #   'FDR': 1.4472340372207918e-09, 'Expression score': 72.88, 'Expression rank': 6720.0},
    #  {'Gene ID': 'ENSSSCG00000000003', 'Gene name': 'TTC38', 'Anatomical entity ID': 'UBERON:0000029',
    #   'Anatomical entity name': 'lymph node', 'Expression': 'present', 'Call quality': 'gold quality',
    #   'FDR': 8.32109039981919e-10, 'Expression score': 74.17, 'Expression rank': 6400.0},
    #  {'Gene ID': 'ENSSSCG00000000003', 'Gene name': 'TTC38', 'Anatomical entity ID': 'UBERON:0000082',
    #   'Anatomical entity name': 'adult mammalian kidney', 'Expression': 'present', 'Call quality': 'gold quality',
    #   'FDR': 5.058176826146248e-10, 'Expression score': 84.3, 'Expression rank': 3890.0},
    #  {'Gene ID': 'ENSSSCG00000000003', 'Gene name': 'TTC38', 'Anatomical entity ID': 'UBERON:0000178',
    #   'Anatomical entity name': 'blood', 'Expression': 'present', 'Call quality': 'gold quality',
    #   'FDR': 1.0302163613600838e-09, 'Expression score': 87.98, 'Expression rank': 2980.0},
    #  {'Gene ID': 'ENSSSCG00000000003', 'Gene name': 'TTC38', 'Anatomical entity ID': 'UBERON:0000465',
    #   'Anatomical entity name': 'material anatomical entity', 'Expression': 'present', 'Call quality': 'gold quality',
    #   'FDR': 1.612528926461786e-11, 'Expression score': 70.31, 'Expression rank': 7360.0},
    #  {'Gene ID': 'ENSSSCG00000000003', 'Gene name': 'TTC38', 'Anatomical entity ID': 'UBERON:0000948',
    #   'Anatomical entity name': 'heart', 'Expression': 'present', 'Call quality': 'gold quality',
    #   'FDR': 8.646459599840692e-08, 'Expression score': 72.01, 'Expression rank': 6930.0},
    #  {'Gene ID': 'ENSSSCG00000000003', 'Gene name': 'TTC38', 'Anatomical entity ID': 'UBERON:0000989',
    #   'Anatomical entity name': 'penis', 'Expression': 'present', 'Call quality': 'gold quality',
    #   'FDR': 1.19937552275178e-05, 'Expression score': 74.7, 'Expression rank': 6270.0},
    #  {'Gene ID': 'ENSSSCG00000000003', 'Gene name': 'TTC38', 'Anatomical entity ID': 'UBERON:0000992',
    #   'Anatomical entity name': 'ovary', 'Expression': 'present', 'Call quality': 'gold quality',
    #   'FDR': 1.652805108499622e-06, 'Expression score': 73.77, 'Expression rank': 6500.0},
    #  {'Gene ID': 'ENSSSCG00000000003', 'Gene name': 'TTC38', 'Anatomical entity ID': 'UBERON:0000995',
    #   'Anatomical entity name': 'uterus', 'Expression': 'present', 'Call quality': 'gold quality',
    #   'FDR': 7.416456947051328e-11, 'Expression score': 82.55, 'Expression rank': 4330.0},
    #  {'Gene ID': 'ENSSSCG00000000003', 'Gene name': 'TTC38', 'Anatomical entity ID': 'UBERON:0001013',
    #   'Anatomical entity name': 'adipose tissue', 'Expression': 'present', 'Call quality': 'gold quality',
    #   'FDR': 4.93782921195003e-09, 'Expression score': 79.81, 'Expression rank': 5000.0},
    #  {'Gene ID': 'ENSSSCG00000000003', 'Gene name': 'TTC38', 'Anatomical entity ID': 'UBERON:0001114',
    #   'Anatomical entity name': 'right lobe of liver', 'Expression': 'present', 'Call quality': 'gold quality',
    #   'FDR': 9.81006191003368e-13, 'Expression score': 94.11, 'Expression rank': 1460.0},
    #  {'Gene ID': 'ENSSSCG00000000003', 'Gene name': 'TTC38', 'Anatomical entity ID': 'UBERON:0001153',
    #   'Anatomical entity name': 'caecum', 'Expression': 'present', 'Call quality': 'gold quality',
    #   'FDR': 3.038152065170732e-08, 'Expression score': 86.85, 'Expression rank': 3260.0},
    #  {'Gene ID': 'ENSSSCG00000000003', 'Gene name': 'TTC38', 'Anatomical entity ID': 'UBERON:0001155',
    #   'Anatomical entity name': 'colon', 'Expression': 'present', 'Call quality': 'gold quality',
    #   'FDR': 4.557228097756098e-08, 'Expression score': 87.66, 'Expression rank': 3060.0},
    #  {'Gene ID': 'ENSSSCG00000000003', 'Gene name': 'TTC38', 'Anatomical entity ID': 'UBERON:0002048',
    #   'Anatomical entity name': 'lung', 'Expression': 'present', 'Call quality': 'gold quality',
    #   'FDR': 8.68931910962822e-08, 'Expression score': 73.03, 'Expression rank': 6680.0},
    #  {'Gene ID': 'ENSSSCG00000000003', 'Gene name': 'TTC38', 'Anatomical entity ID': 'UBERON:0002106',
    #   'Anatomical entity name': 'spleen', 'Expression': 'present', 'Call quality': 'gold quality',
    #   'FDR': 1.2999490886640059e-08, 'Expression score': 73.1, 'Expression rank': 6670.0},
    #  {'Gene ID': 'ENSSSCG00000000003', 'Gene name': 'TTC38', 'Anatomical entity ID': 'UBERON:0002107',
    #   'Anatomical entity name': 'liver', 'Expression': 'present', 'Call quality': 'gold quality',
    #   'FDR': 1.072975521409934e-12, 'Expression score': 93.33, 'Expression rank': 1650.0},
    #  {'Gene ID': 'ENSSSCG00000000003', 'Gene name': 'TTC38', 'Anatomical entity ID': 'UBERON:0002113',
    #   'Anatomical entity name': 'kidney', 'Expression': 'present', 'Call quality': 'gold quality',
    #   'FDR': 6.142071860320444e-10, 'Expression score': 82.65, 'Expression rank': 4300.0},
    #  {'Gene ID': 'ENSSSCG00000000003', 'Gene name': 'TTC38', 'Anatomical entity ID': 'UBERON:0002114',
    #   'Anatomical entity name': 'duodenum', 'Expression': 'present', 'Call quality': 'gold quality',
    #   'FDR': 3.42770272900936e-08, 'Expression score': 86.69, 'Expression rank': 3300.0},
    #  {'Gene ID': 'ENSSSCG00000000003', 'Gene name': 'TTC38', 'Anatomical entity ID': 'UBERON:0002116',
    #   'Anatomical entity name': 'ileum', 'Expression': 'present', 'Call quality': 'gold quality',
    #   'FDR': 1.607121571876024e-06, 'Expression score': 79.24, 'Expression rank': 5140.0},
    #  {'Gene ID': 'ENSSSCG00000000003', 'Gene name': 'TTC38', 'Anatomical entity ID': 'UBERON:0002190',
    #   'Anatomical entity name': 'subcutaneous adipose tissue', 'Expression': 'present', 'Call quality': 'gold quality',
    #   'FDR': 4.264488864865935e-09, 'Expression score': 80.27, 'Expression rank': 4890.0},
    #  {'Gene ID': 'ENSSSCG00000000003', 'Gene name': 'TTC38', 'Anatomical entity ID': 'UBERON:0005316',
    #   'Anatomical entity name': 'endocardial endothelium', 'Expression': 'present', 'Call quality': 'gold quality',
    #   'FDR': 5.019612055912e-07, 'Expression score': 70.45, 'Expression rank': 7320.0},
    #  {'Gene ID': 'ENSSSCG00000000003', 'Gene name': 'TTC38', 'Anatomical entity ID': 'UBERON:0010533',
    #   'Anatomical entity name': 'metanephros cortex', 'Expression': 'present', 'Call quality': 'gold quality',
    #   'FDR': 8.1072623156589e-05, 'Expression score': 71.1, 'Expression rank': 7160.0}]


def test_filter_group_by_rank_short(filter_group_1, filter_col, smallest_n):
    filtered_group = filter_group_by_rank(filter_group_1, filter_col, smallest_n=smallest_n)

    assert type(filtered_group) is list
    assert len(filtered_group) == 5
    for i in filtered_group:
        assert type(i) is dict
        assert i['Gene ID'] == 'ENSSSCG00000000002'

    filtered_group_df = pd.DataFrame(filtered_group)
    assert filtered_group_df[filter_col].to_list() == [3950.0, 4260.0, 5660.0, 6430.0, 7270.0]


def test_filter_group_by_rank_short(filter_group_2, filter_col, smallest_n):
    filtered_group = filter_group_by_rank(filter_group_2, filter_col, smallest_n=smallest_n)

    assert type(filtered_group) is list
    assert len(filtered_group) == 10
    for i in filtered_group:
        assert type(i) is dict
        assert i['Gene ID'] == 'ENSSSCG00000000003'

    filtered_group_df = pd.DataFrame(filtered_group)
    expected_filtered_col = sorted(pd.DataFrame(filter_group_2)[filter_col].to_list())[0:10]
    assert filtered_group_df[filter_col].to_list() == expected_filtered_col


def test_write_group(bgee_mock_koza, filter_group_1):
    write_group(filter_group_1, bgee_mock_koza)
    write_result: list[GeneToExpressionSiteAssociation] = bgee_mock_koza._entities
    assert len(write_result) == 5
    prev_uuid = 0
    object_list = ['CL:0000023', 'CL:0000501', 'UBERON:0000948', 'UBERON:0005417', 'UBERON:0005418']
    for index, item in enumerate(write_result):
        assert type(item) == GeneToExpressionSiteAssociation
        assert item.id != prev_uuid
        prev_uuid = item.id
        assert item.category == ['biolink:GeneToExpressionSiteAssociation']
        assert item.predicate == 'biolink:expressed_in'
        assert item.subject == 'ENSEMBL:ENSSSCG00000000002'
        assert item.object == object_list[index]


@pytest.fixture
def source_name():
    return "bgee_gene_to_expression"


@pytest.fixture
def script():
    return "./monarch_ingest/ingests/bgee/gene_to_expression.py"


@pytest.fixture
def test_file_1():
    pass


def aggregator_knowledge_sources(association) -> bool:
    return all(
        [
            ks in ["infores:monarchinitiative", "infores:bgee"]
            for ks in association.aggregator_knowledge_source
        ]
    )


@pytest.fixture
def koza_row_1():
    return {'Gene ID': 'ENSG00000000003',
            'Gene name': 'TSPAN6',
            'Anatomical entity ID': 'CL:0000019',
            'Anatomical entity name': 'sperm',
            'Expression': 'present',
            'Call quality': 'gold quality',
            'FDR': 0.00167287722066534,
            'Expression score': 99.96,
            'Expression rank': 18.5}


@pytest.fixture
def bgee_koza_1(koza_row_1, mock_koza, source_name, script, global_table):
    rows = iter([koza_row_1])

    # source = getattr(koza_app, 'source')
    # config = getattr(source, 'config')
    # setattr(config, 'files', [PosixPath("tests")])

    test_mock_koza = mock_koza(
        source_name,
        rows,
        script,
        global_table=global_table,
    )
    return test_mock_koza


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


# def test_association(bgee_koza_1, bgee_mock_koza, global_table):
#     bgee_mock_koza.process_sources()
#
#
#     assert len(bgee_koza_1) == 1
#     association = bgee_koza_1[0]
#     assert association.subject == "ENSEMBL:ENSG00000000003"
#     assert association.predicate == "biolink:expressed_in"
#     assert association.object == "CL:0000019"
#     assert aggregator_knowledge_sources(association)
