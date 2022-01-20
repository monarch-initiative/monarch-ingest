"""
Some Gene Ontology Annotation ingest utility functions.
"""
from typing import Optional, Tuple, Any

from biolink_model_pydantic.model import (
    Predicate,
    MolecularActivity,
    BiologicalProcess,
    CellularComponent
)


def molecular_function(go_id: str) -> Optional[MolecularActivity]:
    """
    :param go_id: specified GO identifier
    :return: MolecularActivity object corresponding to the specified GO identifier
    """
    return None


def biological_process(go_id: str) -> Optional[BiologicalProcess]:
    """
    :param go_id: specified GO identifier
    :return: BiologicalProcess object corresponding to the specified GO identifier
    """
    return None


def cellular_component(go_id: str) -> Optional[CellularComponent]:
    """
    :param go_id: specified GO identifier
    :return: CellularComponent object corresponding to the specified GO identifier
    """
    return None


# TODO: replace this workaround dictionary with direct usage of the
#       Pydantic Predicate functionality and the translator_table.yaml
_predicate_by_name = {
    "related_to": {
        "mapping": "skos:relatedMatch",
        "predicate": Predicate.related_to
    },
    "enables": {
        "mapping": "RO:0002327",
        "predicate": Predicate.enables
    },
    "involved_in": {
        "mapping": "RO:0002331",
        "predicate": Predicate.actively_involved_in
    },
    "located_in": {
        "mapping": "RO:0001025",
        "predicate": Predicate.located_in
    },
    "contributes_to": {
        "mapping": "RO:0002326",
        "predicate": Predicate.contributes_to
    },
    "acts_upstream_of": {
        "mapping": "RO:0002263",
        "predicate": Predicate.acts_upstream_of
    },
    "part_of": {
        "mapping": "",
        "predicate": Predicate.part_of
    },
    "acts_upstream_of_positive_effect": {
        "mapping": "RO:0004034",
        "predicate": Predicate.acts_upstream_of_positive_effect
    },
    "is_active_in": {
        "mapping": "RO:0002432",
        "predicate": Predicate.actively_involved_in
    },
    "acts_upstream_of_negative_effect": {
        "mapping": "RO:0004035",
        "predicate": Predicate.acts_upstream_of_negative_effect
    },
    "colocalizes_with": {
        "mapping": "RO:0002325",
        "predicate": Predicate.colocalizes_with
    },
    "acts_upstream_of_or_within": {
        "mapping": "RO:0002264",
        "predicate": Predicate.acts_upstream_of_or_within
    },
    "acts_upstream_of_or_within_positive_effect": {
        "mapping": "RO:0004032",
        "predicate": Predicate.acts_upstream_of_or_within_positive_effect
    },
    "acts_upstream_of_or_within_negative_effect": {
        "mapping": "RO:0004033",
        "predicate": Predicate.acts_upstream_of_or_within_negative_effect
    }
}


def lookup_predicate(name: str = None) -> Tuple[str, Any]:
    """
    :param name: string name of predicate to be looked up
    :return: tuple(Predicate.name, mapping to relation) if available; defaults to "related_to" Predicate
    """
    if name and name in _predicate_by_name:
        entry = _predicate_by_name[name]
    else:
        entry = _predicate_by_name["related_to"]
    return entry["predicate"], entry["mapping"]


DEFAULT_RELATIONSHIP = lookup_predicate("related_to")


def infer_cellular_component_predicate(go_term: CellularComponent):
    """
    Infer the predicate for a specified Cellular Component GO term.
    Distinguishes between 'protein-containing' ('located_in)
    and 'non-protein containing' ('part_of') complex terms.
    See http://geneontology.org/docs/go-annotation-file-gaf-format-2.2/#qualifier-column-4

    :param go_term: CellularComponent
    :return: simple string predicate identifier
    """
    # TODO: Stub implementation - need to filter on (non-)protein status
    return Predicate.located_in
