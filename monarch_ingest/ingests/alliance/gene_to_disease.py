import logging
import uuid

from koza.cli_runner import koza_app
from source_translation import source_map

from biolink.pydantic.model import (
    Disease,
    Gene,
    GeneToDiseaseAssociation
)

LOG = logging.getLogger(__name__)

source_name = "alliance_gene_to_disease"

row = koza_app.get_row(source_name)
associationType = row["AssociationType"]

source = source_map[row["Source"]]

predicate = None
relation = None
negated = False

if associationType == "is_model_of":
    predicate = "biolink:model_of"
    relation = koza_app.translation_table.resolve_term("is model of")
elif associationType == "is_marker_of":
    predicate = "biolink:biomarker_for"
    relation = koza_app.translation_table.resolve_term("is marker for")
elif associationType == "is_implicated_in":
    predicate = "biolink:contributes_to"
    relation = koza_app.translation_table.resolve_term("causes_or_contributes")
elif associationType == "is_not_implicated_in":
    predicate = "biolink:contributes_to"
    relation = koza_app.translation_table.resolve_term("causes_or_contributes")
    negated = True

# elif associationType == 'biomarker_via_orthology':
#    likely this should be biomarker_for with some extra qualifier
# elif associationType == 'implicated_via_orthology':
#    likely this should be contributes_to with some extra qualifier

if row["DBobjectType"] == "gene" and predicate:
    gene = Gene(id=row["DBObjectID"], source=source)
    disease = Disease(id=row["DOID"], source=source)

    association = GeneToDiseaseAssociation(
        id="uuid:" + str(uuid.uuid1()),
        subject=gene.id,
        predicate=predicate,
        object=disease.id,
        publications=[row["Reference"]],
        aggregator_knowledge_source=["infores:monarchinitiative", "infores:alliancegenome"],
        primary_knowledge_source=source
    )

    if negated:
        association.negated = True

    # TODO: Handle ECO terms in row["EvidenceCode"]

    koza_app.write(association)
