from os.path import abspath, dirname
from typing import Tuple
import pytest

from monarch_ingest.ingests.panther.orthology_utils import target_taxon, filter_panther_orthologs_file


@pytest.mark.parametrize(
    "query",
    [
        (
                "",
                False
        ),
        (
                "ASHGO|EnsemblGenome=AGOS_AGL109W|UniProtKB=Q750Q1	" +
                "EMENI|EnsemblGenome=ANIA_10586|UniProtKB=C8VAR7	O	" +
                "Pezizomycotina-Saccharomycotina	PTHR43765",
                False
        ),
        (
                "EMENI|EnsemblGenome=ANIA_10586|UniProtKB=C8VAR7	" +
                "ASPFU|EnsemblGenome=AFUA_3G13550|UniProtKB=Q4WYM2	O	" +
                "Aspergillus	PTHR43765",
                True
        )

    ]
)
def test_target_taxon(query: Tuple):
    assert target_taxon(query[0]) == query[1]


TEST_SOURCE_FILENAME = "test_data"
TEST_TARGET_FILENAME = "filtered_data"
TEST_DIRECTORY = abspath(dirname(__file__))


def test_filter_panther_orthologs_file():
    filter_panther_orthologs_file(
        directory=TEST_DIRECTORY,
        source_filename=TEST_SOURCE_FILENAME,
        target_filename=TEST_TARGET_FILENAME,
        number_of_lines=50
    )

