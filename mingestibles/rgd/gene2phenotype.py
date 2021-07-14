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
map = inject_map("rgd-gene")
row = inject_row(source_name)

internal_id = row["objectId"].replace("RGD:", "")

if internal_id in map.keys() and map[internal_id]['DB_Object_Type'] == 'gene':

    if len(row["phenotypeTermIdentifiers"]) != 1:
        raise ValueError("This import should always have a single phenotype term")

    if "conditionRelations" in row.keys() and row["conditionRelations"] is not None:
        raise ValueError(
            "This import should never have phenotypes with experimental conditions"
        )

    gene = Gene(id=row["objectId"])
    phenotypicFeature = PhenotypicFeature(
        id=row["phenotypeTermIdentifiers"][0]["termId"]
    )
    association = GeneToPhenotypicFeatureAssociation(
        id="uuid:" + str(uuid.uuid1()),
        subject=gene.id,
        predicate=Predicate.has_phenotype,
        object=phenotypicFeature.id,
        relation=translation_table.resolve_term("has phenotype"),
        publications=[row["evidence"]["publicationId"]],
    )
    write(source_name, gene, phenotypicFeature, association)

