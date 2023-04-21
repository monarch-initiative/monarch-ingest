"""
The [Human Phenotype Ontology](http://human-phenotype-ontology.org) group
curates and assembles over 115,000 annotations to hereditary diseases
using the HPO ontology. Here we create Biolink associations
between diseases and phenotypic features, together with their evidence,
and age of onset and frequency (if known).

The parser currently only processes the "abnormal" annotations.
Association to "remarkable normality" will be added in the near future.

filters:
  - inclusion: 'include'
    column: 'Aspect'
    filter_code: 'eq'
    value: 'P'

We are only keeping 'P' == 'phenotypic anomaly' records.

Usage:
poetry run koza transform \
  --global-table src/monarch_ingest/translation_table.yaml \
  --local-table src/monarch_ingest/ingests/hpoa/hpoa-translation.yaml \
  --source src/monarch_ingest/ingests/hpoa/disease_phenotype.yaml \
  --output-format tsv
"""
from typing import Optional, List, Tuple

import uuid

from koza.cli_runner import get_koza_app

from biolink.pydanticmodel import DiseaseToPhenotypicFeatureAssociation
from monarch_ingest.ingests.hpoa.hpoa_utils import phenotype_frequency_to_hpo_term, FrequencyHpoTerm


from loguru import logger

koza_app = get_koza_app("hpoa_disease_phenotype")

while (row := koza_app.get_row()) is not None:

    # Nodes
    disease_id = row["database_id"]

    predicate = "biolink:has_phenotype"

    hpo_id = row["hpo_id"]
    assert hpo_id, "HPOA Disease to Phenotype has missing HP ontology ('HPO_ID') field identifier?"

    # Predicate negation
    negated: Optional[bool]
    if row["qualifier"] == "NOT":
        negated = True
    else:
        negated = None

    # Annotations

    # Translations to curies
    # Three letter ECO code to ECO class based on hpo documentation
    evidence_curie = koza_app.translation_table.resolve_term(row["evidence"])

    # female -> PATO:0000383
    # male -> PATO:0000384
    sex: Optional[str] = row["sex"]  # may be translated by local table
    sex_qualifier = (
        koza_app.translation_table.resolve_term(sex) if sex else None
    )

    onset = row["onset"]

    # Raw frequencies - HPO term curies, ratios, percentages - normalized to HPO terms
    frequency_field = row["frequency"]
    frequency_hpo: Optional[FrequencyHpoTerm] = None
    frequency_percentage: Optional[float] = None
    frequency_quotient: Optional[float] = None
    frequency_parsed: Optional[Tuple[FrequencyHpoTerm, float, float]] = \
        phenotype_frequency_to_hpo_term(frequency_field=frequency_field)
    if frequency_parsed:
        frequency_hpo, frequency_percentage, frequency_quotient = frequency_parsed

    # Publications
    publications_field: str = row["reference"]
    publications: List[str] = publications_field.split(";")

    # Filter out some weird NCBI web endpoints
    publications = [p for p in publications if not p.startswith("http")]

    # Replace ORPHA prefix with orphanet to match preferred biolink prefix
    publications = [p.replace("ORPHA:", "orphanet:") for p in publications]

    # Association/Edge
    association = DiseaseToPhenotypicFeatureAssociation(
        id="uuid:" + str(uuid.uuid1()),
        subject=disease_id.replace("ORPHA:", "Orphanet:"), # match `Orphanet` as used in Mondo SSSOM
        predicate=predicate,
        negated=negated,
        object=hpo_id,
        publications=publications,
        has_evidence=[evidence_curie],
        sex_qualifier=sex_qualifier,
        onset_qualifier=onset,

        # TODO: not totally sure if HPO term now ought to be assigned to
        #       percentage and quotient frequency values anymore?
        has_percentage=frequency_percentage if frequency_percentage else None,
        has_quotient=frequency_quotient if frequency_quotient else None,
        frequency_qualifier=frequency_hpo.curie if frequency_hpo else None,

        aggregator_knowledge_source=["infores:monarchinitiative"],
        primary_knowledge_source="infores:hpoa"
    )
    koza_app.write(association)
