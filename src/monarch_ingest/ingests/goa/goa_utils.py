"""
Some Gene Ontology Annotation ingest utility functions.
"""
from re import sub, IGNORECASE, compile, Pattern
from typing import Any, Optional, Tuple, List, Dict

from loguru import logger

from biolink.pydanticmodel import (
    BiologicalProcess,
    CellularComponent,
    MacromolecularMachineToBiologicalProcessAssociation,
    MacromolecularMachineToCellularComponentAssociation,
    MacromolecularMachineToMolecularActivityAssociation,
    MolecularActivity,
)



def parse_ncbi_taxa(taxon: str) -> List[str]:
    ncbi_taxa: List[str] = list()
    if taxon:
        # in rare circumstances, multiple taxa may be given as a piped list...
        taxa = taxon.split("|")
        for taxon in taxa:
            ncbi_taxa.append(sub(r"^taxon", "NCBITaxon", taxon, flags=IGNORECASE))
        return ncbi_taxa
    else:
        return []


_gene_identifier_map: Dict[str, Tuple[str, Pattern]] = {
    # Genome sequenced model for
    # Aspergillus nidulans FGSC A4  a.k.a. Emericella nidulans
    # The proper CURIE prefix for this is not certain
    "NCBITaxon:227321": ('AspGD', compile(r"(?P<identifier>AN\d+)\|"))
}


def parse_identifiers(row: Dict):
    """
    This method uses specific fields of the GOA data entry
    to resolve both the gene identifier and the NCBI Taxon
    """
    db: str = row['DB']
    db_object_id: str = row['DB_Object_ID']

    # This check is to clean up id's like MGI:MGI:123
    if ":" in db_object_id:
        db_object_id = db_object_id.split(':')[-1]

    ncbitaxa: List[str] = parse_ncbi_taxa(row['Taxon'])
    if not ncbitaxa:
        # Unlikely to happen, but...
        logger.warning(f"Missing taxa for '{db}:{db_object_id}'?")

    # Hacky remapping of some gene identifiers
    if ncbitaxa[0] in _gene_identifier_map.keys():
        id_regex: Pattern = _gene_identifier_map[ncbitaxa[0]][1]
        aliases: str = row['DB_Object_Synonym']
        match = id_regex.match(aliases)
        if match is not None:
            # Overwrite the 'db' and 'db_object_id' accordingly
            db = _gene_identifier_map[ncbitaxa[0]][0]
            db_object_id = match.group('identifier')

    gene_id: str = f"{db}:{db_object_id}"

    return gene_id, ncbitaxa


# TODO: replace this workaround dictionary with direct usage of the
#       Pydantic Predicate functionality and the translator_table.yaml
#       Or an external local table file?
_predicate_by_name = {
    "enables": {"predicate": "biolink:enables", "mapping": "RO:0002327"},
    "involved_in": {"predicate": "biolink:actively_involved_in", "mapping": "RO:0002331"},
    "located_in": {"predicate": "biolink:located_in", "mapping": "RO:0001025"},
    "contributes_to": {"predicate": "biolink:contributes_to", "mapping": "RO:0002326"},
    "acts_upstream_of": {
        "predicate": "biolink:acts_upstream_of",
        "mapping": "RO:0002263",
    },
    "part_of": {"predicate": "biolink:part_of", "mapping": "BFO:0000050"},
    "acts_upstream_of_positive_effect": {
        "predicate": "biolink:acts_upstream_of_positive_effect",
        "mapping": "RO:0004034",
    },
    "is_active_in": {"predicate": "biolink:active_in", "mapping": "RO:0002432"},
    "acts_upstream_of_negative_effect": {
        "predicate": "biolink:acts_upstream_of_negative_effect",
        "mapping": "RO:0004035",
    },
    "colocalizes_with": {
        "predicate": "biolink:colocalizes_with",
        "mapping": "RO:0002325",
    },
    "acts_upstream_of_or_within": {
        "predicate": "biolink:acts_upstream_of_or_within",
        "mapping": "RO:0002264",
    },
    "acts_upstream_of_or_within_positive_effect": {
        "predicate": "biolink:acts_upstream_of_or_within_positive_effect",
        "mapping": "RO:0004032",
    },
    "acts_upstream_of_or_within_negative_effect": {
        "predicate": "biolink:acts_upstream_of_or_within_negative_effect",
        "mapping": "RO:0004033",
    },
}


def lookup_predicate(name: str = None) -> Optional[Tuple[str, Any]]:
    """
    :param name: string name of predicate to be looked up
    :return: tuple(biolink:predicate, mapping to relation) if available; None otherwise
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
    "C": (CellularComponent, MacromolecularMachineToCellularComponentAssociation),
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
