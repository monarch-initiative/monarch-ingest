"""
Tests of HPOA Utils methods
"""
from typing import Optional, Tuple
import pytest

from monarch_ingest.ingests.hpoa.hpoa_utils import (
    FrequencyHpoTerm,
    get_hpo_term,
    map_percentage_frequency_to_hpo_term,
    phenotype_frequency_to_hpo_term
)


def test_get_hpo_term():
    assert get_hpo_term("HP:0040282") == FrequencyHpoTerm("HP:0040282", "Frequent", 30, 79)


@pytest.mark.parametrize(
    "query",
    [
        (
            -1, None
        ),
        (
            0, FrequencyHpoTerm("HP:0040285", "Excluded", 0, 0)
        ),
        (
            1, FrequencyHpoTerm("HP:0040284", "Very rare", 1, 4)
        ),
        (
            2, FrequencyHpoTerm("HP:0040284", "Very rare", 1, 4)
        ),
        (
            4, FrequencyHpoTerm("HP:0040284", "Very rare", 1, 4)
        ),

        (
            20, FrequencyHpoTerm("HP:0040283", "Occasional", 5, 29)
        ),
        (
            50, FrequencyHpoTerm("HP:0040282", "Frequent", 30, 79)
        ),
        (
            85, FrequencyHpoTerm("HP:0040281", "Very frequent", 80, 99)
        ),
        (
            100, FrequencyHpoTerm("HP:0040280", "Obligate", 100, 100)
        ),
        (
            101, None
        )
    ]
)
def test_map_percentage_frequency_to_hpo_term(query: Tuple[int, Optional[FrequencyHpoTerm]]):
    assert map_percentage_frequency_to_hpo_term(query[0]) == query[1]


@pytest.mark.parametrize(
    "query",
    [
        (
            None, None
        ),
        (
            "", None
        ),
        (
            "0", None  # not a raw number... has to be tagged as a percentage?
        ),
        (
            "HP:0040279", None  # the subontology term below HP:0040279, not this 'Frequency' term itself, LOL
        ),
        (   # exact matches to global lower bounds should be sent back accurately
            "0%", FrequencyHpoTerm("HP:0040285", "Excluded", 0, 0)
        ),
        (   # exact matches to lower bounds should be sent back accurately
            "5%", FrequencyHpoTerm("HP:0040283", "Occasional", 5, 29)
        ),
        (   # matches within percentage range bounds should be sent back accurately
            "17%", FrequencyHpoTerm("HP:0040283", "Occasional", 5, 29)
        ),
        (    # exact matches to upper bounds should be sent back accurately
            "29%", FrequencyHpoTerm("HP:0040283", "Occasional", 5, 29)
        ),
        (   # exact matches to global upper bounds should be sent back accurately
            "100%", FrequencyHpoTerm("HP:0040280", "Obligate", 100, 100)
        ),
        (   # if a valid 'Frequency' HPO subontology term  already, should be sent back
            "HP:0040282", FrequencyHpoTerm("HP:0040282", "Frequent", 30, 79)
        ),
        (   # division ratios converted to percentages (i.e. 7/13 ~ 53.8%) that match
            # within a specific percentage range should be sent back accurately
            "7/13", FrequencyHpoTerm("HP:0040282", "Frequent", 30, 79)
        ),
        (
            "1/1", FrequencyHpoTerm("HP:0040280", "Obligate", 100, 100)
        ),
        (
            "2/2", FrequencyHpoTerm("HP:0040280", "Obligate", 100, 100)
        ),
        (
            "1/2", FrequencyHpoTerm("HP:0040282", "Frequent", 30, 79)
        )
    ]
)
def test_phenotype_frequency_to_hpo_term(query: Tuple[str, Optional[FrequencyHpoTerm]]):
    assert phenotype_frequency_to_hpo_term(query[0]) == query[1]
