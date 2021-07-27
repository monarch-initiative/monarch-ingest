import uuid

from biolink_model_pydantic.model import (
    Gene,
    GeneToPhenotypicFeatureAssociation,
    PhenotypicFeature,
    Predicate,
)
from koza.manager.data_collector import write
from koza.manager.data_provider import inject_map, inject_row, inject_translation_table

source_name = "gene-to-phenotype"
translation_table = inject_translation_table()
row = inject_row(source_name)

if len(row["phenotypeTermIdentifiers"]) != 1:
    raise ValueError("This import should always have a single phenotype term")

# TODO: need to limit to only genes

pheno_id = row["phenotypeTermIdentifiers"][0]["termId"]
# Remove the extra WB: prefix
pheno_id = pheno_id.replace("WB:WBPhenotype:", "WBPhenotype:")

gene = Gene(id=row["objectId"])
phenotypicFeature = PhenotypicFeature(
    id=pheno_id
)
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
    for conditionRelation in row['conditionRelations']:
        for condition in conditionRelation['conditions']:
            if condition['conditionClassId']:
                qualifiers.append(condition['conditionClassId'])
    association.qualifiers = qualifiers

write(source_name, gene, phenotypicFeature, association)
