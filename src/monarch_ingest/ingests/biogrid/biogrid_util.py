"""
Some functions to assist parsing of BioGRID fields.
"""
from sys import stderr
from typing import List, Optional

from loguru import logger


def get_gene_id(raw_id: str) -> str:
    """
    Parse in the specified gene identifier.

    :param raw_id: str, raw BioGRID input string (a pseudo-CURIE)
    :return:
    """
    gid = raw_id.replace("entrez gene/locuslink", "NCBIGene")
    return gid


EVIDENCE_CODE_MAPPINGS = {
    # TODO: Need to somehow manually curate mappings of definitions at
    #          https://wiki.thebiogrid.org/doku.php/experimental_systems
    #       onto ECO codes
    #
    # Method: two hybrid
    # Method: affinity chromatography technology
    # Method: genetic interference
    # Method: pull down
    # Method: enzymatic study
    # Method: x-ray crystallography
    # Method: far western blotting
    # Method: fluorescent resonance energy transfer
    # Method: unspecified method
    # Method: imaging technique
    # Method: protein complementation assay
    # Method: biochemical
    # Method: bioid
}


def get_evidence(methods: str) -> Optional[List[str]]:
    """
    Parse in the specified interaction detection methods as a kind of evidence indication.

    :param methods: str, pipe ('|') delimited string of BioGRID interaction detection method encodings.
    :return: List[str], evidence codes
    """
    evidence_codes: List[str] = list()
    if methods:
        for method in methods.split("|"):
            # Sanity check...
            if not method:
                continue
            # databaseName:identifier(methodName)
            method = method.rstrip(")").split('(')[-1]
            if method not in EVIDENCE_CODE_MAPPINGS.keys():
                # logger.warning(
                #     f"Unknown evidence code for detection method '{method}'. Adding method as proxy."
                # )
                print(f"Method: {method}", file=stderr)
                EVIDENCE_CODE_MAPPINGS[method] = method
            evidence_codes.append(EVIDENCE_CODE_MAPPINGS[method])

    return evidence_codes if evidence_codes else None


def get_publication_ids(pub_ids: str) -> List[str]:
    """
    Parse the publication field.
    Simpleminded assumptions:
    - Just parse PMID's that have CURIEs of form 'pubmed:#######'
    - Not sure if this field is multivalued in practice (the column name implies that),
     but if so, one might expect it to be pipe ('|') delimited (if the "Alt IDs*" columns are an indication)

    :param pub_ids: str, raw input column from BioGRID
    :return: List[str], of PMIDs
    """
    publications: List[str] = [pmid.replace("pubmed", "PMID") for pmid in pub_ids.split("|")]
    return publications
