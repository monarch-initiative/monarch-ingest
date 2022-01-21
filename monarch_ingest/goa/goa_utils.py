"""
Some Gene Ontology Annotation ingest utility functions.
"""
from typing import Optional, Tuple, Any
import logging

from biolink_model_pydantic.model import (
    Predicate,
    MolecularActivity,
    BiologicalProcess,
    CellularComponent,
    MacromolecularMachineToMolecularActivityAssociation,
    MacromolecularMachineToBiologicalProcessAssociation,
    MacromolecularMachineToCellularComponentAssociation
)

logger = logging.getLogger(__name__)
logger.setLevel("DEBUG")


# TODO: replace this workaround dictionary with direct usage of the
#       Pydantic Predicate functionality and the translator_table.yaml
#       Or an external local table file?
_predicate_by_name = {
    "enables": {
        "predicate": Predicate.enables,
        "mapping": "RO:0002327"
    },
    "involved_in": {
        "predicate": Predicate.actively_involved_in,
        "mapping": "RO:0002331"
    },
    "located_in": {
        "predicate": Predicate.located_in,
        "mapping": "RO:0001025"
    },
    "contributes_to": {
        "predicate": Predicate.contributes_to,
        "mapping": "RO:0002326"
    },
    "acts_upstream_of": {
        "predicate": Predicate.acts_upstream_of,
        "mapping": "RO:0002263"
    },
    "part_of": {
        "predicate": Predicate.part_of,
        "mapping": "BFO:0000050"
    },
    "acts_upstream_of_positive_effect": {
        "predicate": Predicate.acts_upstream_of_positive_effect,
        "mapping": "RO:0004034"
    },
    "is_active_in": {
        "mapping": "RO:0002432",
        "predicate": Predicate.actively_involved_in
    },
    "acts_upstream_of_negative_effect": {
        "predicate": Predicate.acts_upstream_of_negative_effect,
        "mapping": "RO:0004035"
    },
    "colocalizes_with": {
        "predicate": Predicate.colocalizes_with,
        "mapping": "RO:0002325"
    },
    "acts_upstream_of_or_within": {
        "predicate": Predicate.acts_upstream_of_or_within,
        "mapping": "RO:0002264"
    },
    "acts_upstream_of_or_within_positive_effect": {
        "predicate": Predicate.acts_upstream_of_or_within_positive_effect,
        "mapping": "RO:0004032"
    },
    "acts_upstream_of_or_within_negative_effect": {
        "predicate": Predicate.acts_upstream_of_or_within_negative_effect,
        "mapping": "RO:0004033"
    }
}


def lookup_predicate(name: str = None) -> Optional[Tuple[str, Any]]:
    """
    :param name: string name of predicate to be looked up
    :return: tuple(Predicate.name, mapping to relation) if available; None otherwise
    """
    if name and name in _predicate_by_name:
        entry = _predicate_by_name[name]
    else:
        logger.error(f"Encountered unknown GAF qualifier '{str(name)}'?")
        return None
    
    return entry["predicate"], entry["mapping"]


_biolink_class_by_go_aspect = {
    "F": (MolecularActivity, MacromolecularMachineToMolecularActivityAssociation),
    "P": (BiologicalProcess, MacromolecularMachineToBiologicalProcessAssociation),
    "C": (CellularComponent, MacromolecularMachineToCellularComponentAssociation)
}


def get_biolink_classes(go_aspect: str) -> Tuple:
    """
    Return a tuple of the Biolink Model Pydantic implementation of the
    NamedThing category-associated 'node' and Association 'edge' classes
    mapping onto the specified Gene Ontology 'aspect':
    one of P (biological process), F (molecular function) or C (cellular component).
    
    :param go_aspect: single character code of GO aspect
    :return: (category, association) tuple of Biolink Model Pydantic classes associated with the given GO aspect
    """
    return _biolink_class_by_go_aspect[go_aspect.upper()]
    
