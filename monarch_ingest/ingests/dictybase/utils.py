"""
A few Dictybase parse utility functions
"""
from typing import Optional, Dict, List
import logging

logger = logging.getLogger()


def parse_gene_id(row: Dict, gene_names_to_ids) -> Optional[str]:
    """
    Parses the 'Associated gene(s)' field of the data row
    to extract a dictybase gene ID associated with the row.

    :param row: dictionary with an 'Associated gene(s)' field
    :param gene_names_to_ids: 'Gene Name' to 'Gene ID' mappings dictionary
    :return: string corresponding to a Dictybase gene CURIE
    """
    gene_field: str = row["Associated gene(s)"]

    # sanity check: probably won't happen but empty gene field?
    if not gene_field:
        logger.warning(f"Input record has an empty 'Associated gene(s)' field?")
        return None

    # Split out multiple genes
    genes = gene_field.split('|')

    if len(genes) != 1:
        # the current Dictybase Ingest policy is
        # to only process entries with single genes
        logger.debug(f"Input record has multiple genes assigned for a given strain/phenotype... Ignoring?")
        return None

    # map gene symbols to proper ids
    gene_name = genes.pop().strip()

    # Otherwise, attempt to map the gene symbol given into a gene identifier
    try:
        gene_id = gene_names_to_ids[gene_name]['GENE ID']
    except KeyError:
        logger.warning(f"Gene Name '{gene_name}' mapping onto a Gene ID is unknown")
        return None

    return "dictyBase:" + gene_id


def parse_phenotypes(row: Dict, phenotype_names_to_ids: Dict) -> List[str]:
    """
    Parses the 'Phenotypes' field of the data row
    to extract a dictybase phenotypes associated
    with the given data row (Dictybase Strain).

    :param row: dictionary with an 'Phenotypes' field
    :param phenotype_names_to_ids: 'Phenotype Name' to 'Phenotype ID' mappings dictionary
    :return: List of UPHENO-compatible phenotypes.
    """
    phenotypes_field: str = row["Phenotypes"]

    # sanity check: probably won't happen but empty gene field?
    if not phenotypes_field:
        logger.warning(f"Input record has an empty 'Phenotypes' field?")
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
            logger.warning(f"Phenotype Name '{phenotype_name}' mapping onto a Phenotype ID is unknown")
            return []

    return phenotype_ids
