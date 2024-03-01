"""
HPOA processing utility methods
"""
from typing import Optional, List, Dict, Tuple, NamedTuple


from loguru import logger
from pydantic import BaseModel

from monarch_ingest.constants import INFORES_MEDGEN, INFORES_OMIM, INFORES_ORPHANET, BIOLINK_CAUSES, \
    BIOLINK_CONTRIBUTES_TO, BIOLINK_GENE_ASSOCIATED_WITH_CONDITION


class FrequencyHpoTerm(BaseModel):
    curie: str
    name: str
    lower: float
    upper: float

class Frequency(BaseModel):
    frequency_qualifier: Optional[str] = None
    has_percentage: Optional[float] = None
    has_quotient: Optional[float] = None
    has_count: Optional[int] = None
    has_total: Optional[int] = None
    # convert the fields above to pydantic field declarations

# HPO "HP:0040279": representing the frequency of phenotypic abnormalities within a patient cohort.
hpo_term_to_frequency: Dict = {
    "HP:0040280": FrequencyHpoTerm(curie="HP:0040280", name="Obligate", lower=100.0, upper=100.0),  # Always present,i.e. in 100% of the cases.
    "HP:0040281": FrequencyHpoTerm(curie="HP:0040281", name="Very frequent", lower=80.0, upper=99.0),  # Present in 80% to 99% of the cases.
    "HP:0040282": FrequencyHpoTerm(curie="HP:0040282", name="Frequent", lower=30.0, upper=79.0),       # Present in 30% to 79% of the cases.
    "HP:0040283": FrequencyHpoTerm(curie="HP:0040283", name="Occasional", lower=5.0, upper=29.0),      # Present in 5% to 29% of the cases.
    "HP:0040284": FrequencyHpoTerm(curie="HP:0040284", name="Very rare", lower=1.0, upper=4.0),        # Present in 1% to 4% of the cases.
    "HP:0040285": FrequencyHpoTerm(curie="HP:0040285", name="Excluded", lower=0.0, upper=0.0)          # Present in 0% of the cases.
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
) -> Frequency:
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
    has_count: Optional[int] = None
    has_total: Optional[int] = None
    if frequency_field:
        try:

            if frequency_field.startswith("HP:"):
                hpo_term = get_hpo_term(hpo_id=frequency_field)

            elif frequency_field.endswith("%"):
                percentage = float(frequency_field.removesuffix("%"))
                quotient = percentage / 100.0

            else:
                # assume a ratio
                ratio_parts = frequency_field.split("/")
                has_count = int(ratio_parts[0])
                has_total = int(ratio_parts[1])
                quotient = float(has_count / has_total)
                percentage = quotient * 100.0

        except Exception:
            # expected ratio not recognized
            logger.error(f"hpoa_frequency(): invalid frequency ratio '{frequency_field}'")
            frequency_field = None
    else:
        # may be None, if original field was empty or has an invalid value
        return Frequency()

    return Frequency(frequency_qualifier=hpo_term.curie if hpo_term else None,
                     has_percentage=percentage,
                     has_quotient=quotient,
                     has_count=has_count,
                     has_total=has_total)


def get_knowledge_sources(original_source: str, additional_source: str) -> (str, List[str]):
    """
    Return a tuple of the primary_knowledge_source and original_knowledge_source
    """
    _primary_knowledge_source: str = ""
    _aggregator_knowledge_source: List[str] = []

    if additional_source is not None:
        _aggregator_knowledge_source.append(additional_source)

    if "medgen" in original_source:
        _aggregator_knowledge_source.append(INFORES_MEDGEN)
        _primary_knowledge_source = INFORES_OMIM
    elif "orphadata" in original_source:
        _primary_knowledge_source = INFORES_ORPHANET

    if _primary_knowledge_source == "":
        raise ValueError(f"Unknown knowledge source: {original_source}")

    return _primary_knowledge_source, _aggregator_knowledge_source


def get_predicate(original_predicate: str) -> str:
    """
    Convert the association column into a Biolink Model predicate
    """
    if original_predicate == 'MENDELIAN':
        return BIOLINK_CAUSES
    elif original_predicate == 'POLYGENIC':
        return BIOLINK_CONTRIBUTES_TO
    elif original_predicate == 'UNKNOWN':
        return BIOLINK_GENE_ASSOCIATED_WITH_CONDITION
    else:
        raise ValueError(f"Unknown predicate: {original_predicate}")
