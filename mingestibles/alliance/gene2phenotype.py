import logging
import uuid

from biolink_model_pydantic.model import (
    Gene,
    GeneToPhenotypicFeatureAssociation,
    PhenotypicFeature,
    Predicate,
)
from koza.manager.data_collector import write
from koza.manager.data_provider import inject_map, inject_row, inject_translation_table

LOG = logging.getLogger(__name__)

source_name = "gene-to-phenotype"
translation_table = inject_translation_table()
row = inject_row(source_name)
gene_ids = inject_map("alliance-gene")


if len(row["phenotypeTermIdentifiers"]) == 0:
    LOG.warning("Phenotype ingest record has 0 phenotype terms: " + str(row))

if len(row["phenotypeTermIdentifiers"]) > 1:
    LOG.warning("Phenotype ingest record has >1 phenotype terms: " + str(row))

# limit to only genes
if row["objectId"] in gene_ids.keys() and len(row["phenotypeTermIdentifiers"]) == 1:

    pheno_id = row["phenotypeTermIdentifiers"][0]["termId"]
    # Remove the extra WB: prefix if necessary
    pheno_id = pheno_id.replace("WB:WBPhenotype:", "WBPhenotype:")

    gene = Gene(id=row["objectId"])
    phenotypicFeature = PhenotypicFeature(id=pheno_id)
    association = GeneToPhenotypicFeatureAssociation(
        id="uuid:" + str(uuid.uuid1()),
        subject=gene.id,
        predicate=Predicate.has_phenotype,
        object=phenotypicFeature.id,
        relation=translation_table.resolve_term("has phenotype"),
        publications=[row["evidence"]["publicationId"]],
    )

    if "conditionRelations" in row.keys() and row["conditionRelations"] is not None:
        qualifiers = []
        for conditionRelation in row["conditionRelations"]:
            for condition in conditionRelation["conditions"]:
                if condition["conditionClassId"]:
                    qualifiers.append(condition["conditionClassId"])
        association.qualifiers = qualifiers

    write(source_name, gene, phenotypicFeature, association)
