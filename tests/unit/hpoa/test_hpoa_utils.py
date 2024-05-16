"""
Tests of HPOA Utils methods
"""

import pytest

from monarch_ingest.ingests.hpoa.hpoa_utils import (
    FrequencyHpoTerm,
    get_hpo_term,
    phenotype_frequency_to_hpo_term,
)


def test_get_hpo_term():
    assert get_hpo_term("HP:0040282") == FrequencyHpoTerm(curie="HP:0040282", name="Frequent", lower=30, upper=79)


@pytest.mark.parametrize(
    "raw_value, frequency_qualifier, percentage, quotient, count, total",
    [
        # basic guard rails
        (None, None, None, None, None, None),
        ("", None, None, None, None, None),
        # frequencies given as percentages should be mapped to HPO terms
        ("0%", None, 0.0, 0.0, None, None),
        ("3%", None, 3.0, 0.03, None, None),
        ("20%", None, 20.0, 0.2, None, None),
        ("60%", None, 60.0, 0.6, None, None),
        ("90%", None, 90.0, 0.9, None, None),
        ("100%", None, 100.0, 1.0, None, None),
        # frequencies given as fractions should be mapped to HPO terms, and have percentages and quotients
        ("0/100", None, 0.0, 0.0, 0, 100),
        ("3/100", None, 3.0, 0.03, 3, 100),
        ("5/20", None, 25.0, 0.25, 5, 20),
        ("60/100", None, 60.0, 0.6, 60, 100),
        ("90/100", None, 90.0, 0.9, 90, 100),
        ("100/100", None, 100.0, 1.0, 100, 100),
        # frequencies given as HPO qualifiers should be mapped to percentages only for 0 and 100
        ("HP:0040285", "HP:0040285", None, None, None, None),
        ("HP:0040284", "HP:0040284", None, None, None, None),
        ("HP:0040283", "HP:0040283", None, None, None, None),
        ("HP:0040282", "HP:0040282", None, None, None, None),
        ("HP:0040281", "HP:0040281", None, None, None, None),
        ("HP:0040280", "HP:0040280", None, None, None, None),
    ],
)
def test_frequency_result(raw_value, frequency_qualifier, percentage, quotient, count, total):
    frequency = phenotype_frequency_to_hpo_term(raw_value)
    assert frequency.frequency_qualifier == frequency_qualifier
    assert frequency.has_percentage == percentage
    assert frequency.has_quotient == quotient
    assert frequency.has_count == count
    assert frequency.has_total == total
