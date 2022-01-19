import uuid
from typing import Optional

from biolink_model_pydantic.model import (
    Gene,
    Predicate,
    MolecularActivity,
    BiologicalProcess,
    CellularComponent,
    MacromolecularMachineToMolecularActivityAssociation,
    MacromolecularMachineToBiologicalProcessAssociation,
    MacromolecularMachineToCellularComponentAssociation
)

from koza.cli_runner import koza_app


def molecular_function(go_id: str) -> Optional[MolecularActivity]:
    """

    :param go_id:
    :return:
    """
    return None


def biological_process(go_id: str) -> Optional[BiologicalProcess]:
    """

    :param go_id:
    :return:
    """
    return None


def cellular_component(go_id: str)-> Optional[CellularComponent]:
    """

    :param go_id:
    :return:
    """
    return None


row = koza_app.get_row()

db = row['DB']
db_object_id = row['DB_Object_ID']
db_id = f"{db}:{db_object_id}"

# TODO: need to remap this DB id onto a proper gene id (db_id is probably probably a uniprot id?)
gene_id = db_id

ncbitaxon = row['Taxon']

# TODO: probably wrong right now.. not an Entrez ID?
gene= Gene(id=gene_id, in_taxon=ncbitaxon, source="entrez")

association = None  # in case of a go_id which doesn't hit anything?

go_id = row['GO_ID']
# TODO: need to figure out which GO identifier space this term belongs to:
#       molecular_function - child of GO:0003674,
#       biological_process - child of GO:0008150 OR
#       cellular_component - child of GO:0005575
#       Note that since GO is a DAG, these terms can have multiple parents...how do we handle this?

# First naive iteration... probably wrong! TODO: every 'go_term' may be an array of terms(?)
go_term = molecular_function(go_id)
if go_term:
    association = MacromolecularMachineToMolecularActivityAssociation(
        id="uuid:" + str(uuid.uuid1()),
        subject=gene.id,
        object=go_term.id,
        predicate=Predicate.related_to,
        relation=koza_app.translation_table.global_table['related to'],
        source="infores:goa",
    )
else:
    go_term = biological_process(go_id)
    if go_term:
        association = MacromolecularMachineToBiologicalProcessAssociation(
            id="uuid:" + str(uuid.uuid1()),
            subject=gene.id,
            object=go_term.id,
            predicate=Predicate.participates_in,
            relation=koza_app.translation_table.global_table['participates in'],
            source="infores:goa",
        )
    else:
        go_term = cellular_component(go_id)
        if go_term:
            association = MacromolecularMachineToCellularComponentAssociation(
                id="uuid:" + str(uuid.uuid1()),
                subject=gene.id,
                object=go_term.id,
                predicate=Predicate.located_in,
                relation=koza_app.translation_table.global_table['located in'],
                source="infores:goa",
            )
        else:
            pass  # no hit? not sure what error condition to trigger here... maybe nothing?

if association:
    koza_app.write(gene_id, go_id, association)
