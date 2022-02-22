"""
Utility functions for Panther Orthology data processing
"""
from typing import Optional, Tuple, Dict
import logging


logger = logging.getLogger(__name__)

_ncbitaxon_catalog = {
    # TODO: may need to further build up this catalog
    #       of species - just starting with the STRING DB list
    "HUMAN": "9606",
    "MOUSE": "10090",
    "RAT": "10116",
    "DANRE": "7955",
    "DROME": "7227",
    "CAEEL": "6239",
    "SCHPO": "4896",
    "YEAST": "4932"
}


def ncbitaxon_by_name(species_name: str) -> Optional[str]:
    """
    Retrieves the NCBI Taxon ID of a given species, only if we are interested in it...
    :param species_name:
    """
    if species_name in _ncbitaxon_catalog:
        return f"NCBITaxon:{_ncbitaxon_catalog[species_name]}"
    else:
        logger.error(f"parse_gene_id(): Taxon '{species_name}' is not a unknown? Ignoring...")
        return None


_db_to_curie = {
    "FlyBase": "FB",
    "Ensembl": "ENSEMBL",
    
}


def get_biolink_curie_prefix(db_prefix: str) -> Optional[str]:
    """
    :param db_prefix: original database namespace identifier
    :return: Biolink Model compliant canonical CURIE namespace prefix
    """
    if db_prefix in _db_to_curie:
        return _db_to_curie[db_prefix]
    else:
        return db_prefix


def parse_gene_id(gene_id_spec: str) -> Optional[str]:
    """
    Parse out the Proting identifier
    :param gene_id_spec: is assumed to be of form 'UniProtKB=<object_id>'
    """
    if not gene_id_spec:
        logger.error(f"parse_gene_id(): Empty 'gene_id_spec'? Ignoring...")
        return None

    try:
        spec_part = gene_id_spec.split("=")
        
        if len(spec_part) == 2:
            # Map DB to Biolink Model canonical CURIE namespace
            prefix = get_biolink_curie_prefix(spec_part[0])
            return f"{prefix}:{spec_part[1]}"
        
        elif len(spec_part) == 3 and spec_part[1] == "MGI":
            # Odd special case of MGI
            # (is this the only one like this? Logger errors
            #  trapped by the RuntimeError below should answer this...)
            return f"{spec_part[1]}:{spec_part[2]}"
        
        else:
            raise RuntimeError
    
    except RuntimeError:
        logger.error(f"parse_gene_id(): Error parsing '{str(gene_id_spec)}'? Ignoring...")
        return None


def parse_gene(gene_entry: str) -> Optional[Tuple[str, str]]:
    """
    Captures a gene identifier from the Panther ref_genome record.

    :param gene_entry: string "species1|DB=id1|protdb=pdbid1" of descriptors describing the target gene
    """
    
    if not gene_entry:
        logger.error("parse_gene(): Empty 'gene_entry' argument?. Ignoring...")
        return None
    
    try:
        species, gene_spec, _ = gene_entry.split("|")
    except ValueError:
        logger.error(f"parse_gene(): Gene entry field '{str(gene_entry)}' has incorrect format. Ignoring...")
        return None
    
    # get the NCBI Taxonomic identifier
    ncbitaxon_id = ncbitaxon_by_name(species)
    
    # Quietly ignore a species we don't know about? Only complain in debug mode though (otherwise...)
    if not ncbitaxon_id:
        logger.debug(
            f"parse_gene(): Taxon '{str(species)}' in gene entry "
            f"'{str(gene_entry)}' is not in target list. Ignoring..."
        )
        return None

    # get the gene identifier
    gene_id = parse_gene_id(gene_spec)
    
    # Quietly ignore a gene identifier we can't parse out? Only complain in debug mode though (otherwise...)
    if not gene_id:
        logger.debug(
            f"parse_gene(): Gene identifier in gene entry '{str(gene_entry)}' cannot be parsed. Ignoring..."
        )
        return None
    
    return ncbitaxon_id, gene_id


# TODO: probably overkill... how do I discriminate between LDO and O?
# _predicate_by_orthology_type = {
#     "LDO": {  # least diverged ortholog
#         "predicate": Predicate.orthologous_to,
#         "mapping": "RO:HOM0000017"
#     },
#     "O": {
#         "predicate": Predicate.orthologous_to,
#         "mapping": "RO:HOM0000017"
#     },
#     # Starting PANTHER 15.0, paralogs (P), horizontal gene transfer (X) and
#     # least diverged horizontal gene transfer (LDX) are no longer included in the file.
#
#     # "P": {
#     #     "predicate": Predicate.paralogous_to,
#     #     "mapping": "RO:0001025"
#     # },
#     # "X": {
#     #     "predicate": Predicate.xenologous_to,
#     #     "mapping": "RO:0002326"
#     # },
#     # "LDX": {
#     #     "predicate": Predicate.acts_upstream_of,
#     #     "mapping": "RO:0002263"
#     # }
# }


# def lookup_predicate(orthology_type: str = None) -> Optional[Tuple[str, Any]]:
#     """
#     Maps an orthology_type onto an appropriate predicate and relation term.
#
#     :param orthology_type: string code of orthology_type to be mapped { LDO, O, P, X, LDX }
#     :return: tuple(Predicate.name, mapping to relation) if available; None otherwise
#     """
#     if orthology_type and orthology_type in _predicate_by_orthology_type:
#         entry = _predicate_by_orthology_type[orthology_type]
#     else:
#         logger.error(f"Encountered unknown type of orthology '{str(orthology_type)}'?")
#         return None
#
#     return entry["predicate"], entry["mapping"]
