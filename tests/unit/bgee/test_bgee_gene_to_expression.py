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


@pytest.fixture
def filter_group_2(bgee_mock_koza) -> List[Dict]:
    _ = get_bgee_rows(bgee_mock_koza, 5)
    return get_bgee_rows(bgee_mock_koza, 22)


def test_filter_group_by_rank_short(filter_group_1, filter_col, smallest_n):
    filtered_group = filter_group_by_rank(filter_group_1, filter_col, smallest_n=smallest_n)

    assert type(filtered_group) is list
    assert len(filtered_group) == 5
    for i in filtered_group:
        assert type(i) is dict
        assert i['Gene ID'] == 'ENSSSCG00000000002'

    filtered_group_df = pd.DataFrame(filtered_group)
    expected_filtered_col = sorted(pd.DataFrame(filter_group_1)[filter_col].to_list())[0:10]
    assert filtered_group_df[filter_col].to_list() == expected_filtered_col


def test_filter_group_by_rank_long(filter_group_2, filter_col, smallest_n):
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
