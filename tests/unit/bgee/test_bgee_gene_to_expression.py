import pytest
import types
import yaml
import pandas as pd
from pathlib import PosixPath
from typing import List, Dict

from koza.app import KozaApp
from koza.model.source import Source
from koza.io.yaml_loader import UniqueIncludeLoader
from koza.model.config.source_config import PrimaryFileConfig, OutputFormat

from biolink.pydanticmodel import GeneToExpressionSiteAssociation
from monarch_ingest.ingests.bgee.gene_to_expression_utils import get_row_group, filter_group_by_rank, write_group


def get_mock_koza(
        yaml_file: str,
        translation_table: str,
        output_dir: str,
        output_format: str,
        files: List[str]) -> KozaApp:
    """Function to mock a KozaApp:

        Creates a mock KozaApp from KozaApp by changing input files and write function:

        Args:
            yaml_file (str): The yaml file used for the Koza ingest of interest.
            translation_table (str): The translation table for the Koza ingest.
            output_dir (str): The directory for KozaApp output.
            output_format (str): The format for output from the KozaApp.
            files (List[PosixPath]): The files to use for the mock KozaApp.

        Returns:
            KozaApp: Returns a mock KozaApp for the indicated ingest modifying files, output, and write function.
        """
    with open(yaml_file, 'r') as source_fh:
        yaml_data = yaml.load(source_fh, Loader=UniqueIncludeLoader)

    yaml_data['files'] = files
    source_config = PrimaryFileConfig(**yaml_data)

    koza_app = KozaApp(
        source=Source(source_config),
        translation_table=translation_table,
        output_dir=output_dir,
        output_format=OutputFormat(output_format))

    def _mock_write(self, *entities):
        if hasattr(self, '_entities'):
            self._entities.extend(list(entities))
        else:
            self._entities = list(entities)

    koza_app.write = types.MethodType(_mock_write, koza_app)
    return koza_app


def get_koza_rows(mock_koza: KozaApp, n_rows: int) -> List[Dict]:
    """Function to get specified number of rows from mock Koza:

        Read n rows from mock Koza:

        Args:
            mock_koza (KozaApp): The mock koza object to read rows from.
            n_rows (int): The number of rows to return.

        Returns:
            List[Dict]: Returns a list of ros in Koza dict format.
        """
    rows = []
    for i in range(0, n_rows):
        rows.append(mock_koza.get_row())
    return rows


@pytest.fixture
def bgee_yaml():
    return "monarch_ingest/ingests/bgee/gene_to_expression.yaml"


@pytest.fixture
def bgee_test_output() -> str:
    return "tests/unit/bgee/output"


@pytest.fixture
def bgee_test_output_format() -> str:
    return 'tsv'


@pytest.fixture
def bgee_test_files() -> List[str]:
    return ["tests/unit/bgee/test_bgee.tsv.gz"]


@pytest.fixture
def bgee_mock_koza_rows(bgee_yaml, global_table, bgee_test_output, bgee_test_output_format, bgee_test_files) -> KozaApp:
    return get_mock_koza(bgee_yaml, global_table, bgee_test_output, bgee_test_output_format, bgee_test_files)


@pytest.fixture
def row_group_1(bgee_mock_koza_rows) -> List[Dict]:
    return get_koza_rows(bgee_mock_koza_rows, 5)


@pytest.fixture
def row_group_2(bgee_mock_koza_rows) -> List[Dict]:
    _ = get_koza_rows(bgee_mock_koza_rows, 5)
    return get_koza_rows(bgee_mock_koza_rows, 22)


@pytest.fixture
def filter_col() -> str:
    return 'Expression rank'


@pytest.fixture
def smallest_n() -> int:
    return 10


def test_filter_group_by_rank_short(row_group_1, filter_col, smallest_n):
    filtered_group = filter_group_by_rank(row_group_1, filter_col, smallest_n=smallest_n)

    assert type(filtered_group) is list
    assert len(filtered_group) == 5
    for i in filtered_group:
        assert type(i) is dict
        assert i['Gene ID'] == 'ENSSSCG00000000002'

    filtered_group_df = pd.DataFrame(filtered_group)
    expected_filtered_col = sorted(pd.DataFrame(row_group_1)[filter_col].to_list())[0:10]
    assert filtered_group_df[filter_col].to_list() == expected_filtered_col


def test_filter_group_by_rank_long(row_group_2, filter_col, smallest_n):
    filtered_group = filter_group_by_rank(row_group_2, filter_col, smallest_n=smallest_n)

    assert type(filtered_group) is list
    assert len(filtered_group) == 10
    for i in filtered_group:
        assert type(i) is dict
        assert i['Gene ID'] == 'ENSSSCG00000000003'

    filtered_group_df = pd.DataFrame(filtered_group)
    expected_filtered_col = sorted(pd.DataFrame(row_group_2)[filter_col].to_list())[0:10]
    assert filtered_group_df[filter_col].to_list() == expected_filtered_col


@pytest.fixture
def bgee_mock_koza(bgee_yaml, global_table, bgee_test_output, bgee_test_output_format, bgee_test_files) -> KozaApp:
    return get_mock_koza(bgee_yaml, global_table, bgee_test_output, bgee_test_output_format, bgee_test_files)


def test_write_group(row_group_1, bgee_mock_koza):
    write_group(row_group_1, bgee_mock_koza)
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


def test_get_row_group(bgee_mock_koza, row_group_1, filter_col) -> List:
    row_group = get_row_group(bgee_mock_koza)

    assert type(row_group) is list
    assert len(row_group) == 5
    for i in row_group:
        assert type(i) is dict

    assert row_group == row_group_1

# Ignoring process_koza_sources for now as it depends completely on above tested functions but goes deeper into Koza.
# def test_process_koza_source(bgee_mock_koza):
#     pass
