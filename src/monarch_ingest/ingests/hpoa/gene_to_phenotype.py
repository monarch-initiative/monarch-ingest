"""
Usage:
poetry run koza transform \
  --source src/monarch_ingest/ingests/hpoa/gene_to_phenotype.yaml \
  --output-format tsv
"""

import uuid

from koza.cli_utils import get_koza_app

from biolink_model.datamodel.pydanticmodel_v2 import (
    GeneToPhenotypicFeatureAssociation,
    KnowledgeLevelEnum,
    AgentTypeEnum,
)

koza_app = get_koza_app("hpoa_gene_to_phenotype")

while (row := koza_app.get_row()) is not None:
    gene_id = "NCBIGene:" + row["ncbi_gene_id"]
    phenotype_id = row["hpo_id"]

    association = GeneToPhenotypicFeatureAssociation(
        id="uuid:" + str(uuid.uuid1()),
        subject=gene_id,
        predicate="biolink:has_phenotype",
        object=phenotype_id,
        aggregator_knowledge_source=["infores:monarchinitiative"],
        primary_knowledge_source="infores:hpo-annotations",
        knowledge_level=KnowledgeLevelEnum.logical_entailment,
        agent_type=AgentTypeEnum.automated_agent,
    )

    koza_app.write(association)
