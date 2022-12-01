from typing import List

import uuid

from koza.cli_runner import get_koza_app
from source_translation import source_map

from biolink.pydanticmodel import GeneToPhenotypicFeatureAssociation

import logging
LOG = logging.getLogger(__name__)

koza_app = get_koza_app("alliance_gene_to_phenotype")

while (row := koza_app.get_row()) is not None:

    gene_ids = koza_app.get_map("alliance-gene")

    if len(row["phenotypeTermIdentifiers"]) == 0:
        LOG.debug("Phenotype ingest record has 0 phenotype terms: " + str(row))

    if len(row["phenotypeTermIdentifiers"]) > 1:
        LOG.debug("Phenotype ingest record has >1 phenotype terms: " + str(row))

    # limit to only genes
    if row["objectId"] in gene_ids.keys() and len(row["phenotypeTermIdentifiers"]) == 1:

        gene_id = row["objectId"]

        phenotypic_feature_id = row["phenotypeTermIdentifiers"][0]["termId"]

        # Remove the extra WB: prefix if necessary
        phenotypic_feature_id = phenotypic_feature_id.replace("WB:WBPhenotype:", "WBPhenotype:")

        source = source_map[row["objectId"].split(':')[0]]

        association = GeneToPhenotypicFeatureAssociation(
            id="uuid:" + str(uuid.uuid1()),
            subject=gene_id,
            predicate="biolink:has_phenotype",
            object=phenotypic_feature_id,
            publications=[row["evidence"]["publicationId"]],
            aggregator_knowledge_source=["infores:monarchinitiative", "infores:alliancegenome"],
            primary_knowledge_source=source
        )

        if "conditionRelations" in row.keys() and row["conditionRelations"] is not None:
            qualifiers: List[str] = []
            for conditionRelation in row["conditionRelations"]:
                for condition in conditionRelation["conditions"]:
                    if condition["conditionClassId"]:
                        qualifier_term = condition["conditionClassId"]
                        qualifiers.append(qualifier_term)

            association.qualifiers = qualifiers

        koza_app.write(association)
