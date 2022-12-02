import types

import pytest
from koza.cli_runner import *
from koza.io.writer.jsonl_writer import JSONLWriter
from koza.io.writer.tsv_writer import TSVWriter
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


class MockKozaApp(KozaApp):
    def write(self, *entities):
        if hasattr(self, '_entities'):
            self._entities.extend(list(entities))
        else:
            self._entities = list(entities)


@pytest.fixture
def bgee_mock_koza(koza_row_1, mock_koza, global_table, source_name, script):
    # source_yaml_file = "monarch_ingest/ingests/bgee/gene_to_expression.yaml"
    # with open(source_yaml_file, 'r') as source_fh:
    #     source_config = PrimaryFileConfig(**yaml.load(source_fh, Loader=UniqueIncludeLoader))

    # source_config.files = [PosixPath("tests/unit/bgee/test_bgee.tsv.gz")]
    # source_config.transform_code = str(Path(source_yaml_file).parent / Path(source_yaml_file).stem) + '.py'
    # koza_source = Source(source_config)
    # output_format = OutputFormat('tsv')
    # koza_app = MockKozaApp(koza_source, global_table, output_format=output_format)

    yaml_file = "monarch_ingest/ingests/bgee/gene_to_expression.yaml"
    with open(yaml_file, 'r') as source_fh:
        source_config = PrimaryFileConfig(**yaml.load(source_fh, Loader=UniqueIncludeLoader))
    source = Source(source_config)
    output_dir = "tests/unit/bgee/output"
    output_format = OutputFormat('tsv')
    schema = None
    koza_app = KozaApp(source, global_table, output_dir, output_format, schema)
    koza_app.source.config.files = [PosixPath("tests/unit/bgee/test_bgee.tsv.gz")]
    koza_app.source.config.transform_code = str(Path(yaml_file).parent / Path(yaml_file).stem) + '.py'

    def _mock_write(self, *entities):
        if hasattr(self, '_entities'):
            self._entities.extend(list(entities))
        else:
            self._entities = list(entities)

    koza_app.write = types.MethodType(_mock_write, koza_app)

    return koza_app


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


def test_association(bgee_koza_1, bgee_mock_koza, global_table):
    bgee_mock_koza.process_maps()
    bgee_mock_koza.process_sources()


    assert len(bgee_koza_1) == 1
    association = bgee_koza_1[0]
    assert association.subject == "ENSEMBL:ENSG00000000003"
    assert association.predicate == "biolink:expressed_in"
    assert association.object == "CL:0000019"
    assert aggregator_knowledge_sources(association)
