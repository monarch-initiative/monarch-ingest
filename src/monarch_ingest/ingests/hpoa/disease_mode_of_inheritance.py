"""
The [Human Phenotype Ontology](http://human-phenotype-ontology.org) group
curates and assembles over 115,000 annotations to hereditary diseases
using the HPO ontology. Here we create Biolink associations
between diseases and their mode of inheritance.

This parser only processes out the "inheritance" (aspect == 'I') annotation records.

filters:
  - inclusion: 'include'
    column: 'aspect'
    filter_code: 'eq'
    value: 'I'

Usage:
poetry run koza transform \
  --global-table src/monarch_ingest/translation_table.yaml \
  --local-table src/monarch_ingest/ingests/hpoa/hpoa-translation.yaml \
  --source src/monarch_ingest/ingests/hpoa/disease_mode_of_inheritance.yaml \
  --output-format tsv
"""
from typing import List

import uuid

from koza.cli_runner import get_koza_app

from biolink_model.datamodel.pydanticmodel_v2 import DiseaseOrPhenotypicFeatureToGeneticInheritanceAssociation


from loguru import logger

koza_app = get_koza_app("hpoa_disease_mode_of_inheritance")

while (row := koza_app.get_row()) is not None:

  # Object: Actually a Genetic Inheritance (as should be specified by a suitable HPO term)
  # TODO: perhaps load the proper (Genetic Inheritance) node concepts into the Monarch Graph (simply as Ontology terms?).
  hpo_id = row["hpo_id"]

  # We ignore records that don't map to a known HPO term for Genetic Inheritance
  # (as recorded in the locally bound 'hpoa-modes-of-inheritance' table)
  if hpo_id and hpo_id in koza_app.translation_table.local_table:

      # Nodes

      # Subject: Disease
      disease_id = row["database_id"]

      # Predicate (canonical direction)
      predicate = "biolink:has_mode_of_inheritance"

      # Annotations

      # Three letter ECO code to ECO class based on HPO documentation
      evidence_curie = koza_app.translation_table.resolve_term(row["evidence"])

      # Publications
      publications_field: str = row["reference"]
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
          primary_knowledge_source="infores:hpo-annotations"
      )
      koza_app.write(association)

  else:
      logger.warning(f"HPOA ID field value '{str(hpo_id)}' is missing or an invalid disease mode of inheritance?")
