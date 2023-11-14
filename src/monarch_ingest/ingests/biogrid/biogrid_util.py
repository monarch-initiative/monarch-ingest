"""
Some functions to assist parsing of BioGRID fields.
"""
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
    # "neighborhood": "ECO:0000044",
    # "fusion": "ECO:0000124",
    # "cooccurence": "ECO:0000080",
    # "coexpression": "ECO:0000075",
    # "experimental": "ECO:0000006",
    # "database": "ECO:0007636",
    # "textmining": "ECO:0007833"
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
            detection_method = method.rstrip(")").split('(')
            if detection_method not in EVIDENCE_CODE_MAPPINGS:
                logger.warning(
                    f"Unknown evidence code for detection method '{detection_method}'. Adding method as proxy."
                )
                EVIDENCE_CODE_MAPPINGS[detection_method] = detection_method
            evidence_codes.append(EVIDENCE_CODE_MAPPINGS[detection_method])
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
