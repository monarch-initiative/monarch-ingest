"""
The [Human Phenotype Ontology](http://human-phenotype-ontology.org) group
curates and assembles over 115,000 annotations to hereditary diseases
using the HPO ontology. Here we create Biolink associations
between diseases and their mode of inheritance.

This parser only processes out the "inheritance" (Aspect == 'I') annotation records.

filters:
  - inclusion: 'include'
    column: 'Aspect'
    filter_code: 'eq'
    value: 'I'

Usage:
poetry run koza transform \
  --global-table monarch_ingest/translation_table.yaml \
  --local-table monarch_ingest/ingests/hpoa/hpoa-translation.yaml \
  --source monarch_ingest/ingests/hpoa/disease_mode_of_inheritance.yaml \
  --output-format tsv
"""
from typing import List

import uuid

from koza.cli_runner import get_koza_app

from biolink.pydanticmodel import DiseaseOrPhenotypicFeatureToGeneticInheritanceAssociation

import logging
LOG = logging.getLogger(__name__)

koza_app = get_koza_app("hpoa_disease_mode_of_inheritance")

row = koza_app.get_row()

# Object: Actually a Genetic Inheritance (as should be specified by a suitable HPO term)
# TODO: perhaps load the proper (Genetic Inheritance) node concepts into the Monarch Graph (simply as Ontology terms?).
hpo_id = row["HPO_ID"]

# We ignore records that don't map to a known HPO term for Genetic Inheritance
# (as recorded in the locally bound 'hpoa-modes-of-inheritance' table)
if hpo_id and hpo_id in koza_app.translation_table.local_table:

    # Nodes

    # Subject: Disease
    disease_id = row["DatabaseID"]

    # Predicate (canonical direction)
    predicate = "biolink:has_mode_of_inheritance"

    # Annotations

    # Three letter ECO code to ECO class based on HPO documentation
    evidence_curie = koza_app.translation_table.resolve_term(row["Evidence"])

    # Publications
    publications_field: str = row["Reference"]
    publications: List[str] = publications_field.split(";")

    # Filter out some weird NCBI web endpoints
    publications = [p for p in publications if not p.startswith("http")]

    # Association/Edge
    association = DiseaseOrPhenotypicFeatureToGeneticInheritanceAssociation(
        id="uuid:" + str(uuid.uuid1()),
        subject=disease_id,
        predicate=predicate,
        object=hpo_id,
        publications=publications,
        has_evidence=[evidence_curie],
        aggregator_knowledge_source=["infores:monarchinitiative"],
        primary_knowledge_source="infores:hpoa"
    )
    koza_app.write(association)

else:
    LOG.warning(f"HPOA ID field value '{str(hpo_id)}' is missing or an invalid disease mode of inheritance?")
