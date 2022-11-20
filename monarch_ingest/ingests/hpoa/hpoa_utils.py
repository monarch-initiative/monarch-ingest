"""
HPOA processing utility methods
"""
from typing import Optional, List, Dict, Tuple, NamedTuple
import logging

logger = logging.getLogger(__file__)


class FrequencyHpoTerm(NamedTuple):
    curie: str
    name: str
    lower: int
    upper: int


# HPO "HP:0040279": representing the frequency of phenotypic abnormalities within a patient cohort.
hpo_term_to_frequency: Dict = {
    "HP:0040280": FrequencyHpoTerm("HP:0040280", "Obligate", 100, 100),     # Always present, i.e. in 100% of the cases.
    "HP:0040281": FrequencyHpoTerm("HP:0040281", "Very frequent", 80, 99),  # Present in 80% to 99% of the cases.
    "HP:0040282": FrequencyHpoTerm("HP:0040282", "Frequent", 30, 79),       # Present in 30% to 79% of the cases.
    "HP:0040283": FrequencyHpoTerm("HP:0040283", "Occasional", 5, 29),      # Present in 5% to 29% of the cases.
    "HP:0040284": FrequencyHpoTerm("HP:0040284", "Very rare", 1, 4),        # Present in 1% to 4% of the cases.
    "HP:0040285": FrequencyHpoTerm("HP:0040285", "Excluded", 0, 0)          # Present in 0% of the cases.
}


def get_hpo_term(hpo_id: str) -> Optional[FrequencyHpoTerm]:
    if hpo_id:
        return hpo_term_to_frequency[hpo_id] if hpo_id in hpo_term_to_frequency else None
    else:
        return None


def map_percentage_frequency_to_hpo_term(percentage: int) -> Optional[FrequencyHpoTerm]:
    """
    Map phenotypic percentage frequency to a corresponding HPO term corresponding to (HP:0040280 to HP:0040285).

    :param percentage: int, should be in range 0 to 100
    :return: str, HPO term mapping onto percentage range of term definition; None if outside range
    """
    for hpo_id, details in hpo_term_to_frequency.items():
        if details.lower <= percentage <= details.upper:
            return details

    return None


def phenotype_frequency_to_hpo_term(frequency_field: Optional[str]) -> Optional[FrequencyHpoTerm]:
    """
Maps a raw frequency field onto HPO, for consistency. This is needed since the **phenotypes.hpoa** file field #8 which tracks phenotypic frequency, has a variable values. There are three allowed options for this field:

1. A term-id from the HPO-sub-ontology below the term “Frequency” (HP:0040279). (since December 2016 ; before was a mixture of values). The terms for frequency are in alignment with Orphanet;
2. A count of patients affected within a cohort. For instance, 7/13 would indicate that 7 of the 13 patients with the specified disease were found to have the phenotypic abnormality referred to by the HPO term in question in the study referred to by the DB_Reference;
3. A percentage value such as 17%.

    :param frequency_field: str, raw frequency value in one of the three above forms
    :return: Optional[FrequencyHpoTerm], raw frequency mapped to its HPO term; None if unsuccessful
    """
    hpo_term: Optional[FrequencyHpoTerm] = None
    if frequency_field:
        # Pass HPO term format 1 through but map formats 2 and 3 into HP terms
        if frequency_field.startswith("HP:"):
            hpo_term = get_hpo_term(hpo_id=frequency_field)
        elif frequency_field.endswith("%"):
            percentage: int = int(frequency_field.removesuffix("%"))
            hpo_term = map_percentage_frequency_to_hpo_term(percentage)
        else:
            # assume a ratio
            try:
                ratio_parts = frequency_field.split("/")
                percentage: int = round((int(ratio_parts[0]) / int(ratio_parts[1]))*100)
                hpo_term = map_percentage_frequency_to_hpo_term(percentage)
            except Exception:
                # expected ratio not recognized
                logger.error(f"hpoa_frequency(): invalid frequency ratio '{frequency_field}'")
                frequency_field = None

    return hpo_term   # may be None, if original field was empty or has an invalid value
