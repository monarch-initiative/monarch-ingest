"""
Usage:
poetry run koza transform \
  --source monarch_ingest/ingests/hpoa/gene_to_phenotype.yaml \
  --output-format tsv
"""
import uuid
from typing import Optional

from koza.cli_runner import get_koza_app

from biolink.pydanticmodel import GeneToPhenotypicFeatureAssociation

from monarch_ingest.ingests.hpoa.hpoa_utils import phenotype_frequency_to_hpo_term, FrequencyHpoTerm

koza_app = get_koza_app("hpoa_gene_to_phenotype")

while (row := koza_app.get_row()) is not None:

    gene_id = "NCBIGene:" + row["entrez-gene-id"]
    phenotype_id = row["HPO-Term-ID"]
    disease_id = row["disease-ID for link"]
    frequency_hpo: Optional[FrequencyHpoTerm] = \
        phenotype_frequency_to_hpo_term(frequency_field=row["Frequency-HPO"])
    qualifiers = [disease_id]
    evidence = [row["G-D source"]]

    association = GeneToPhenotypicFeatureAssociation(
        id="uuid:" + str(uuid.uuid1()),
        subject=gene_id,
        predicate="biolink:has_phenotype",
        object=phenotype_id,
        qualifiers=qualifiers,
        frequency_qualifier=frequency_hpo.curie,
        has_evidence=evidence,
        aggregator_knowledge_source=["infores:monarchinitiative"],
        primary_knowledge_source="infores:hpoa"
    )

    koza_app.write(association)
