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

We are only excludeP associations from the ingest;
keeping 'I' == 'inheritance' and 'C' == 'clinical'

Usage:
poetry run koza transform \
  --global-table monarch_ingest/translation_table.yaml \
  --local-table monarch_ingest/hpoa/hpoa-translation.yaml \
  --source monarch_ingest/hpoa/disease_phenotype.yaml \
  --output-format tsv
"""
from typing import Optional, List

import uuid

from koza.cli_runner import get_koza_app

from biolink.pydanticmodel import (
    Disease,
    DiseaseToPhenotypicFeatureAssociation
)

import logging
LOG = logging.getLogger(__name__)

koza_app = get_koza_app("hpoa_disease_phenotype")
row = koza_app.get_row()

# Nodes
disease_id = row["DatabaseID"]

predicate = "biolink:has_phenotype"

hpo_id = row["HPO_ID"]
mode_of_inheritance: bool = True if hpo_id and hpo_id in koza_app.translation_table.local_table else False

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

# Avoiding creating publication nodes within ingests, at least temporarily
# for pub in publications:
#
#     publication = Publication(
#         id=pub,
#         type=koza_app.translation_table.global_table["publication"],
#     )
#
#     if pub.startswith("PMID:"):
#         # journal article -> IAO:0000013
#         publication.type = koza_app.translation_table.global_table["journal article"]
#
#     elif pub.startswith("ISBN"):
#         # publication -> IAO:0000311
#         publication.type = koza_app.translation_table.global_table["publication"]
#
#     elif pub.startswith("OMIM:"):
#         # web page -> SIO:000302
#         publication.type = koza_app.translation_table.global_table["web page"]
#
#     elif pub.startswith("DECIPHER:"):
#         publication.type = koza_app.translation_table.global_table["web page"]
#
#     elif pub.startswith("ORPHA:"):
#         publication.type = koza_app.translation_table.global_table["web page"]
#
#     elif pub.startswith("http"):
#         publication.type = koza_app.translation_table.global_table["web page"]
#
#     koza_app.write(publication)

if mode_of_inheritance:

    disease = Disease(
        id=disease_id,
        has_attribute=[hpo_id],
        provided_by=["infores:hpoa"]
    )
    koza_app.write(disease)

else:
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
