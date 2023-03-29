"""
HPOA processing utility methods
"""
from typing import Optional, List, Dict, Tuple, NamedTuple


from loguru import logger


class FrequencyHpoTerm(NamedTuple):
    curie: str
    name: str
    lower: float
    upper: float


# HPO "HP:0040279": representing the frequency of phenotypic abnormalities within a patient cohort.
hpo_term_to_frequency: Dict = {
    "HP:0040280": FrequencyHpoTerm("HP:0040280", "Obligate", 100.0, 100.0),  # Always present,i.e. in 100% of the cases.
    "HP:0040281": FrequencyHpoTerm("HP:0040281", "Very frequent", 80.0, 99.0),  # Present in 80% to 99% of the cases.
    "HP:0040282": FrequencyHpoTerm("HP:0040282", "Frequent", 30.0, 79.0),       # Present in 30% to 79% of the cases.
    "HP:0040283": FrequencyHpoTerm("HP:0040283", "Occasional", 5.0, 29.0),      # Present in 5% to 29% of the cases.
    "HP:0040284": FrequencyHpoTerm("HP:0040284", "Very rare", 1.0, 4.0),        # Present in 1% to 4% of the cases.
    "HP:0040285": FrequencyHpoTerm("HP:0040285", "Excluded", 0.0, 0.0)          # Present in 0% of the cases.
}


def get_hpo_term(hpo_id: str) -> Optional[FrequencyHpoTerm]:
    if hpo_id:
        return hpo_term_to_frequency[hpo_id] if hpo_id in hpo_term_to_frequency else None
    else:
        return None


def map_percentage_frequency_to_hpo_term(percentage_or_quotient: float) -> Optional[FrequencyHpoTerm]:
    """
    Map phenotypic percentage frequency to a corresponding HPO term corresponding to (HP:0040280 to HP:0040285).

    :param percentage_or_quotient: int, should be in range 0.0 to 100.0
    :return: str, HPO term mapping onto percentage range of term definition; None if outside range
    """
    for hpo_id, details in hpo_term_to_frequency.items():
        if details.lower <= percentage_or_quotient <= details.upper:
            return details

    return None


def phenotype_frequency_to_hpo_term(
        frequency_field: Optional[str]
) -> Optional[Tuple[FrequencyHpoTerm, Optional[float], Optional[float]]]:
    """
Maps a raw frequency field onto HPO, for consistency. This is needed since the **phenotypes.hpoa**
file field #8 which tracks phenotypic frequency, has a variable values. There are three allowed options for this field:

1. A term-id from the HPO-sub-ontology below the term “Frequency” (HP:0040279). (since December 2016 ; before was a mixture of values). The terms for frequency are in alignment with Orphanet;
2. A percentage value such as 17%.
3. A count of patients affected within a cohort. For instance, 7/13 would indicate that 7 of the 13 patients with the specified disease were found to have the phenotypic abnormality referred to by the HPO term in question in the study referred to by the DB_Reference;

    :param frequency_field: str, raw frequency value in one of the three above forms
    :return: Optional[FrequencyHpoTerm, float, float], raw frequency mapped to its HPO term, quotient or percentage
             respectively (as applicable); return None if unmappable;
             percentage and/or quotient returned are also None, if not applicable
    """
    hpo_term: Optional[FrequencyHpoTerm] = None
    quotient: Optional[float] = None
    percentage: Optional[float] = None
    if frequency_field:
        try:
            # Pass HPO term format 1 through but map formats 2 and 3 into HP terms
            if frequency_field.startswith("HP:"):
                hpo_term = get_hpo_term(hpo_id=frequency_field)

            elif frequency_field.endswith("%"):
                percentage = float(frequency_field.removesuffix("%"))
                hpo_term = map_percentage_frequency_to_hpo_term(percentage)

            else:
                # assume a ratio
                ratio_parts = frequency_field.split("/")
                quotient = float(int(ratio_parts[0]) / int(ratio_parts[1]))
                hpo_term = map_percentage_frequency_to_hpo_term(quotient*100.0)

        except Exception:
            # expected ratio not recognized
            logger.error(f"hpoa_frequency(): invalid frequency ratio '{frequency_field}'")
            frequency_field = None
    else:
        # may be None, if original field was empty or has an invalid value
        return None

    if not hpo_term:
        # Input value could not be classified
        return None

    return hpo_term, percentage, quotient   # percentage and/or quotient will also be None if not applicable
