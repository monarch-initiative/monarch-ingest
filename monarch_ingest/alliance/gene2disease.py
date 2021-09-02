import logging
import uuid

from biolink_model_pydantic.model import (
    Disease,
    Gene,
    GeneToDiseaseAssociation,
    Predicate,
)
from koza.manager.data_collector import write
from koza.manager.data_provider import inject_row, inject_translation_table

LOG = logging.getLogger(__name__)

source_name = "gene-to-disease"
translation_table = inject_translation_table()
row = inject_row(source_name)

associationType = row["AssociationType"]

predicate = None
relation = None
negated = False

if associationType == "is_model_of":
    predicate = Predicate.model_of
    relation = translation_table.resolve_term("is model of")
elif associationType == "is_marker_of":
    predicate = Predicate.biomarker_for
    relation = translation_table.resolve_term("is marker for")
elif associationType == "is_implicated_in":
    predicate = Predicate.contributes_to
    relation = translation_table.resolve_term("causes_or_contributes")
elif associationType == "is_not_implicated_in":
    predicate = Predicate.contributes_to
    relation = translation_table.resolve_term("causes_or_contributes")
    negated = True

# elif associationType == 'biomarker_via_orthology':
#    likely this should be biomarker_for with some extra qualifier
# elif associationType == 'implicated_via_orthology':
#    likely this should be contributes_to with some extra qualifier

if row["DBobjectType"] == "gene" and predicate:
    gene = Gene(id=row["DBObjectID"])
    disease = Disease(id=row["DOID"])

    association = GeneToDiseaseAssociation(
        id="uuid:" + str(uuid.uuid1()),
        subject=gene.id,
        predicate=predicate,
        object=disease.id,
        publications=[row["Reference"]],
        relation=relation,
        source=row["Source"],
    )

    if negated:
        association.negated = True

    write(source_name, gene, disease, association)
