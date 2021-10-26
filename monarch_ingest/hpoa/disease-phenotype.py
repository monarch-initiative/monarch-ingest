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

We are only including P associations, which are disease to phenotype associations

Usage:
poetry run koza transform \
  --global-table monarch_ingest/translation_table.yaml \
  --local-table monarch_ingest/hpoa/hpoa-translation.yaml \
  --source monarch_ingest/hpoa/disease-phenotype.yaml \
  --output-format tsv
"""

import logging
import uuid
from typing import List

from biolink_model_pydantic.model import (
    Disease,
    DiseaseToPhenotypicFeatureAssociation,
    PhenotypicFeature,
    Predicate,
    Publication
)
from koza.cli_runner import koza_app

LOG = logging.getLogger(__name__)

source_name = "disease-phenotype"
row = koza_app.get_row(source_name)

# Filters

# Skipping NOTs for now but we'll want to come back and add them
# Could also add this to the yaml filters but leaving here as the
# intention is to bring these in
if row['Qualifier'] == 'NOT':
    koza_app.next_row()

# Nodes global to all aspect types
disease = Disease(
    id=row['DatabaseID']
)

# Translations to curies
evidence_curie = koza_app.translation_table.resolve_term(row['Evidence'])
sex_qualifier = koza_app.translation_table.resolve_term(row['Sex'])


# Publications
publications: List[str] = row['Reference'].split(';')
for pub in publications:

    publication = Publication(id=pub)

    if pub.startswith('PMID:'):
        publication.type = koza_app.translation_table.global_table['journal article']

    elif pub.startswith('ISBN'):
        publication.type = koza_app.translation_table.global_table['publication']

    elif pub.startswith('OMIM:'):
        publication.type = koza_app.translation_table.global_table['web page']

    elif pub.startswith('DECIPHER:'):
        publication.type = koza_app.translation_table.global_table['web page']

    elif pub.startswith('ORPHA:'):
        publication.type = koza_app.translation_table.global_table['web page']

    elif pub.startswith('http'):
        publication.type = koza_app.translation_table.global_table['web page']

    koza_app.write(publication)

# Associations

phenotypic_feature = PhenotypicFeature(
    id=row['HPO_ID']
)

association = DiseaseToPhenotypicFeatureAssociation(
    id="uuid:" + str(uuid.uuid1()),
    subject=disease.id,
    predicate=Predicate.has_phenotype,
    object=phenotypic_feature.id,
    relation=koza_app.translation_table.resolve_term("has phenotype"),
    publications=publications,
    has_evidence=evidence_curie,
    sex_qualifier=sex_qualifier,
    onset_qualifier=row['Onset'],
    # Sometimes frequency is a proportion or a percent
    frequency_qualifier=row['Frequency']
)

koza_app.write(association)
