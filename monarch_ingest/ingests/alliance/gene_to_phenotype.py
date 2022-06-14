import logging
import uuid

from koza.cli_runner import koza_app
from source_translation import source_map

from monarch_ingest.model.biolink import Gene, GeneToPhenotypicFeatureAssociation, PhenotypicFeature

LOG = logging.getLogger(__name__)

source_name = "alliance_gene_to_phenotype"

row = koza_app.get_row(source_name)
gene_ids = koza_app.get_map("alliance-gene")

if len(row["phenotypeTermIdentifiers"]) == 0:
    LOG.debug("Phenotype ingest record has 0 phenotype terms: " + str(row))

if len(row["phenotypeTermIdentifiers"]) > 1:
    LOG.debug("Phenotype ingest record has >1 phenotype terms: " + str(row))

# limit to only genes
if row["objectId"] in gene_ids.keys() and len(row["phenotypeTermIdentifiers"]) == 1:

    source = source_map[row["objectId"].split(':')[0]]

    pheno_id = row["phenotypeTermIdentifiers"][0]["termId"]
    # Remove the extra WB: prefix if necessary
    pheno_id = pheno_id.replace("WB:WBPhenotype:", "WBPhenotype:")

    gene = Gene(id=row["objectId"], source=source)
    phenotypicFeature = PhenotypicFeature(id=pheno_id, source=source)
    #relation = koza_app.translation_table.resolve_term("has phenotype"),
    association = GeneToPhenotypicFeatureAssociation(
        id="uuid:" + str(uuid.uuid1()),
        subject=gene.id,
        predicate="biolink:has_phenotype",
        object=phenotypicFeature.id,
        publications=[row["evidence"]["publicationId"]],
        aggregating_knowledge_source=["infores:monarchinitiative", "infores:alliancegenome"],
        primary_knowledge_source=source
    )

    if "conditionRelations" in row.keys() and row["conditionRelations"] is not None:
        qualifiers = []
        for conditionRelation in row["conditionRelations"]:
            for condition in conditionRelation["conditions"]:
                if condition["conditionClassId"]:
                    qualifiers.append(condition["conditionClassId"])
        association.qualifiers = qualifiers

    koza_app.write(association)
