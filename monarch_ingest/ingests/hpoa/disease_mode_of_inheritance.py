"""
The [Human Phenotype Ontology](http://human-phenotype-ontology.org) group
curates and assembles over 115,000 annotations to hereditary diseases
using the HPO ontology. Here we create Biolink associations
between diseases and phenotypic features, together with their evidence,
and age of onset and frequency (if known).

The parser currently only processes the "inheritance" annotations.

filters:
  - inclusion: 'include'
    column: 'Aspect'
    filter_code: 'eq'
    value: 'I'

We are only keeping 'I' == 'inheritance' records.

Usage:
poetry run koza transform \
  --global-table monarch_ingest/translation_table.yaml \
  --local-table monarch_ingest/hpoa/hpoa-translation.yaml \
  --source monarch_ingest/hpoa/disease_mode_of_inheritance.yaml \
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

koza_app = get_koza_app("hpoa_disease_mode_of_inheritance")

row = koza_app.get_row()

# Nodes
disease_id = row["DatabaseID"]

hpo_id = row["HPO_ID"]
assert hpo_id, "HPOA Disease to Phenotype has missing HP ontology ('HPO_ID') field identifier?"

if hpo_id in koza_app.translation_table.local_table:

    disease = Disease(
        id=disease_id,
        has_attribute=[hpo_id],
        provided_by=["infores:hpoa"]
    )
    koza_app.write(disease)
