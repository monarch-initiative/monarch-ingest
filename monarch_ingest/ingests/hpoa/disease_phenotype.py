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
  --global-table monarch_ingest/translation_table.yaml \
  --local-table monarch_ingest/ingests/hpoa/hpoa-translation.yaml \
  --source monarch_ingest/ingests/hpoa/disease_phenotype.yaml \
  --output-format tsv
"""
from typing import Optional, List

import uuid

from koza.cli_runner import get_koza_app

from biolink.pydanticmodel import DiseaseToPhenotypicFeatureAssociation

import logging
LOG = logging.getLogger(__name__)

koza_app = get_koza_app("hpoa_disease_phenotype")

while (row := koza_app.get_row()) is not None:

    # Nodes
    disease_id = row["DatabaseID"]

    predicate = "biolink:has_phenotype"

    hpo_id = row["HPO_ID"]
    assert hpo_id, "HPOA Disease to Phenotype has missing HP ontology ('HPO_ID') field identifier?"

    # Predicate negation
    negated: Optional[bool]
    if row["Qualifier"] == "NOT":
        negated = True
    else:
        negated = None

    # Annotations

    # Translations to curies
    # Three letter ECO code to ECO class based on hpo documentation
    evidence_curie = koza_app.translation_table.resolve_term(row["Evidence"])

    # female -> PATO:0000383
    # male -> PATO:0000384
    sex: Optional[str] = row["Sex"]  # may be translated by local table
    sex_qualifier = (
        koza_app.translation_table.resolve_term(sex) if sex else None
    )

    onset = row["Onset"]

    frequency_qualifier = row["Frequency"]

    # Publications
    publications_field: str = row["Reference"]
    publications: List[str] = publications_field.split(";")

    # Filter out some weird NCBI web endpoints
    publications = [p for p in publications if not p.startswith("http")]

    # Association/Edge
    association = DiseaseToPhenotypicFeatureAssociation(
        id="uuid:" + str(uuid.uuid1()),
        subject=disease_id,
        predicate=predicate,
        negated=negated,
        object=hpo_id,
        publications=publications,
        has_evidence=[evidence_curie],
        sex_qualifier=sex_qualifier,
        onset_qualifier=onset,
        frequency_qualifier=frequency_qualifier,
        aggregator_knowledge_source=["infores:monarchinitiative"],
        primary_knowledge_source="infores:hpoa"
    )
    koza_app.write(association)
