"""
A few Dictybase parse utility functions
"""
from typing import Optional, Tuple, Dict, List


from loguru import logger


def parse_gene_id(row: Dict, gene_names_to_ids: Dict) -> Optional[Tuple[str, str]]:
    """
    Parses the 'Associated gene(s)' field of the data row
    to extract a dictybase gene ID associated with the row.

    :param row: dictionary with an 'Associated gene(s)' field
    :param gene_names_to_ids: 'Gene Name' ('Symbol') to 'Gene ID' mappings dictionary
    :param dicty_symbols_to_ncbi_genes: 'Gene Name'  ('Symbol')  to 'NCBI Gene ID' mappings dictionary

    :return: string corresponding to a Dictybase gene CURIE
    """
    error_prefix = f"Input record:\n\t'{str(row)}':\n"
    gene_field: str = row["Associated gene(s)"]

    # sanity check: probably won't happen but empty gene field?
    if not gene_field:
        logger.debug(f"{error_prefix} has an empty 'Associated gene(s)' field?\n")
        return None

    # Split out multiple genes
    genes = gene_field.split('|')

    if len(genes) != 1:
        # TODO: review the current Dictybase Ingest policy, to only process entries with single genes
        logger.debug(f"{error_prefix} has multiple genes assigned for a given strain/phenotype... Ignoring?\n")
        return None

    # map gene symbols to proper ids
    gene_name = genes.pop().strip()

    try:
        # If an NCBI Gene Id is not available, attempt a more local Dictybase gene identifier
        gene_id = f"dictyBase:{gene_names_to_ids[gene_name]['GENE ID']}"
    except KeyError:
        logger.debug(f"{error_prefix} has a Gene Name '{gene_name}' with an unknown identifier mapping?\n")
        return None

    return gene_id, gene_name


def parse_phenotypes(row: Dict, phenotype_names_to_ids: Dict) -> List[str]:
    """
    Parses the 'Phenotypes' field of the data row
    to extract a dictybase phenotypes associated
    with the given data row (Dictybase Strain).

    :param row: dictionary with an 'Phenotypes' field
    :param phenotype_names_to_ids: 'Phenotype Name' to 'Phenotype ID' mappings dictionary
    :return: List of UPHENO-compatible phenotypes.
    """
    error_prefix = f"Input record:\n\t'{str(row)}':\n"
    phenotypes_field: str = row["Phenotypes"]

    # sanity check: probably won't happen but empty gene field?
    if not phenotypes_field:
        logger.debug(f"{error_prefix} has an empty 'Phenotypes' field?\n")
        return []

    # Split out multiple genes
    phenotypes: List[str] = phenotypes_field.split('|')

    # Clean up leading and trailing spaces
    phenotypes = [phenotype.strip() for phenotype in phenotypes]

    phenotype_ids: List[str] = list()
    for phenotype_name in phenotypes:
        try:
            phenotype_ids.append(phenotype_names_to_ids[phenotype_name]['id'])
        except KeyError:
            logger.debug(f"{error_prefix} Phenotype Name '{phenotype_name}' has unknown identifier mapping?\n")
            return []

    return phenotype_ids
