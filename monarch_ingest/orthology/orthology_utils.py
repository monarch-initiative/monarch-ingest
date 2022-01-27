"""
Utility functions for Panther Orthology data processing
"""
from typing import Optional, Tuple, Any, Dict
import logging

from biolink_model_pydantic.model import Predicate

logger = logging.getLogger(__name__)
logger.setLevel("DEBUG")

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
        return None


def parse_protein_id(protein_id_spec: str) -> Optional[str]:
    """
    Parse out the Proting identifier
    :param protein_id_spec: is assumed to be of form 'UniProtKB=<object_id>'
    """
    if not protein_id_spec:
        return None
    
    try:
        spec_part = protein_id_spec.split("=")
        
        if len(spec_part) == 2 and spec_part[0] == "UniProtKB":
            # then just return the bare uniprot identifier
            return spec_part[1]
        else:
            # unexpected spec?
            return None
    
    except RuntimeError:
        logger.error(f"parse_protein_id(): Error parsing {str(protein_id_spec)}? Returning an empty string...")
        return None


def parse_gene(gene_entry: str, uniprot_2_gene: Dict) -> Optional[Tuple[str, str]]:
    """
    Maps a gene/ortholog column value of a
    Panther ortholog record, onto an Entrez identifier.

    :param gene_entry: string "species1|DB=id1|protdb=pdbid1" of descriptors describing the target gene
    :param uniprot_2_gene: koza_app managed identifier map
    """
    species, gene_spec, protein_spec = gene_entry.split("|")
    
    # get the NCBI Taxonomic identifier
    ncbitaxon_id = ncbitaxon_by_name(species)
    
    # Quietly ignore a species we don't know about?
    if not ncbitaxon_id:
        return None
    
    # get the protein id, to resolve it directly to an Entrez Gene Identifier
    uniprot_id = parse_protein_id(protein_spec)
    
    # Attempt to remap the UniProt ID onto its Entrez ID
    try:
        entrez_id = f"NCBIGene:{uniprot_2_gene[uniprot_id]['Entrez']}"
        return ncbitaxon_id, entrez_id
    
    except KeyError:
        logger.warning(
            f"Could not map Uniprot identifier '{str(uniprot_id)}' onto an Entrez Gene Id. Ignoring?"
        )
        return None


# TODO: probably overkill... how do I discriminate between LDO and O?
_predicate_by_orthology_type = {
    "LDO": {  # least diverged ortholog
        "predicate": Predicate.orthologous_to,
        "mapping": "RO:HOM0000017"
    },
    "O": {
        "predicate": Predicate.orthologous_to,
        "mapping": "RO:HOM0000017"
    },
    # Starting PANTHER 15.0, paralogs (P), horizontal gene transfer (X) and
    # least diverged horizontal gene transfer (LDX) are no longer included in the file.
    
    # "P": {
    #     "predicate": Predicate.paralogous_to,
    #     "mapping": "RO:0001025"
    # },
    # "X": {
    #     "predicate": Predicate.xenologous_to,
    #     "mapping": "RO:0002326"
    # },
    # "LDX": {
    #     "predicate": Predicate.acts_upstream_of,
    #     "mapping": "RO:0002263"
    # }
}


def lookup_predicate(orthology_type: str = None) -> Optional[Tuple[str, Any]]:
    """
    Maps an orthology_type onto an appropriate predicate and relation term.
    
    :param orthology_type: string code of orthology_type to be mapped { LDO, O, P, X, LDX }
    :return: tuple(Predicate.name, mapping to relation) if available; None otherwise
    """
    if orthology_type and orthology_type in _predicate_by_orthology_type:
        entry = _predicate_by_orthology_type[orthology_type]
    else:
        logger.error(f"Encountered unknown type of orthology '{str(orthology_type)}'?")
        return None
    
    return entry["predicate"], entry["mapping"]
