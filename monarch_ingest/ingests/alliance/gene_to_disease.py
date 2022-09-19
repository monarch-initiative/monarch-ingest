import logging
import uuid

from koza.cli_runner import get_koza_app
from source_translation import source_map

from biolink.pydanticmodel import GeneToDiseaseAssociation

LOG = logging.getLogger(__name__)

koza_app = get_koza_app("alliance_gene_to_disease")

row = koza_app.get_row()
associationType = row["AssociationType"]

source = source_map[row["Source"]]

predicate = None
negated = False

if associationType == "is_model_of":
    predicate = "biolink:model_of"
elif associationType == "is_marker_of":
    predicate = "biolink:biomarker_for"
elif associationType == "is_implicated_in":
    predicate = "biolink:contributes_to"
elif associationType == "is_not_implicated_in":
    predicate = "biolink:contributes_to"
    negated = True

# elif associationType == 'biomarker_via_orthology':
#    likely this should be biomarker_for with some extra qualifier
# elif associationType == 'implicated_via_orthology':
#    likely this should be contributes_to with some extra qualifier

if row["DBobjectType"] == "gene" and predicate:

    gene_id = row["DBObjectID"]

    disease_id = row["DOID"]

    association = GeneToDiseaseAssociation(
        id="uuid:" + str(uuid.uuid1()),
        subject=gene_id,
        predicate=predicate,
        object=disease_id,
        publications=[row["Reference"]],
        aggregator_knowledge_source=["infores:monarchinitiative", "infores:alliancegenome"],
        primary_knowledge_source=source
    )

    if negated:
        association.negated = True

    # TODO: Handle ECO terms in row["EvidenceCode"]

    koza_app.write(association)
